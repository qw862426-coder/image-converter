/* Background-removal worker: downloads the model once, runs it off the main thread, cleans up the mask. */
importScripts('/vendor/ort/ort-wasm.js', '/vendor/ort/mini-ort.js');

var MODELS = {
  hq: { parts: ['/models/silueta.onnx.part0', '/models/silueta.onnx.part1', '/models/silueta.onnx.part2'], size: 44173029 },
  fast: { parts: ['/models/u2netp.onnx'], size: 4574861 }
};
var ortPromise = null, sessions = {}, S = 320;

function simd() {
  try { return WebAssembly.validate(new Uint8Array([0, 97, 115, 109, 1, 0, 0, 0, 1, 5, 1, 96, 0, 1, 123, 3, 2, 1, 0, 10, 10, 1, 8, 0, 65, 0, 253, 15, 253, 98, 11])); } catch (e) { return false; }
}
function getOrt() {
  if (!ortPromise) ortPromise = MiniOrt.fromFactory(self.ortWasm, '/vendor/ort/' + (simd() ? 'ort-wasm-simd.wasm' : 'ort-wasm.wasm'));
  return ortPromise;
}

/* Fetch with progress, keeping a copy in the Cache API so later visits skip the download. */
async function fetchPart(url, onBytes) {
  var cache = null;
  try { cache = await caches.open('picshifter-models-v1'); var hit = await cache.match(url); if (hit) { var b = new Uint8Array(await hit.arrayBuffer()); onBytes(b.length); return b; } } catch (e) { cache = null; }
  var res = await fetch(url);
  if (!res.ok) throw new Error('eModel');
  var chunks = [], got = 0;
  if (res.body && res.body.getReader) {
    var reader = res.body.getReader();
    for (;;) { var r = await reader.read(); if (r.done) break; chunks.push(r.value); got += r.value.length; onBytes(r.value.length); }
  } else { var all = new Uint8Array(await res.arrayBuffer()); chunks.push(all); got = all.length; onBytes(got); }
  var out = new Uint8Array(got), o = 0; chunks.forEach(function (c) { out.set(c, o); o += c.length; });
  try { if (cache) await cache.put(url, new Response(out)); } catch (e) {}
  return out;
}

async function getSession(key) {
  if (sessions[key]) return sessions[key];
  sessions[key] = (async function () {
    var m = MODELS[key], loaded = 0, last = 0;
    var parts = [];
    for (var i = 0; i < m.parts.length; i++) {
      parts.push(await fetchPart(m.parts[i], function (n) {
        loaded += n; var p = Math.min(1, loaded / m.size);
        if (p - last > 0.01 || p === 1) { last = p; postMessage({ type: 'progress', stage: 'download', value: p }); }
      }));
    }
    var total = parts.reduce(function (a, b) { return a + b.length; }, 0), model = new Uint8Array(total), o = 0;
    parts.forEach(function (p) { model.set(p, o); o += p.length; });
    postMessage({ type: 'progress', stage: 'prepare', value: 1 });
    var ort = await getOrt();
    return ort.createSession(model);
  })();
  try { return await sessions[key]; } catch (e) { delete sessions[key]; throw e; }
}

/* Keep the main subject: drop small separate blobs (stray shadows, background bits) and sharpen the edge. */
function cleanMask(o) {
  var n = S * S, lo = Infinity, hi = -Infinity, i;
  for (i = 0; i < n; i++) { if (o[i] < lo) lo = o[i]; if (o[i] > hi) hi = o[i]; }
  var m = new Float32Array(n), span = hi - lo || 1;
  for (i = 0; i < n; i++) m[i] = (o[i] - lo) / span;
  var lab = new Int32Array(n).fill(-1), sizes = [], stack = [];
  for (i = 0; i < n; i++) {
    if (m[i] < 0.5 || lab[i] >= 0) continue;
    var id = sizes.length, size = 0; lab[i] = id; stack.push(i);
    while (stack.length) {
      var p = stack.pop(), x = p % S, y = (p - x) / S; size++;
      if (x > 0 && m[p - 1] >= 0.5 && lab[p - 1] < 0) { lab[p - 1] = id; stack.push(p - 1); }
      if (x < S - 1 && m[p + 1] >= 0.5 && lab[p + 1] < 0) { lab[p + 1] = id; stack.push(p + 1); }
      if (y > 0 && m[p - S] >= 0.5 && lab[p - S] < 0) { lab[p - S] = id; stack.push(p - S); }
      if (y < S - 1 && m[p + S] >= 0.5 && lab[p + S] < 0) { lab[p + S] = id; stack.push(p + S); }
    }
    sizes.push(size);
  }
  if (sizes.length > 1) {
    var big = Math.max.apply(null, sizes), keep = new Uint8Array(n);
    for (i = 0; i < n; i++) if (lab[i] >= 0 && sizes[lab[i]] >= big * 0.12) keep[i] = 1;
    /* grow the kept area a little so soft edges around the subject survive */
    var r = 6, grown = new Uint8Array(n);
    for (var y2 = 0; y2 < S; y2++) for (var x2 = 0; x2 < S; x2++) {
      if (!keep[y2 * S + x2]) continue;
      for (var dy = -r; dy <= r; dy++) { var yy = y2 + dy; if (yy < 0 || yy >= S) continue;
        for (var dx = -r; dx <= r; dx++) { var xx = x2 + dx; if (xx >= 0 && xx < S) grown[yy * S + xx] = 1; } }
    }
    for (i = 0; i < n; i++) if (!grown[i]) m[i] = 0;
  }
  for (i = 0; i < n; i++) { var v = (m[i] - 0.08) / 0.84; m[i] = v < 0 ? 0 : v > 1 ? 1 : v; }
  return m;
}

onmessage = async function (e) {
  var msg = e.data;
  try {
    if (msg.type === 'load') { await getSession(msg.model); postMessage({ type: 'ready', model: msg.model }); return; }
    if (msg.type === 'run') {
      var s = await getSession(msg.model);
      postMessage({ type: 'progress', stage: 'run', value: 0, id: msg.id });
      var out = s.run({ [s.inputNames[0]]: { data: msg.input, dims: [1, 3, S, S] } });
      var mask = cleanMask(out[s.outputNames[0]].data);
      postMessage({ type: 'mask', id: msg.id, mask: mask }, [mask.buffer]);
    }
  } catch (err) {
    postMessage({ type: 'error', id: msg.id, message: (err && err.message) || 'eGeneric' });
  }
};
