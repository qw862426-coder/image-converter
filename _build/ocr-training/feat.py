"""Glyph features shared by training (Python) and the browser (JS port must match exactly)."""
import numpy as np
S=32; BOX=28; SUB=4; G=8; CELL=S//G
def normalize(ink):
    """ink: 2D float array (1=ink) cropped tightly. Returns 32x32 float image, aspect kept, centred."""
    h,w=ink.shape; s=BOX/max(h,w); nw=max(1,int(round(w*s))); nh=max(1,int(round(h*s)))
    out=np.zeros((S,S),np.float32); x0=(S-nw)//2; y0=(S-nh)//2
    # point-sample a SUB×SUB grid inside every target pixel and average
    off=(np.arange(SUB)+0.5)/SUB
    ys=((np.arange(nh)[:,None]+off[None,:])*(h/nh)).reshape(-1); xs=((np.arange(nw)[:,None]+off[None,:])*(w/nw)).reshape(-1)
    yi=np.minimum(h-1,ys.astype(np.int32)); xi=np.minimum(w-1,xs.astype(np.int32))
    samp=ink[yi][:,xi].reshape(nh,SUB,nw,SUB).mean(axis=(1,3))
    out[y0:y0+nh,x0:x0+nw]=samp
    return out
def grad_feat(P):
    Pp=np.pad(P,1)
    gx=Pp[1:-1,2:]-Pp[1:-1,:-2]; gy=Pp[2:,1:-1]-Pp[:-2,1:-1]
    mag=np.sqrt(gx*gx+gy*gy); ang=np.arctan2(gy,gx); ang=np.where(ang<0,ang+2*np.pi,ang)
    b=ang/(2*np.pi)*8; b0=np.floor(b).astype(np.int32)%8; fr=b-np.floor(b); b1=(b0+1)%8
    F=np.zeros((G,G,8),np.float32)
    ys,xs=np.mgrid[0:S,0:S]
    cy=(ys+0.5)/CELL-0.5; cx=(xs+0.5)/CELL-0.5
    y0=np.floor(cy).astype(np.int32); x0=np.floor(cx).astype(np.int32); ty=cy-y0; tx=cx-x0
    for dy,wy in ((0,1-ty),(1,ty)):
        for dx,wx in ((0,1-tx),(1,tx)):
            yy=y0+dy; xx=x0+dx; ok=(yy>=0)&(yy<G)&(xx>=0)&(xx<G)
            for bb,wb in ((b0,1-fr),(b1,fr)):
                np.add.at(F,(yy[ok],xx[ok],bb[ok]),(mag*wy*wx*wb)[ok])
    f=np.sqrt(F.reshape(-1)); n=np.linalg.norm(f); return f/(n+1e-6)
def features(ink,top,bottom,left,right,T0,H0):
    """ink: tight crop; top/bottom/left/right: pixel box in line coords; T0/H0: line reference top and height"""
    g=grad_feat(normalize(ink))
    geo=np.array([(right-left)/H0,(bottom-top)/H0,(top-T0)/H0,(bottom-T0)/H0],np.float32)
    return np.concatenate([g,geo])
