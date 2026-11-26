"""Train the prototype reader (LDA, 128 dims) on v2 samples and export ocr-model.bin + ocr-meta.json."""
import numpy as np, scipy.linalg as sl, json
from chars import charset
H_,J_,A_,E_=charset(); CHARS=H_+J_+A_+E_
X=np.load('train2_X.npy',mmap_mode='r'); y=np.load('train2_y.npy'); Xt=np.load('hold2_X.npy'); yt=np.load('hold2_y.npy')
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
    Q=(np.asarray(Xq)-mu).astype(np.float32)@W; d2=np.maximum(0,(Q*Q).sum(1)[:,None]-2*Q@Pq.T+(Pq*Pq).sum(1)[None]); return d2
d2=run(Xt); pred=d2.argmin(1); h=yt<len(H_)
print('held-out fonts: all',round((pred==yt).mean(),4),'hangul',round((pred[h]==yt[h]).mean(),4),'other',round((pred[~h]==yt[~h]).mean(),4))
sub=np.arange(0,N,40); d2t=run(X[sub]); print('train sample acc',round((d2t.argmin(1)==y[sub]).mean(),4))
med=float(np.median(np.sqrt(d2t.min(1))))
buf=mu.astype(np.float32).tobytes()+W.tobytes()+sc.tobytes()+q.tobytes()
open('out2/ocr-model.bin','wb').write(buf)
json.dump({'chars':''.join(CHARS),'dim':d,'D':D,'classes':C,'medDist':med},open('out2/ocr-meta.json','w'),ensure_ascii=False)
print('bytes',len(buf),'med',med)
