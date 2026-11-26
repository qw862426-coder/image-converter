"""PicShifter's own page text in Korean, English, German, Spanish, French and Portuguese.
held=True leaves out the HEIC article used by the screenshot test."""
import glob, json, sys
from corpus import clean
B='/home/claude/image-converter/'
def collect(held):
    out={}
    for lang in ['ko','en','de','es','fr','pt']:
        L=[]
        for p in glob.glob(B+'_build/content/%s/*.html'%lang)+glob.glob(B+'_build/posts/%s/*.html'%lang):
            if held and ('heic-photos-wont-open' in p or 'heic-to-jpg' in p): continue
            L+=clean(p)
        out[lang]=L
    return out
if __name__=='__main__':
    held=sys.argv[1]=='held'; c=collect(held); json.dump(c,open('corpus2_%s.json'%sys.argv[1],'w'),ensure_ascii=False)
    print({k:sum(len(x) for x in v) for k,v in c.items()})
