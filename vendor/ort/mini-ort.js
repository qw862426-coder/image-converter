/* Minimal wrapper around the onnxruntime WebAssembly build (MIT, Microsoft) used by PicShifter.
   It only supports what background removal needs: load one model, run it with float32 inputs.
   API (browser): MiniOrt.load(baseUrl) -> Promise<ort>;  ort.createSession(Uint8Array) -> session;
                  session.run({name: {data: Float32Array, dims: [...]}}) -> {name: {data, dims}} */
(function (root) {
'use strict';

function wasmSimdSupported() {
  try {
    return WebAssembly.validate(new Uint8Array([0, 97, 115, 109, 1, 0, 0, 0, 1, 5, 1, 96, 0, 1, 123, 3, 2, 1, 0, 10, 10, 1, 8, 0, 65, 0, 253, 15, 253, 98, 11]));
  } catch (e) { return false; }
}

function wrap(wasm) {
  if (wasm._OrtInit(1, 3) !== 0) throw new Error('ORT init failed');

  function cstr(s, allocs) {
    var bytes = new TextEncoder().encode(s + '\0'), p = wasm._malloc(bytes.length);
    wasm.HEAPU8.set(bytes, p); allocs.push(p); return p;
  }

  function createSession(model) {
    var allocs = [], opt = 0, modelPtr = wasm._malloc(model.byteLength), handle = 0;
    try {
      /* graph optimisation: all (99), cpu arena on, mem pattern on, sequential, no profiling, log level error */
      opt = wasm._OrtCreateSessionOptions(99, 1, 1, 0, 0, 0, 0, 3, 0);
      if (!opt) throw new Error('ORT session options failed');
      wasm.HEAPU8.set(model, modelPtr);
      handle = wasm._OrtCreateSession(modelPtr, model.byteLength, opt);
      if (!handle) throw new Error('ORT could not load the model');
    } finally {
      wasm._free(modelPtr); if (opt) wasm._OrtReleaseSessionOptions(opt); allocs.forEach(wasm._free);
    }
    var inputs = [], outputs = [];
    for (var i = 0; i < wasm._OrtGetInputCount(handle); i++) { var p = wasm._OrtGetInputName(handle, i); inputs.push({ ptr: p, name: wasm.UTF8ToString(p) }); }
    for (var j = 0; j < wasm._OrtGetOutputCount(handle); j++) { var q = wasm._OrtGetOutputName(handle, j); outputs.push({ ptr: q, name: wasm.UTF8ToString(q) }); }

    return {
      inputNames: inputs.map(function (x) { return x.name; }),
      outputNames: outputs.map(function (x) { return x.name; }),
      run: function (feeds) {
        var tensors = [], allocs2 = [], result = {};
        try {
          inputs.forEach(function (inp) {
            var f = feeds[inp.name]; if (!f) throw new Error('missing input ' + inp.name);
            var bytes = f.data.byteLength, dp = wasm._malloc(bytes); allocs2.push(dp);
            wasm.HEAPU8.set(new Uint8Array(f.data.buffer, f.data.byteOffset, bytes), dp);
            var dimsPtr = wasm._malloc(4 * f.dims.length); allocs2.push(dimsPtr);
            for (var k = 0; k < f.dims.length; k++) wasm.HEAP32[dimsPtr / 4 + k] = f.dims[k];
            var t = wasm._OrtCreateTensor(1 /* float */, dp, bytes, dimsPtr, f.dims.length);
            if (!t) throw new Error('ORT could not create a tensor');
            tensors.push(t);
          });
          var n = inputs.length, m = outputs.length, block = wasm._malloc(4 * (2 * n + 2 * m)); allocs2.push(block);
          var inVals = block, inNames = block + 4 * n, outVals = block + 8 * n, outNames = outVals + 4 * m;
          for (var a = 0; a < n; a++) { wasm.HEAPU32[inVals / 4 + a] = tensors[a]; wasm.HEAPU32[inNames / 4 + a] = inputs[a].ptr; }
          for (var b = 0; b < m; b++) { wasm.HEAPU32[outVals / 4 + b] = 0; wasm.HEAPU32[outNames / 4 + b] = outputs[b].ptr; }
          var err = wasm._OrtRun(handle, inNames, inVals, n, outNames, m, outVals, 0);
          if (err !== 0) throw new Error('ORT run failed (' + err + ')');
          var info = wasm._malloc(16); allocs2.push(info);
          for (var c = 0; c < m; c++) {
            var ot = wasm.HEAPU32[outVals / 4 + c];
            try {
              if (wasm._OrtGetTensorData(ot, info, info + 4, info + 8, info + 12) !== 0) throw new Error('ORT output read failed');
              var dataPtr = wasm.HEAPU32[info / 4 + 1], dimsP = wasm.HEAPU32[info / 4 + 2], dimsN = wasm.HEAPU32[info / 4 + 3], dims = [];
              for (var d = 0; d < dimsN; d++) dims.push(wasm.HEAPU32[dimsP / 4 + d]);
              wasm._OrtFree(dimsP);
              var size = dims.reduce(function (x, y) { return x * y; }, 1), out = new Float32Array(size);
              new Uint8Array(out.buffer).set(wasm.HEAPU8.subarray(dataPtr, dataPtr + size * 4));
              result[outputs[c].name] = { data: out, dims: dims };
            } finally { wasm._OrtReleaseTensor(ot); }
          }
        } finally {
          tensors.forEach(function (t) { wasm._OrtReleaseTensor(t); });
          allocs2.forEach(function (p) { wasm._free(p); });
        }
        return result;
      },
      release: function () {
        inputs.concat(outputs).forEach(function (x) { wasm._OrtFree(x.ptr); });
        wasm._OrtReleaseSession(handle);
      }
    };
  }
  return { createSession: createSession };
}

/* factory: the emscripten loader function (ortWasm); wasmFile: URL or path of the .wasm */
async function fromFactory(factory, wasmFile) {
  var m = factory({ locateFile: function () { return wasmFile; }, numThreads: 1 });
  var wasm = m && m.ready ? await m.ready : await m;
  return wrap(wasm);
}

function load(base) {
  base = base.replace(/\/?$/, '/');
  return new Promise(function (resolve, reject) {
    function go() { fromFactory(root.ortWasm, base + (wasmSimdSupported() ? 'ort-wasm-simd.wasm' : 'ort-wasm.wasm')).then(resolve, reject); }
    if (root.ortWasm) return go();
    var s = document.createElement('script'); s.src = base + 'ort-wasm.js';
    s.onload = go; s.onerror = function () { reject(new Error('eLib')); };
    document.head.appendChild(s);
  });
}

var MiniOrt = { load: load, fromFactory: fromFactory, wrap: wrap };
if (typeof module !== 'undefined' && module.exports) module.exports = MiniOrt; else root.MiniOrt = MiniOrt;
})(typeof window !== 'undefined' ? window : globalThis);
