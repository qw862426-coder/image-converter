"""Character counts (v2 character list) from corpus2_<which>.json -> out2/ocr-lm-<which>.json"""
import json, sys, os
from chars import charset
H_,J_,A_,E_=charset(); CHARS=H_+J_+A_+E_; ix={c:i for i,c in enumerate(CHARS)}
which=sys.argv[1]; C=json.load(open('corpus2_%s.json'%which)); uni=[0]*len(CHARS); bi={}
for lang,lines in C.items():
    for s in lines:
        prev=-1
        for ch in s:
            i=ix.get(ch,-1)
            if i>=0:
                uni[i]+=1; k=prev*len(CHARS)+i if prev>=0 else -1-i; bi[k]=bi.get(k,0)+1
            prev=i
json.dump({'uni':uni,'bi':[[k,v] for k,v in bi.items()]},open('out2/ocr-lm-%s.json'%which,'w'),separators=(',',':'))
print(which,'chars seen',sum(1 for u in uni if u),'pairs',len(bi),'bytes',os.path.getsize('out2/ocr-lm-%s.json'%which))
