import numpy as np, scipy.linalg as sl, sys
X=np.load('train_X.npy',mmap_mode='r'); y=np.load('train_y.npy'); Xt=np.load('test_X.npy'); yt=np.load('test_y.npy')
C=y.max()+1; d=X.shape[1]; N=len(y)
mu=np.zeros(d); 
for i in range(0,N,20000): mu+=X[i:i+20000].sum(0)
mu/=N
M=np.zeros((C,d)); n=np.bincount(y,minlength=C)
for i in range(0,N,20000): np.add.at(M,y[i:i+20000],np.asarray(X[i:i+20000],np.float64)-mu)
M/=np.maximum(n,1)[:,None]
Sw=np.zeros((d,d))
for i in range(0,N,20000):
    R=(np.asarray(X[i:i+20000],np.float64)-mu)-M[y[i:i+20000]]; Sw+=R.T@R
Sw/=N; Sb=(M.T*(n/N))@M
w,V=sl.eigh(Sb,Sw+1e-4*np.eye(d)*np.trace(Sw)/d); order=np.argsort(w)[::-1]
np.save('lda_V.npy',V[:,order[:256]].astype(np.float32)); np.save('lda_mu.npy',mu.astype(np.float32))
for D in [128]:
    W=V[:,order[:D]].astype(np.float32); P=(M@W).astype(np.float32)
    def acc(Xq,yq):
        Q=(np.asarray(Xq)-mu).astype(np.float32)@W; d2=(Q*Q).sum(1)[:,None]-2*Q@P.T+(P*P).sum(1)[None]; return (d2.argmin(1)==yq).mean()
    print('D',D,'train',round(acc(X[::20],y[::20]),4),'heldout WQY',round(acc(Xt,yt),4))
