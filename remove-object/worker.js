/* Object-removal worker: downloads the chosen model once (kept in the Cache API), then fills painted areas.
   'lama'  = Big LaMa, high quality (about 71 MB, slower)   'migan' = MI-GAN, fast (about 27 MB) */
importScripts('/vendor/ort/ort-wasm.js', '/vendor/ort/mini-ort.js', '/remove-object/patchfill.js');

var MDIR = ['', 'models', ''].join('/'); /* built in pieces: not a page for search robots */
var MODELS = {
  migan: { parts: [MDIR + 'migan.onnx.part0', MDIR + 'migan.onnx.part1'], size: 26762424 },
  lama: { parts: [MDIR + 'lama.onnx.part0', MDIR + 'lama.onnx.part1', MDIR + 'lama.onnx.part2'], size: 71196116 }
};
var ortPromise = null, sessions = {}, N = 512;

function simd() {
  try { return WebAssembly.validate(new Uint8Array([0, 97, 115, 109, 1, 0, 0, 0, 1, 5, 1, 96, 0, 1, 123, 3, 2, 1, 0, 10, 10, 1, 8, 0, 65, 0, 253, 15, 253, 98, 11])); } catch (e) { return false; }
}
function getOrt() {
  if (!ortPromise) ortPromise = MiniOrt.fromFactory(self.ortWasm, '/vendor/ort/' + (simd() ? 'ort-wasm-simd.wasm' : 'ort-wasm.wasm'));
  return ortPromise;
}
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
function getSession(which) {
  var MODEL = MODELS[which];
  if (sessions[which]) return sessions[which];
  var session = sessions[which] = (async function () {
    var loaded = 0, last = 0, parts = [];
    for (var i = 0; i < MODEL.parts.length; i++) {
      parts.push(await fetchPart(MODEL.parts[i], function (n) {
        loaded += n; var p = Math.min(1, loaded / MODEL.size);
        if (p - last > 0.01 || p === 1) { last = p; postMessage({ type: 'progress', stage: 'download', value: p }); }
      }));
    }
    var total = parts.reduce(function (a, b) { return a + b.length; }, 0), model = new Uint8Array(total), o = 0;
    parts.forEach(function (p) { model.set(p, o); o += p.length; });
    postMessage({ type: 'progress', stage: 'prepare', value: 1 });
    var ort = await getOrt();
    return ort.createSession(model);
  })();
  session.catch(function () { delete sessions[which]; });
  return session;
}

/* rgba: 512*512*4 bytes of the area to fix; hole: 512*512 bytes, 1 = paint over. Returns rgba of the filled area. */
onmessage = async function (e) {
  var msg = e.data;
  if (msg.type === 'refine') {
    try {
      var last = 0;
      var res = PatchFill.fill(msg.img, msg.w, msg.h, msg.hole, msg.init, { onProgress: function (p) { if (p - last > 0.05 || p === 1) { last = p; postMessage({ type: 'progress', stage: 'refine', value: p }); } } });
      if (res) postMessage({ type: 'done', rgb: res }, [res.buffer]); else postMessage({ type: 'done', rgb: null });
    } catch (err) { postMessage({ type: 'error', message: 'eGeneric' }); }
    return;
  }
  try {
    var which = msg.model === 'migan' ? 'migan' : 'lama';
    var s = await getSession(which);
    postMessage({ type: 'progress', stage: 'run', value: 0 });
    var n = N * N, px = msg.rgba, hole = msg.hole, res = new Uint8ClampedArray(n * 4);
    if (which === 'lama') {
      var img = new Float32Array(3 * n), mk = new Float32Array(n);
      for (var p = 0; p < n; p++) { img[p] = px[p * 4] / 255; img[n + p] = px[p * 4 + 1] / 255; img[2 * n + p] = px[p * 4 + 2] / 255; mk[p] = hole[p] ? 1 : 0; }
      var lo = s.run({ img: { data: img, dims: [1, 3, N, N] }, mask: { data: mk, dims: [1, 1, N, N] } })[s.outputNames[0]].data;
      for (var q = 0; q < n; q++) { res[q * 4] = lo[q] * 255; res[q * 4 + 1] = lo[n + q] * 255; res[q * 4 + 2] = lo[2 * n + q] * 255; res[q * 4 + 3] = 255; }
      postMessage({ type: 'done', rgba: res }, [res.buffer]);
      return;
    }
    var inp = new Float32Array(4 * n);
    for (var i = 0; i < n; i++) {
      var m = hole[i] ? 1 : 0, k = 1 - m;
      inp[i] = 0.5 - m;
      inp[n + i] = (px[i * 4] / 127.5 - 1) * k;
      inp[2 * n + i] = (px[i * 4 + 1] / 127.5 - 1) * k;
      inp[3 * n + i] = (px[i * 4 + 2] / 127.5 - 1) * k;
    }
    var out = s.run({ [s.inputNames[0]]: { data: inp, dims: [1, 4, N, N] } })[s.outputNames[0]].data;
    for (var j = 0; j < n; j++) {
      res[j * 4] = (out[j] * 0.5 + 0.5) * 255; res[j * 4 + 1] = (out[n + j] * 0.5 + 0.5) * 255; res[j * 4 + 2] = (out[2 * n + j] * 0.5 + 0.5) * 255; res[j * 4 + 3] = 255;
    }
    postMessage({ type: 'done', rgba: res }, [res.buffer]);
  } catch (err) {
    postMessage({ type: 'error', message: (err && err.message) || 'eGeneric' });
  }
};
