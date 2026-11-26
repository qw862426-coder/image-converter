"""Collect PicShifter's own Korean and English page text (for natural sentences and character counts)."""
import re, glob, html, json
def clean(p):
    t=open(p,encoding='utf-8').read(); t=re.sub(r'<(script|style)[^>]*>.*?</\1>',' ',t,flags=re.S); t=re.sub(r'<[^>]+>','\n',t); t=html.unescape(t)
    return [re.sub(r'\s+',' ',l).strip() for l in t.split('\n') if len(l.strip())>=4]
B='/home/claude/image-converter/'
ko=[];en=[]
for p in glob.glob(B+'_build/content/ko/*.html')+glob.glob(B+'_build/posts/ko/*.html'):
    if 'heic-photos-wont-open' in p or 'heic-to-jpg' in p: continue  # kept out: the screenshot test shows this page
    ko+=clean(p)
for p in glob.glob(B+'_build/content/en/*.html')+glob.glob(B+'_build/posts/en/*.html'): en+=clean(p)
if __name__=="__main__": json.dump({'ko':ko,'en':en},open('corpus.json','w'),ensure_ascii=False)
if __name__=="__main__": print(len(ko),len(en),sum(len(x) for x in ko))
