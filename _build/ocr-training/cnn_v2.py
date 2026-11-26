"""Train network v2 (2,721 characters). Starts from an earlier network; new characters get fresh output weights.
usage: python3 cnn_v2.py <init.npz> <epochs> <out.npz> <lr>"""
import numpy as np, sys, time
from cnn import Net
from chars import charset
f32=np.float32; H_,J_,A_,E_=charset(); C=len(H_+J_+A_+E_)
def ld(p):
    X=np.fromfile(p+'.x',np.uint8).reshape(-1,32,32); G=np.fromfile(p+'.g',f32).reshape(-1,4); Y=np.fromfile(p+'.y',np.int16).astype(np.int64); return X,G,Y
init,epochs,out,lr=sys.argv[1],int(sys.argv[2]),sys.argv[3],float(sys.argv[4])
a=ld('p2tr_a'); b=ld('p2tr_b'); g=np.load('train2g.npz')
X=np.concatenate([a[0],b[0],g['X']]); G=np.concatenate([a[1],b[1],g['G']]); Y=np.concatenate([a[2],b[2],g['Y'].astype(np.int64)])
Xv,Gv,Yv=ld('p2va')
p={k:v.astype(f32) for k,v in np.load(init).items()}
if p['w5'].shape[1]<C:
    k=C-p['w5'].shape[1]; rng0=np.random.default_rng(1)
    p['w5']=np.concatenate([p['w5'],(rng0.normal(0,0.02,(p['w5'].shape[0],k))).astype(f32)],1)
    p['b5']=np.concatenate([p['b5'],np.full(k,np.median(p['b5']),f32)])
net=Net(C); net.p=p; rng=np.random.default_rng(int(time.time()))
def evaluate():
    ok=0; okn=0; nn=0
    for i in range(0,len(Xv),1024):
        o,_=net.forward(Xv[i:i+1024].astype(f32)/255,Gv[i:i+1024]); pr=o.argmax(1); y=Yv[i:i+1024]
        ok+=(pr==y).sum(); m=y>=2518; okn+=(pr[m]==y[m]).sum(); nn+=m.sum()
    return ok/len(Xv), okn/max(1,nn)
print('start val acc (all, new letters)',[round(float(v),4) for v in evaluate()],'train',len(Y),flush=True)
m={k:np.zeros_like(v) for k,v in net.p.items()}; v2={k:np.zeros_like(v) for k,v in net.p.items()}; step=0; t0=time.time(); bs=256
for ep in range(epochs):
    tl=0; nb=0; perm=rng.permutation(len(Y))
    for i in range(0,len(Y),bs):
        idx=perm[i:i+bs]; x=X[idx].astype(f32)/255
        sh=rng.integers(-1,2,2); x=np.roll(x,tuple(sh),axis=(1,2)); gg=G[idx]+rng.normal(0,0.02,G[idx].shape).astype(f32)
        o,c=net.forward(x,gg,True); y=Y[idx]; o-=o.max(1,keepdims=True); e=np.exp(o); pr=e/e.sum(1,keepdims=True)
        tl+=-np.log(pr[np.arange(len(y)),y]+1e-9).mean(); nb+=1; pr[np.arange(len(y)),y]-=1; pr/=len(y)
        gr=net.backward(c,pr.astype(f32)); step+=1
        for k in net.p:
            gk=gr[k]+(1e-5*net.p[k] if net.p[k].ndim>1 else 0)
            m[k]=0.9*m[k]+0.1*gk; v2[k]=0.999*v2[k]+0.001*gk*gk
            net.p[k]-=lr*(m[k]/(1-0.9**step))/(np.sqrt(v2[k]/(1-0.999**step))+1e-8)
        if nb%500==0: print('  ep',ep,'batch',nb,'loss',round(tl/nb,3),'%.0fs'%(time.time()-t0),flush=True)
    lr*=0.6
    np.savez(out,**net.p)
    print('epoch',ep,'loss',round(tl/nb,3),'val acc (all, new letters)',[round(float(v),4) for v in evaluate()],'%.0fs'%(time.time()-t0),flush=True)
