/* Text recognition worker: loads PicShifter's own OCR model once and reads text from images. */
importScripts('/image-to-text/engine.js');
var ready = null;
function init() {
  if (!ready) ready = Promise.all([
    fetch('/image-to-text/ocr-model.bin').then(function (r) { if (!r.ok) throw new Error('eModel'); return r.arrayBuffer(); }),
    fetch('/image-to-text/ocr-meta.json').then(function (r) { if (!r.ok) throw new Error('eModel'); return r.json(); })
  ]).then(function (a) { PicOCR.load(a[0], a[1]); });
  ready.catch(function () { ready = null; });
  return ready;
}
onmessage = async function (e) {
  var m = e.data;
  try {
    await init();
    postMessage({ type: 'progress', value: 0 });
    var text = PicOCR.recognize(m.rgba, m.w, m.h, function (p) { postMessage({ type: 'progress', value: p }); });
    postMessage({ type: 'done', text: text });
  } catch (err) { postMessage({ type: 'error', message: (err && err.message === 'eModel') ? 'eModel' : 'eGeneric' }); }
};
