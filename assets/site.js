/* PicShifter shared site chrome: top bar (brand, menu, language), footer links, language state.
   Pages call Site.onChange(fn) to re-translate their own text when the language changes. */
(function () {
  'use strict';
  var LANGS = { en: 'English', ko: '한국어', ja: '日本語', zh: '中文（简体）', es: 'Español', pt: 'Português', fr: 'Français', de: 'Deutsch' };
  var KEY = 'imgconv-lang';
  var T = {
    en: { compress: 'Compress images', popular: 'Popular', bg: 'Remove background', scan: 'Photo to scan', img: 'Image converter', doc: 'Documents to PDF', guide: 'How to use', about: 'About', privacy: 'Privacy policy', contact: 'Contact', lang: 'Language', menu: 'Menu', note: 'Files are converted on your device and never uploaded.' },
    ko: { compress: '사진 용량 줄이기', popular: '인기 변환', bg: '배경 지우기', scan: '사진 → 스캔본', img: '이미지 변환', doc: '문서 → PDF', guide: '사용 방법', about: '사이트 소개', privacy: '개인정보처리방침', contact: '문의하기', lang: '언어', menu: '메뉴', note: '파일은 내 기기에서 변환되며 어디에도 업로드되지 않습니다.' },
    ja: { compress: '画像を圧縮', popular: '人気の変換', bg: '背景を削除', scan: '写真をスキャンに', img: '画像変換', doc: '文書をPDFに', guide: '使い方', about: 'このサイトについて', privacy: 'プライバシーポリシー', contact: 'お問い合わせ', lang: '言語', menu: 'メニュー', note: 'ファイルは端末内で変換され、アップロードされることはありません。' },
    zh: { compress: '压缩图片', popular: '常用转换', bg: '去除背景', scan: '照片转扫描件', img: '图片转换', doc: '文档转 PDF', guide: '使用方法', about: '关于本站', privacy: '隐私政策', contact: '联系我们', lang: '语言', menu: '菜单', note: '文件在你的设备上转换，不会上传到任何地方。' },
    es: { compress: 'Comprimir imágenes', popular: 'Populares', bg: 'Quitar fondo', scan: 'Foto a escaneo', img: 'Convertir imágenes', doc: 'Documentos a PDF', guide: 'Cómo usarlo', about: 'Acerca de', privacy: 'Privacidad', contact: 'Contacto', lang: 'Idioma', menu: 'Menú', note: 'Los archivos se convierten en tu dispositivo y nunca se suben.' },
    pt: { compress: 'Comprimir imagens', popular: 'Populares', bg: 'Remover fundo', scan: 'Foto para digitalização', img: 'Converter imagens', doc: 'Documentos para PDF', guide: 'Como usar', about: 'Sobre', privacy: 'Privacidade', contact: 'Contato', lang: 'Idioma', menu: 'Menu', note: 'Os arquivos são convertidos no seu dispositivo e nunca são enviados.' },
    fr: { compress: 'Compresser des images', popular: 'Populaires', bg: 'Supprimer le fond', scan: 'Photo en scan', img: 'Convertir des images', doc: 'Documents en PDF', guide: 'Mode d’emploi', about: 'À propos', privacy: 'Confidentialité', contact: 'Contact', lang: 'Langue', menu: 'Menu', note: 'Les fichiers sont convertis sur votre appareil et ne sont jamais envoyés.' },
    de: { compress: 'Bilder komprimieren', popular: 'Beliebt', bg: 'Hintergrund entfernen', scan: 'Foto zu Scan', img: 'Bilder umwandeln', doc: 'Dokumente zu PDF', guide: 'Anleitung', about: 'Über uns', privacy: 'Datenschutz', contact: 'Kontakt', lang: 'Sprache', menu: 'Menü', note: 'Dateien werden auf deinem Gerät umgewandelt und nie hochgeladen.' }
  };
  var LINKS = [['img', '/'], ['doc', '/document-to-pdf/'], ['scan', '/scan/'], ['bg', '/remove-background/'], ['guide', '/guide/']];
  var FOOT = [['about', '/about/'], ['privacy', '/privacy/'], ['contact', '/contact/']];
  var POPULAR = [['HEIC → JPG', '/heic-to-jpg/'], ['PNG → JPG', '/png-to-jpg/'], ['JPG → PNG', '/jpg-to-png/'], ['WebP → JPG', '/webp-to-jpg/'],
    ['JPG → PDF', '/jpg-to-pdf/'], ['PDF → JPG', '/pdf-to-jpg/'], ['PNG → ICO', '/png-to-ico/'], ['Word → PDF', '/word-to-pdf/'],
    ['Excel → PDF', '/excel-to-pdf/'], ['PPT → PDF', '/ppt-to-pdf/'], ['HWP → PDF', '/hwp-to-pdf/'], ['@compress', '/compress-image/']];

  /* Every page has a fixed language from its address: /heic-to-jpg/ is English, /ko/heic-to-jpg/ is Korean. */
  function stored() { try { var s = localStorage.getItem(KEY); return s && LANGS[s] ? s : null; } catch (e) { return null; } }
  function browserLang() {
    var list = navigator.languages || [navigator.language || 'en'];
    for (var i = 0; i < list.length; i++) { var k = String(list[i]).toLowerCase().split('-')[0]; if (LANGS[k]) return k; }
    return 'en';
  }
  var PREFIX = new RegExp('^/(' + Object.keys(LANGS).filter(function (k) { return k !== 'en'; }).join('|') + ')(?=/)');
  var bare = location.pathname.replace(/index\.html$/, '').replace(PREFIX, '') || '/';
  var lang = window.PAGE_LANG && LANGS[window.PAGE_LANG] ? window.PAGE_LANG : (stored() || browserLang());
  function pathFor(l, p) { return (l === 'en' ? '' : '/' + l) + p; }
  /* First visit to an English address from a phone set to another supported language: open that language's page. */
  if (window.PAGE_LANG === 'en') {
    var want = stored() || browserLang();
    if (want !== 'en' && location.protocol !== 'file:') { window.Site = { LANGS: LANGS, lang: want, onChange: function () {} }; location.replace(pathFor(want, bare) + location.search + location.hash); return; }
  }
  var subs = [];
  function t(k) { return (T[lang] && T[lang][k]) || T.en[k] || k; }
  function here(href) { return bare === href; }

  var css = document.createElement('style');
  css.textContent =
    '.sitebar{position:sticky;top:env(safe-area-inset-top,0px);z-index:20;background:var(--panel);border-bottom:1px solid var(--line)}' +
    '.sitebar-in{max-width:960px;margin:0 auto;padding-inline:16px;padding-block:10px;display:flex;align-items:center;gap:12px;flex-wrap:wrap}' +
    '.brand{font-weight:700;font-size:1.05rem;color:var(--fg);text-decoration:none;letter-spacing:-.01em;display:flex;align-items:center;gap:8px}' +
    '.brand i{width:22px;height:22px;border-radius:6px;background:var(--accent);display:inline-block;position:relative}' +
    '.brand i::after{content:"";position:absolute;inset:6px;border:2px solid var(--accent-fg);border-radius:2px;transform:rotate(12deg)}' +
    '.sitenav{display:flex;gap:4px;flex-wrap:wrap;flex:1;min-width:0}' +
    '.sitenav a{color:var(--muted);text-decoration:none;font-size:.9rem;padding:6px 10px;border-radius:8px}' +
    '.sitenav a:hover{color:var(--fg);background:var(--bg)}' +
    '.sitenav a[aria-current="page"]{color:var(--accent);font-weight:500;background:color-mix(in srgb,var(--accent) 10%,transparent)}' +
    '.sitelang{display:flex;align-items:center;gap:6px}.sitelang label{font-size:.8rem;color:var(--muted)}' +
    '.sitelang select{font:inherit;font-size:.85rem;color:var(--fg);background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:5px 8px}' +
    '.sitefoot{max-width:960px;margin:0 auto;padding-inline:16px;padding-block:24px 40px;display:flex;flex-direction:column;align-items:center;gap:8px;font-size:.8rem;color:var(--muted);text-align:center}' +
    '.sitefoot nav{display:flex;gap:8px 16px;flex-wrap:wrap;justify-content:center}.sitefoot a{color:var(--muted)}' +
    '.sitefoot .popular{display:flex;flex-direction:column;align-items:center;gap:6px;padding-bottom:10px;border-bottom:1px solid var(--line);width:100%}.sitefoot .popular b{font-weight:600;color:var(--fg)}' +
    '@media (max-width:560px){.sitenav{order:3;flex-basis:100%}.sitelang{margin-left:auto}}';
  document.head.appendChild(css);

  var bar = document.createElement('header'); bar.className = 'sitebar';
  bar.innerHTML = '<div class="sitebar-in"><a class="brand" href="' + pathFor(lang, '/') + '"><i aria-hidden="true"></i>PicShifter</a><nav class="sitenav"></nav>' +
    '<div class="sitelang"><label for="lang"></label><select id="lang"></select></div></div>';
  document.body.insertBefore(bar, document.body.firstChild);
  var sel = bar.querySelector('select');
  Object.keys(LANGS).forEach(function (k) { var o = document.createElement('option'); o.value = k; o.textContent = LANGS[k]; sel.appendChild(o); });

  var foot = document.createElement('footer'); foot.className = 'sitefoot';
  foot.innerHTML = '<div class="popular"><b></b><nav></nav></div><nav class="legal"></nav><p></p><p>© ' + new Date().getFullYear() + ' PicShifter</p>';
  document.body.appendChild(foot);

  function paint() {
    document.documentElement.lang = lang === 'zh' ? 'zh-CN' : lang;
    sel.value = lang; bar.querySelector('label').textContent = t('lang');
    var nav = bar.querySelector('.sitenav'); nav.innerHTML = '';
    LINKS.forEach(function (l) { var a = document.createElement('a'); a.href = pathFor(lang, l[1]); a.textContent = t(l[0]); if (here(l[1])) a.setAttribute('aria-current', 'page'); nav.appendChild(a); });
    var pn = foot.querySelector('.popular nav'); pn.innerHTML = ''; foot.querySelector('.popular b').textContent = t('popular');
    POPULAR.forEach(function (l) { var a = document.createElement('a'); a.href = pathFor(lang, l[1]); a.textContent = l[0].charAt(0) === '@' ? t(l[0].slice(1)) : l[0]; pn.appendChild(a); });
    var fn = foot.querySelector('nav.legal'); fn.innerHTML = '';
    FOOT.forEach(function (l) { var a = document.createElement('a'); a.href = pathFor(lang, l[1]); a.textContent = t(l[0]); fn.appendChild(a); });
    foot.querySelector('p').textContent = t('note');
  }
  sel.addEventListener('change', function () {
    var next = sel.value; try { localStorage.setItem(KEY, next); } catch (e) {}
    if (window.PAGE_LANG) { location.href = pathFor(next, bare) + location.hash; return; }
    lang = next; paint(); subs.forEach(function (f) { f(lang); });
  });
  paint();

  /* Show the <div data-lang="xx"> block that matches the language (falls back to English). */
  function showLangBlocks() {
    var blocks = document.querySelectorAll('[data-lang]');
    if (!blocks.length) return;
    var has = false; blocks.forEach(function (b) { if (b.getAttribute('data-lang') === lang) has = true; });
    var want = has ? lang : 'en';
    blocks.forEach(function (b) { b.hidden = b.getAttribute('data-lang') !== want; });
  }
  subs.push(showLangBlocks); showLangBlocks();

  window.Site = {
    LANGS: LANGS,
    get lang() { return lang; },
    onChange: function (fn) { subs.push(fn); fn(lang); }
  };
})();
