"""Prototype reader for ja/zh: python3 lda_cjk.py ja -> out_ja/ocr-model.bin + ocr-meta.json"""
import numpy as np, scipy.linalg as sl, json, sys, os
import cjk
lang=sys.argv[1]; CHARS=cjk.charset(lang); os.makedirs('out_'+lang,exist_ok=True)
X=np.load('%s_lda_train_X.npy'%lang,mmap_mode='r'); y=np.load('%s_lda_train_y.npy'%lang); Xt=np.load('%s_lda_hold_X.npy'%lang); yt=np.load('%s_lda_hold_y.npy'%lang)
C=len(CHARS); d=X.shape[1]; N=len(y); B=20000
mu=np.zeros(d)
for i in range(0,N,B): mu+=X[i:i+B].sum(0)
mu/=N
M=np.zeros((C,d)); n=np.bincount(y,minlength=C)
for i in range(0,N,B): np.add.at(M,y[i:i+B],np.asarray(X[i:i+B],np.float64)-mu)
M/=np.maximum(n,1)[:,None]
Sw=np.zeros((d,d))
for i in range(0,N,B): R=(np.asarray(X[i:i+B],np.float64)-mu)-M[y[i:i+B]]; Sw+=R.T@R
Sw/=N; Sb=(M.T*(n/N))@M
w,V=sl.eigh(Sb,Sw+1e-4*np.eye(d)*np.trace(Sw)/d); order=np.argsort(w)[::-1]
D=128; W=V[:,order[:D]].astype(np.float32); P=(M@W).astype(np.float32)
sc=(np.abs(P).max(0)/127+1e-12).astype(np.float32); q=np.clip(np.round(P/sc),-127,127).astype(np.int8); Pq=q*sc
def run(Xq):
    Q=(np.asarray(Xq)-mu).astype(np.float32)@W; return np.maximum(0,(Q*Q).sum(1)[:,None]-2*Q@Pq.T+(Pq*Pq).sum(1)[None])
pred=np.concatenate([run(Xt[i:i+5000]).argmin(1) for i in range(0,len(yt),5000)])
print(lang,'held-out font acc',round((pred==yt).mean(),4))
sub=np.arange(0,N,40); d2t=np.concatenate([run(X[sub[i:i+5000]]) .min(1) for i in range(0,len(sub),5000)])
med=float(np.median(np.sqrt(d2t)))
open('out_%s/ocr-model.bin'%lang,'wb').write(mu.astype(np.float32).tobytes()+W.tobytes()+sc.tobytes()+q.tobytes())
json.dump({'chars':''.join(CHARS),'dim':d,'D':D,'classes':C,'medDist':med,'lang':lang},open('out_%s/ocr-meta.json'%lang,'w'),ensure_ascii=False)
print('saved, med',med)
