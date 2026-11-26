"""Small convolutional network for glyph recognition, written in plain NumPy (forward and backward)."""
import numpy as np, time, sys, json
from numpy.lib.stride_tricks import sliding_window_view as swv
f32=np.float32
def im2col(x):  # x: N,H,W,C -> N*H*W, 9*C (3x3, same padding)
    N,H,W,C=x.shape; p=np.pad(x,((0,0),(1,1),(1,1),(0,0)))
    v=swv(p,(3,3),axis=(1,2))  # N,H,W,C,3,3
    return np.ascontiguousarray(v.transpose(0,1,2,4,5,3)).reshape(N*H*W,9*C)
def col2im(dc,shape):
    N,H,W,C=shape; d=dc.reshape(N,H,W,3,3,C); out=np.zeros((N,H+2,W+2,C),f32)
    for i in range(3):
        for j in range(3): out[:,i:i+H,j:j+W,:]+=d[:,:,:,i,j,:]
    return out[:,1:-1,1:-1,:]
def pool(x):
    N,H,W,C=x.shape; r=x.reshape(N,H//2,2,W//2,2,C); m=r.max(axis=(2,4)); return m,r
def pool_back(dm,r,m):
    mask=(r==m[:,:,None,:,None,:]); cnt=mask.sum(axis=(2,4),keepdims=True)
    return (mask*(dm[:,:,None,:,None,:]/cnt)).reshape(r.shape[0],r.shape[1]*2,r.shape[3]*2,r.shape[5])
class Net:
    def __init__(s,C,ch=(16,32,64),hid=256,seed=0):
        rng=np.random.default_rng(seed); s.ch=ch
        def he(i,o): return (rng.standard_normal((i,o))*np.sqrt(2/i)).astype(f32)
        s.p={'k1':he(9,ch[0]),'b1':np.zeros(ch[0],f32),'k2':he(9*ch[0],ch[1]),'b2':np.zeros(ch[1],f32),'k3':he(9*ch[1],ch[2]),'b3':np.zeros(ch[2],f32),
             'w4':he(16*ch[2]+4,hid),'b4':np.zeros(hid,f32),'w5':(rng.standard_normal((hid,C))*np.sqrt(1/hid)).astype(f32),'b5':np.zeros(C,f32)}
    def forward(s,x,g,train=False):
        p=s.p; c={}; N=x.shape[0]
        a=x[...,None]
        for i,(k,b) in enumerate((('k1','b1'),('k2','b2'),('k3','b3'))):
            col=im2col(a); z=(col@p[k]+p[b]).reshape(a.shape[0],a.shape[1],a.shape[2],-1); r=np.maximum(z,0); m,rr=pool(r)
            if train: c[i]=(col,a.shape,z,rr,m)
            a=m
        flat=np.concatenate([a.reshape(N,-1),g],1)
        h=flat@p['w4']+p['b4']; hr=np.maximum(h,0)
        if train:
            q=getattr(s,'dropout',0.3); s.drop=(np.random.random(hr.shape)>=q).astype(f32)/(1-q); hr=hr*s.drop
        out=hr@p['w5']+p['b5']
        if train: c['fc']=(flat,h,hr,a.shape)
        return out,c
    def backward(s,c,dout):
        p=s.p; gr={}
        flat,h,hr,ash=c['fc']
        gr['w5']=hr.T@dout; gr['b5']=dout.sum(0); dh=(dout@p['w5'].T)*s.drop; dh[h<=0]=0
        gr['w4']=flat.T@dh; gr['b4']=dh.sum(0); dflat=dh@p['w4'].T
        da=dflat[:,:-4].reshape(ash)
        for i,(k,b) in reversed(list(enumerate((('k1','b1'),('k2','b2'),('k3','b3'))))):
            col,ishape,z,rr,m=c[i]
            dr=pool_back(da,rr,m); dz=dr*(z>0); dz2=dz.reshape(-1,dz.shape[-1])
            gr[k]=col.T@dz2; gr[b]=dz2.sum(0)
            if i>0: da=col2im(dz2@p[k].T,ishape)
        return gr
def batches(n,bs,rng):
    perm=rng.permutation(n)
    for i in range(0,n,bs): yield perm[i:i+bs]
if __name__=='__main__':
    tr=np.load('train.npz'); va=np.load('val.npz')
    X=tr['X']; G=tr['G']; Y=tr['Y'].astype(np.int64); Xv=va['X']; Gv=va['G']; Yv=va['Y'].astype(np.int64)
    C=int(max(Y.max(),Yv.max())+1); net=Net(C)
    m={k:np.zeros_like(v) for k,v in net.p.items()}; v2={k:np.zeros_like(v) for k,v in net.p.items()}
    epochs=int(sys.argv[1]); bs=256; lr=2e-3; step=0; rng=np.random.default_rng(0); t0=time.time()
    def evaluate():
        ok=0
        for i in range(0,len(Xv),1024):
            o,_=net.forward(Xv[i:i+1024].astype(f32)/255,Gv[i:i+1024]); ok+=(o.argmax(1)==Yv[i:i+1024]).sum()
        return ok/len(Xv)
    for ep in range(epochs):
        tl=0; nb=0
        for idx in batches(len(X),bs,rng):
            x=X[idx].astype(f32)/255
            # small random shift for robustness
            sh=rng.integers(-1,2,2); x=np.roll(x,tuple(sh),axis=(1,2))
            g=G[idx]+rng.normal(0,0.02,G[idx].shape).astype(f32)
            out,c=net.forward(x,g,True); y=Y[idx]
            out-=out.max(1,keepdims=True); e=np.exp(out); pr=e/e.sum(1,keepdims=True)
            tl+=-np.log(pr[np.arange(len(y)),y]+1e-9).mean(); nb+=1
            pr[np.arange(len(y)),y]-=1; pr/=len(y)
            gr=net.backward(c,pr.astype(f32)); step+=1
            for k in net.p:
                gk=gr[k]+(1e-5*net.p[k] if net.p[k].ndim>1 else 0)
                m[k]=0.9*m[k]+0.1*gk; v2[k]=0.999*v2[k]+0.001*gk*gk
                net.p[k]-=lr*(m[k]/(1-0.9**step))/(np.sqrt(v2[k]/(1-0.999**step))+1e-8)
            if nb%200==0: print('  ep',ep,'batch',nb,'loss',round(tl/nb,3),'%.0fs'%(time.time()-t0),flush=True)
        if ep>=epochs-4: lr*=0.4
        acc=evaluate(); print('epoch',ep,'loss',round(tl/nb,3),'val acc',round(float(acc),4),'%.0fs'%(time.time()-t0),flush=True)
        np.savez('cnn.npz',**net.p)
