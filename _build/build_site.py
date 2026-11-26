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
ADSENSE = ('<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6213198663836411"\n'
           '     crossorigin="anonymous"></script>\n')
OG_LOCALE = {'en': 'en_US', 'ko': 'ko_KR', 'ja': 'ja_JP', 'zh': 'zh_CN', 'es': 'es_ES', 'pt': 'pt_BR', 'fr': 'fr_FR', 'de': 'de_DE'}
LASTMOD = '2026-11-10'
MORE = {'en': 'More free tools', 'ko': '다른 무료 도구', 'ja': 'ほかの無料ツール', 'zh': '更多免费工具', 'es': 'Más herramientas gratis',
        'pt': 'Mais ferramentas grátis', 'fr': 'Autres outils gratuits', 'de': 'Weitere kostenlose Tools'}

I18N = json.loads(subprocess.check_output(['node', os.path.join(HERE, 'dump_i18n.js')]))
TOOLS = [('/', 'image'), ('/document-to-pdf/', 'doc'), ('/scan/', 'scan'), ('/remove-background/', 'bg'), ('/photo-editor/', 'edit'), ('/remove-object/', 'erase')]
ARTICLES = ['guide', 'about', 'privacy', 'contact']
ALL_PATHS = [p for p, _ in TOOLS] + ['/%s/' % p['slug'] for p in PAGES] + ['/%s/' % a for a in ARTICLES]
LANDING_ORDER = [p['slug'] for p in PAGES] + ['scan', 'remove-background', 'photo-editor', 'remove-object']

# Articles ("읽을거리"): English and Korean only. _build/posts/posts.json lists them with a publish date;
# a post goes live only when the site is built on or after that date (Korea time).
import datetime as _dt
POST_LANGS = ['en', 'ko']
POSTS_ALL = json.loads(open(os.path.join(HERE, 'posts', 'posts.json'), encoding='utf-8').read())
TODAY = _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=9))).strftime('%Y-%m-%d')
POSTS = sorted([p for p in POSTS_ALL if p['date'] <= TODAY], key=lambda p: p['date'], reverse=True)
POST_PATHS = ['/articles/'] + ['/articles/%s/' % p['slug'] for p in POSTS]
POST_UI = {
    'en': {'index_title': 'Articles: tips for images, PDFs and documents | PicShifter',
           'index_desc': 'Plain guides to everyday file problems: photos that won’t open, files that are too big, and documents to submit.',
           'h1': 'Articles', 'lede': 'Plain guides to everyday file problems, with the free PicShifter tool that fixes each one.',
           'date': 'Published %s', 'more': 'More articles', 'all': 'All articles', 'try': 'Try it now:'},
    'ko': {'index_title': '읽을거리: 사진·PDF·문서 파일 꿀팁 | PicShifter',
           'index_desc': '안 열리는 사진, 너무 큰 파일, 제출용 서류처럼 자주 겪는 파일 문제를 쉽게 풀어 쓴 글 모음이에요.',
           'h1': '읽을거리', 'lede': '자주 겪는 파일 문제를 쉽게 풀어 쓴 글이에요. 글마다 바로 해결할 수 있는 무료 도구를 함께 알려 드려요.',
           'date': '%s 게시', 'more': '다른 글', 'all': '전체 글 보기', 'try': '바로 해 보기:'},
}



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


def head_links(lang, path, langs=None):
    alts = ''.join('<link rel="alternate" hreflang="%s" href="%s">\n' % (HREFLANG.get(L, L), url(L, path)) for L in (langs or LANGS))
    alts += '<link rel="alternate" hreflang="x-default" href="%s">\n' % url('en', path)
    return '<link rel="canonical" href="%s">\n%s' % (url(lang, path), alts)


def localize(s, lang, path, title, desc, table=None, override=None, langs=None):
    s = one(r'<html lang="[^"]*">', '<html lang="%s">' % HTML_LANG.get(lang, lang), s)
    s = one(r'<link rel="canonical" href="[^"]*">\n?', head_links(lang, path, langs), s)
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
    # Google AdSense (publisher ca-pub-6213198663836411)
    s = one(r'</head>', ADSENSE + '</head>', s)
    s = one(r'<script src="/assets/site\.js"></script>', '<script>window.PAGE_LANG=%s;%s</script>\n<script src="/assets/site.js"></script>' % (json.dumps(lang), ('window.PAGE_ONLY=%s;' % json.dumps(langs)) if langs else ''), s)
    if lang != 'en':
        def link(m):
            target = m.group(1)
            base = target.split('#')[0]
            return 'href="%s%s"' % (prefix(lang), target) if base in ALL_PATHS or base in POST_PATHS else m.group(0)
        s = re.sub(r'href="(/[^"]*)"', link, s)
    return s


def landing_name(lang, slug):
    if slug == 'scan':
        return I18N['scan'][lang].get('h1') or I18N['scan']['en']['h1']
    if slug == 'remove-background':
        return I18N['bg'][lang].get('h1') or I18N['bg']['en']['h1']
    if slug == 'photo-editor':
        return I18N['edit'][lang].get('h1') or I18N['edit']['en']['h1']
    if slug == 'remove-object':
        return I18N['erase'][lang].get('h1') or I18N['erase']['en']['h1']
    p = next(p for p in PAGES if p['slug'] == slug)
    return p['meta'].get(lang, p['meta']['en'])['h1']


GUIDE_NAME = {'en': 'How to use', 'ko': '사용 방법', 'ja': '使い方', 'zh': '使用方法', 'es': 'Cómo usarlo', 'pt': 'Como usar',
              'fr': 'Mode d’emploi', 'de': 'Anleitung'}


def related(lang, slug):
    items = ''.join('<li><a href="/%s/">%s</a></li>' % (k, html.escape(landing_name(lang, k))) for k in LANDING_ORDER if k != slug)
    items += '<li><a href="/guide/">%s</a></li>' % html.escape(GUIDE_NAME[lang])
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
    tpl = {k: read(os.path.join(HERE, 'templates', k + '.html')) for k in ['image', 'doc', 'scan', 'bg', 'edit', 'erase', 'article']}
    count = 0
    for lang in LANGS:
        for path, kind in TOOLS:
            t = I18N[kind]
            s = tpl[kind]
            # explanatory article under the tool (content/<lang>/tool-<kind>.html), plus links to the other tools
            art = '\n  <section class="doc landing">\n    <article>\n%s%s\n    </article>\n  </section>\n' % (
                content(lang, 'tool-' + kind), related(lang, path.strip('/')))
            s = one(r'\n</main>', art + '</main>', s)
            s = localize(s, lang, path, tr(t, lang, 'title'), tr(t, lang, 'desc'), t)
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
    count += build_posts(tpl['article'])
    # sitemap with language alternates
    rows = []
    for path in ALL_PATHS:
        alts = ''.join('<xhtml:link rel="alternate" hreflang="%s" href="%s"/>' % (HREFLANG.get(L, L), url(L, path)) for L in LANGS)
        alts += '<xhtml:link rel="alternate" hreflang="x-default" href="%s"/>' % url('en', path)
        for L in LANGS:
            rows.append('  <url><loc>%s</loc><lastmod>%s</lastmod>%s</url>' % (url(L, path), LASTMOD, alts))
    for path in POST_PATHS:
        slug = path.strip('/').split('/')[-1]
        p = next((x for x in POSTS if x['slug'] == slug), None)
        last = p['date'] if p else (POSTS[0]['date'] if POSTS else LASTMOD)
        alts = ''.join('<xhtml:link rel="alternate" hreflang="%s" href="%s"/>' % (L, url(L, path)) for L in POST_LANGS)
        alts += '<xhtml:link rel="alternate" hreflang="x-default" href="%s"/>' % url('en', path)
        for L in POST_LANGS:
            rows.append('  <url><loc>%s</loc><lastmod>%s</lastmod>%s</url>' % (url(L, path), last, alts))
    sm = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
          'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + '\n'.join(rows) + '\n</urlset>\n')
    with open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write(sm)
    # sitemap index (a "table of contents" pointing at sitemap.xml) - some sites only get read by Google this way
    with open(os.path.join(ROOT, 'sitemap_index.xml'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                '  <sitemap><loc>%s/sitemap.xml</loc><lastmod>%s</lastmod></sitemap>\n</sitemapindex>\n' % (SITE, LASTMOD))
    with open(os.path.join(ROOT, 'sitemap.txt'), 'w', encoding='utf-8') as f:
        f.write(''.join(url(L, p) + '\n' for p in ALL_PATHS for L in LANGS) + ''.join(url(L, p) + '\n' for p in POST_PATHS for L in POST_LANGS))
    return count, len(rows)


def post_card(lang, p):
    m = p[lang]
    return '<li><a href="/articles/%s/">%s</a><br><span class="post-desc">%s</span></li>' % (p['slug'], html.escape(m['h1']), html.escape(m['desc']))


def build_posts(tpl):
    n = 0
    for lang in POST_LANGS:
        ui = POST_UI[lang]
        # list page
        body = '<h1>%s</h1>\n<p class="lede">%s</p>\n<ul class="post-list">%s</ul>' % (
            ui['h1'], ui['lede'], ''.join(post_card(lang, p) for p in POSTS))
        s = localize(tpl.replace('<!--ARTICLE-->', body), lang, '/articles/', ui['index_title'], ui['index_desc'], langs=POST_LANGS)
        write(lang, '/articles/', s); n += 1
        for p in POSTS:
            m = p[lang]
            text = read(os.path.join(HERE, 'posts', lang, p['slug'] + '.html'))
            others = [q for q in POSTS if q['slug'] != p['slug']][:4]
            d = p['date'] if lang == 'en' else '%s년 %d월 %d일' % (p['date'][:4], int(p['date'][5:7]), int(p['date'][8:10]))
            body = ('<h1>%s</h1>\n<p class="lede">%s</p>\n<p class="meta">%s</p>\n%s\n'
                    '<p class="post-try"><b>%s</b> <a href="%s">%s</a></p>\n'
                    '<h2>%s</h2><ul class="related">%s<li><a href="/articles/">%s</a></li></ul>') % (
                html.escape(m['h1']), html.escape(m['lede']), ui['date'] % d, text,
                ui['try'], p['tool'], html.escape(m['tool_name']),
                ui['more'], ''.join('<li><a href="/articles/%s/">%s</a></li>' % (q['slug'], html.escape(q[lang]['h1'])) for q in others), ui['all'])
            s = localize(tpl.replace('<!--ARTICLE-->', body), lang, '/articles/%s/' % p['slug'], m['title'], m['desc'], langs=POST_LANGS)
            s = s.replace('<meta property="og:type" content="website">', '<meta property="og:type" content="article">')
            write(lang, '/articles/%s/' % p['slug'], s); n += 1
    return n


if __name__ == '__main__':
    pages, urls = build()
    print('pages written:', pages, '| sitemap urls:', urls)
