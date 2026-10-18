"""Generate every page of the site in 8 languages.

Sources (edit these, not the generated pages):
  _build/templates/*.html        page layouts (tool pages and the article shell)
  _build/content/<lang>/*.html   article text per language (falls back to English)
  _build/content/<lang>/meta.json titles/descriptions for guide, about, privacy, contact
  _build/pages_data.py           feature pages: preset + titles in 8 languages
  */i18n.js, assets/i18n-image.js tool interface text in 8 languages

Output: English at the root (/, /heic-to-jpg/ ...), other languages under /<lang>/ (/ko/, /ja/ ...),
plus sitemap.xml.  Run from the repo root:  python3 _build/build_site.py
"""
import html, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from pages_data import PAGES  # noqa: E402

SITE = 'https://picshifter.pages.dev'
LANGS = ['en', 'ko', 'ja', 'zh', 'es', 'pt', 'fr', 'de']
HREFLANG = {'zh': 'zh-Hans'}
HTML_LANG = {'zh': 'zh-CN'}
OG_LOCALE = {'en': 'en_US', 'ko': 'ko_KR', 'ja': 'ja_JP', 'zh': 'zh_CN', 'es': 'es_ES', 'pt': 'pt_BR', 'fr': 'fr_FR', 'de': 'de_DE'}
LASTMOD = '2026-10-17'
MORE = {'en': 'More free tools', 'ko': '다른 무료 도구', 'ja': 'ほかの無料ツール', 'zh': '更多免费工具', 'es': 'Más herramientas gratis',
        'pt': 'Mais ferramentas grátis', 'fr': 'Autres outils gratuits', 'de': 'Weitere kostenlose Tools'}

I18N = json.loads(subprocess.check_output(['node', os.path.join(HERE, 'dump_i18n.js')]))
TOOLS = [('/', 'image'), ('/document-to-pdf/', 'doc'), ('/scan/', 'scan'), ('/remove-background/', 'bg')]
ARTICLES = ['guide', 'about', 'privacy', 'contact']
ALL_PATHS = [p for p, _ in TOOLS] + ['/%s/' % p['slug'] for p in PAGES] + ['/%s/' % a for a in ARTICLES]
LANDING_ORDER = [p['slug'] for p in PAGES] + ['scan', 'remove-background']


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def content(lang, name):
    p = os.path.join(HERE, 'content', lang, name + '.html')
    return read(p) if os.path.exists(p) else read(os.path.join(HERE, 'content', 'en', name + '.html'))


def meta_json(lang):
    p = os.path.join(HERE, 'content', lang, 'meta.json')
    base = json.loads(read(os.path.join(HERE, 'content', 'en', 'meta.json')))
    if os.path.exists(p):
        base.update(json.loads(read(p)))
    return base


def prefix(lang):
    return '' if lang == 'en' else '/' + lang


def url(lang, path):
    return SITE + prefix(lang) + path


def tr(table, lang, key, override=None):
    for src in ([override.get(lang, {}), table.get(lang, {}), override.get('en', {}), table.get('en', {})] if override
                else [table.get(lang, {}), table.get('en', {})]):
        if key in src:
            return src[key]
    return None


def one(pattern, repl, s):
    out, n = re.subn(pattern, lambda m: repl(m) if callable(repl) else repl, s, count=1, flags=re.S)
    assert n == 1, pattern
    return out


def head_links(lang, path):
    alts = ''.join('<link rel="alternate" hreflang="%s" href="%s">\n' % (HREFLANG.get(L, L), url(L, path)) for L in LANGS)
    alts += '<link rel="alternate" hreflang="x-default" href="%s">\n' % url('en', path)
    return '<link rel="canonical" href="%s">\n%s' % (url(lang, path), alts)


def localize(s, lang, path, title, desc, table=None, override=None):
    s = one(r'<html lang="[^"]*">', '<html lang="%s">' % HTML_LANG.get(lang, lang), s)
    s = one(r'<link rel="canonical" href="[^"]*">\n?', head_links(lang, path), s)
    s = one(r'<title>.*?</title>', '<title>%s</title>' % html.escape(title, quote=False), s)
    s = one(r'(<meta(?=[^>]*name="description")[^>]*content=")[^"]*(")', lambda m: m.group(1) + html.escape(desc) + m.group(2), s)
    # robots + Open Graph tags (used by Naver, Facebook, KakaoTalk link previews, ...)
    og = ('<meta name="robots" content="index, follow">\n'
          '<meta property="og:type" content="website">\n'
          '<meta property="og:site_name" content="PicShifter">\n'
          '<meta property="og:locale" content="%s">\n'
          '<meta property="og:url" content="%s">\n'
          '<meta property="og:title" content="%s">\n'
          '<meta property="og:description" content="%s">\n'
          '<meta name="twitter:card" content="summary">\n') % (OG_LOCALE[lang], url(lang, path), html.escape(title), html.escape(desc))
    s = one(r'(<meta(?=[^>]*name="description")[^>]*>\n?)', lambda m: m.group(1) + og, s)
    if table is not None:
        def text(m):
            v = tr(table, lang, m.group(3), override)
            return m.group(1) + (html.escape(v, quote=False) if v is not None else m.group(4)) + m.group(5)
        s = re.sub(r'(<(\w+)\b[^>]*\bdata-i18n="(\w+)"[^>]*>)([^<]*)(</\2>)', text, s)
        def set_attr(attr_name, data_name):
            def f(m):
                tag, key = m.group(0), m.group(1)
                v = tr(table, lang, key, override)
                if v is None:
                    return tag
                return re.sub(r'(?<![-\w])%s="[^"]*"' % attr_name, '%s="%s"' % (attr_name, html.escape(v).replace('\\', '\\\\')), tag)
            return f
        s = re.sub(r'<[^>]*\bdata-i18n-label="(\w+)"[^>]*>', set_attr('label', 'label'), s)
        s = re.sub(r'<[^>]*\bdata-i18n-aria="(\w+)"[^>]*>', set_attr('aria-label', 'aria'), s)
    s = one(r'<script src="/assets/site\.js"></script>', '<script>window.PAGE_LANG=%s;</script>\n<script src="/assets/site.js"></script>' % json.dumps(lang), s)
    if lang != 'en':
        def link(m):
            target = m.group(1)
            base = target.split('#')[0]
            return 'href="%s%s"' % (prefix(lang), target) if base in ALL_PATHS else m.group(0)
        s = re.sub(r'href="(/[^"]*)"', link, s)
    return s


def landing_name(lang, slug):
    if slug == 'scan':
        return I18N['scan'][lang].get('h1') or I18N['scan']['en']['h1']
    if slug == 'remove-background':
        return I18N['bg'][lang].get('h1') or I18N['bg']['en']['h1']
    p = next(p for p in PAGES if p['slug'] == slug)
    return p['meta'].get(lang, p['meta']['en'])['h1']


def related(lang, slug):
    items = ''.join('<li><a href="/%s/">%s</a></li>' % (k, html.escape(landing_name(lang, k))) for k in LANDING_ORDER if k != slug)
    return '<h2>%s</h2><ul class="related">%s</ul>' % (MORE[lang], items)


_VER = {}


def version_assets(s):
    """Add ?v=<content hash> to local .js/.css links, so browsers and search robots never reuse an old copy."""
    import hashlib
    def rep(m):
        p = m.group(2)
        f = os.path.join(ROOT, p.lstrip('/'))
        if not os.path.isfile(f):
            return m.group(0)
        if p not in _VER:
            _VER[p] = hashlib.md5(open(f, 'rb').read()).hexdigest()[:8]
        return '%s="%s?v=%s"' % (m.group(1), p, _VER[p])
    return re.sub(r'\b(src|href)="(/[^"?#]+\.(?:js|css))"', rep, s)


def write(lang, path, s):
    s = version_assets(s)
    out = os.path.join(ROOT, prefix(lang).lstrip('/'), path.lstrip('/'), 'index.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(s)


def build():
    tpl = {k: read(os.path.join(HERE, 'templates', k + '.html')) for k in ['image', 'doc', 'scan', 'bg', 'article']}
    count = 0
    for lang in LANGS:
        for path, kind in TOOLS:
            t = I18N[kind]
            s = localize(tpl[kind], lang, path, tr(t, lang, 'title'), tr(t, lang, 'desc'), t)
            write(lang, path, s); count += 1
        for p in PAGES:
            path = '/%s/' % p['slug']
            kind = 'image' if p['base'] == 'image' else 'doc'
            m = p['meta'].get(lang, p['meta']['en'])
            s = tpl[kind]
            preset = '<script>window.PRESET=%s;window.PAGE_I18N=%s;</script>\n' % (json.dumps(p['preset']), json.dumps(p['meta'], ensure_ascii=False))
            s = one(r'<script src="/assets/codecs\.js"></script>', preset + '<script src="/assets/codecs.js"></script>', s)
            art = '\n  <section class="doc landing">\n    <article>\n%s%s\n    </article>\n  </section>\n' % (content(lang, p['slug']), related(lang, p['slug']))
            s = one(r'\n</main>', art + '</main>', s)
            s = localize(s, lang, path, m['title'], m['desc'], I18N[kind], p['meta'])
            write(lang, path, s); count += 1
        meta = meta_json(lang)
        for a in ARTICLES:
            path = '/%s/' % a
            s = tpl['article'].replace('<!--ARTICLE-->', content(lang, a))
            s = localize(s, lang, path, meta[a]['title'], meta[a]['desc'])
            write(lang, path, s); count += 1
    # sitemap with language alternates
    rows = []
    for path in ALL_PATHS:
        alts = ''.join('<xhtml:link rel="alternate" hreflang="%s" href="%s"/>' % (HREFLANG.get(L, L), url(L, path)) for L in LANGS)
        alts += '<xhtml:link rel="alternate" hreflang="x-default" href="%s"/>' % url('en', path)
        for L in LANGS:
            rows.append('  <url><loc>%s</loc><lastmod>%s</lastmod>%s</url>' % (url(L, path), LASTMOD, alts))
    sm = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
          'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + '\n'.join(rows) + '\n</urlset>\n')
    with open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write(sm)
    return count, len(rows)


if __name__ == '__main__':
    pages, urls = build()
    print('pages written:', pages, '| sitemap urls:', urls)
