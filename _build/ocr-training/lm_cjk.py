"""Character counts for ja/zh from PicShifter's own page text (+ English pages for Latin words)."""
import json, sys, os
import cjk
lang=sys.argv[1]; CHARS=cjk.charset(lang); ix={c:i for i,c in enumerate(CHARS)}
FW={'（':'(','）':')','：':':','！':'!','？':'?','，':',','；':';'}
lines=json.load(open('corpus_cjk.json'))[lang]+json.load(open('corpus2_all.json'))['en'][:300]
uni=[0]*len(CHARS); bi={}
for s in lines:
    prev=-1
    for ch in s:
        i=ix.get(ch,ix.get(FW.get(ch,''),-1))
        if i>=0:
            uni[i]+=1; k=prev*len(CHARS)+i if prev>=0 else -1-i; bi[k]=bi.get(k,0)+1
        prev=i
os.makedirs('out_'+lang,exist_ok=True)
json.dump({'uni':uni,'bi':[[k,v] for k,v in bi.items()]},open('out_%s/ocr-lm.json'%lang,'w'),separators=(',',':'))
print(lang,'chars seen',sum(1 for u in uni if u),'pairs',len(bi),os.path.getsize('out_%s/ocr-lm.json'%lang))
