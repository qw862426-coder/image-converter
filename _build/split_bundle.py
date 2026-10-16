"""Split a translation bundle (sections starting with '=== name') into _build/content/<lang>/<name>.html|meta.json.
Usage: python3 _build/split_bundle.py <lang> <bundle-file>"""
import json, os, sys
lang, src = sys.argv[1], sys.argv[2]
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'content', lang)
os.makedirs(out, exist_ok=True)
name, buf, n = None, [], 0
def flush():
    global n
    if not name: return
    text = '\n'.join(buf).strip() + '\n'
    if name == 'meta':
        json.loads(text)
        path = os.path.join(out, 'meta.json')
    else:
        path = os.path.join(out, name + '.html')
    with open(path, 'w', encoding='utf-8') as f: f.write(text)
    n += 1
for line in open(src, encoding='utf-8').read().split('\n'):
    if line.startswith('=== '):
        flush(); name, buf = line[4:].strip(), []
    else:
        buf.append(line)
flush()
print(lang, 'files written:', n)
