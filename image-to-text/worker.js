/* Text recognition worker: loads PicShifter's own OCR models and reads text from images.
   Model sets: Korean + Latin letters (default), Japanese ('ja'), Chinese ('zh') and Russian ('ru'). Only the chosen one is downloaded. */
importScripts('/image-to-text/engine.js');
var cache = {}, current = null;
function get(url, type, optional) {
  return fetch(url).then(function (r) {
    if (!r.ok) { if (optional) return null; throw new Error('eModel'); }
    return type === 'json' ? r.json() : r.arrayBuffer();
  }).catch(function (e) { if (optional) return null; throw e; });
}
function files(lang) {
  if (!cache[lang]) {
    var sfx = lang ? '-' + lang : '', b = '/image-to-text/';
    cache[lang] = get(b + 'ocr-meta' + sfx + '.json', 'json').then(function (meta) {
      var plain = meta.extras === false; /* Russian: shape matching only, no network or character counts */
      return Promise.all([
        get(b + 'ocr-model' + sfx + '.bin', 'bin'),
        meta,
        /* neural network + character counts: optional extras; reading still works without them */
        plain ? null : get(b + 'ocr-net' + sfx + '.bin', 'bin', true),
        plain ? null : get(b + 'ocr-net' + sfx + '.json', 'json', true),
        plain ? null : get(b + 'ocr-lm' + sfx + '.json', 'json', true)
      ]);
    });
    cache[lang].catch(function () { delete cache[lang]; });
  }
  return cache[lang];
}
function use(lang) {
  return files(lang).then(function (a) {
    if (current === lang) return;
    /* load() copies what it needs, so the cached buffers stay usable for switching back */
    PicOCR.load(a[0], a[1]);
    PicOCR.loadNet(a[2] && a[3] ? a[2] : null, a[3]);
    PicOCR.loadLM(a[4]);
    current = lang;
  });
}
onmessage = async function (e) {
  var m = e.data, lang = (m.lang === 'ja' || m.lang === 'zh' || m.lang === 'ru') ? m.lang : '';
  try {
    await use(lang);
    postMessage({ type: 'progress', value: 0 });
    var text = PicOCR.recognize(m.rgba, m.w, m.h, function (p) { postMessage({ type: 'progress', value: p }); });
    postMessage({ type: 'done', text: text });
  } catch (err) { postMessage({ type: 'error', message: (err && err.message === 'eModel') ? 'eModel' : 'eGeneric' }); }
};
