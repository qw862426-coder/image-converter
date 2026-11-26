"""Continue training the network on pieces cut by the real reader (plus part of the old samples)."""
import numpy as np, sys, time
from cnn import Net
f32=np.float32
def ld(p):
    X=np.fromfile(p+'.x',np.uint8).reshape(-1,32,32); G=np.fromfile(p+'.g',f32).reshape(-1,4); Y=np.fromfile(p+'.y',np.int16).astype(np.int64); return X,G,Y
init,epochs,out=sys.argv[1],int(sys.argv[2]),sys.argv[3]
a=ld('ptr_a'); b=ld('ptr_b'); tr=np.load('train.npz'); rng=np.random.default_rng(0); k=rng.choice(len(tr['Y']),120000,replace=False)
X=np.concatenate([a[0],b[0],tr['X'][k]]); G=np.concatenate([a[1],b[1],tr['G'][k]]); Y=np.concatenate([a[2],b[2],tr['Y'][k].astype(np.int64)])
Xv,Gv,Yv=ld('pva')
p=dict(np.load(init)); net=Net(p['b5'].shape[0]); net.p={k:v.astype(f32) for k,v in p.items()}
def evaluate():
    ok=0
    for i in range(0,len(Xv),1024): o,_=net.forward(Xv[i:i+1024].astype(f32)/255,Gv[i:i+1024]); ok+=(o.argmax(1)==Yv[i:i+1024]).sum()
    return ok/len(Xv)
print('start val acc',round(float(evaluate()),4),'train',len(Y),flush=True)
m={k:np.zeros_like(v) for k,v in net.p.items()}; v2={k:np.zeros_like(v) for k,v in net.p.items()}
lr=float(sys.argv[4]) if len(sys.argv)>4 else 6e-4; step=0; t0=time.time(); bs=256
for ep in range(epochs):
    tl=0; nb=0; perm=rng.permutation(len(Y))
    for i in range(0,len(Y),bs):
        idx=perm[i:i+bs]; x=X[idx].astype(f32)/255
        sh=rng.integers(-1,2,2); x=np.roll(x,tuple(sh),axis=(1,2)); g=G[idx]+rng.normal(0,0.02,G[idx].shape).astype(f32)
        o,c=net.forward(x,g,True); y=Y[idx]; o-=o.max(1,keepdims=True); e=np.exp(o); pr=e/e.sum(1,keepdims=True)
        tl+=-np.log(pr[np.arange(len(y)),y]+1e-9).mean(); nb+=1; pr[np.arange(len(y)),y]-=1; pr/=len(y)
        gr=net.backward(c,pr.astype(f32)); step+=1
        for k in net.p:
            gk=gr[k]+(1e-5*net.p[k] if net.p[k].ndim>1 else 0)
            m[k]=0.9*m[k]+0.1*gk; v2[k]=0.999*v2[k]+0.001*gk*gk
            net.p[k]-=lr*(m[k]/(1-0.9**step))/(np.sqrt(v2[k]/(1-0.999**step))+1e-8)
    lr*=0.6
    print('epoch',ep,'loss',round(tl/nb,3),'val acc',round(float(evaluate()),4),'%.0fs'%(time.time()-t0),flush=True)
    np.savez(out,**net.p)
