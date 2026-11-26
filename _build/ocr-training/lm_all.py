"""Character counts from PicShifter's own Korean/English text: how often each character appears, and which
character tends to follow which. Used to settle look-alike shapes (은/온, 을/올)."""
import json
from chars import charset
H_,J_,A_,E_=charset(); CHARS=H_+J_+A_+E_; ix={c:i for i,c in enumerate(CHARS)}
C=json.load(open('corpus_all.json')); uni=[0]*len(CHARS); bi={}
for s in C['ko']+C['en']:
    prev=-1
    for ch in s:
        i=ix.get(ch, -1)
        if i>=0:
            uni[i]+=1; k=prev*len(CHARS)+i if prev>=0 else -1-i
            bi[k]=bi.get(k,0)+1
        prev=i
pairs=[[k,v] for k,v in bi.items()]
json.dump({'uni':uni,'bi':pairs},open('out/ocr-lm-all.json','w'),separators=(',',':'))
import os; print('chars seen',sum(1 for u in uni if u),'pairs',len(pairs),'bytes',os.path.getsize('out/ocr-lm-all.json'))
print('은',uni[ix['은']],'온',uni[ix['온']],'을',uni[ix['을']],'올',uni[ix['올']])
