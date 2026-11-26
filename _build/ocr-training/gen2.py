"""Realistic glyph samples for the neural network: rendered from fonts, then made to look like
screenshots, scans and phone photos (tilt, blur, low resolution, noise, JPEG, uneven contrast)."""
import numpy as np, sys, os, random, io
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from multiprocessing import Pool
from feat import normalize
from chars import charset
from gen import KR, LAT, REFS, ref
H_,J_,A_,E_=charset(); CHARS=H_+J_+A_+E_
WQY=[('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',0),('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',2)]
def make(font,size,ch,rnd,refs):
    fg=rnd.randint(0,80); bg=rnd.randint(max(150,fg+90),255)
    W=int(size*2.6); H=int(size*2.4); base=int(size*1.6)
    im=Image.new('L',(W,H),bg); d=ImageDraw.Draw(im); d.text((int(size*0.45),base),ch,fill=fg,font=font,anchor='ls')
    # geometry: width change, slant, small rotation
    sx=rnd.uniform(0.82,1.18); sh=rnd.uniform(-0.18,0.18) if rnd.random()<0.5 else 0
    im=im.transform(im.size,Image.AFFINE,(1/sx,sh,-sh*base,0,1,0),resample=Image.BILINEAR,fillcolor=bg)
    if rnd.random()<0.4: im=im.rotate(rnd.uniform(-3,3),resample=Image.BILINEAR,fillcolor=bg)
    if rnd.random()<0.5: im=im.filter(ImageFilter.GaussianBlur(rnd.uniform(0.2,0.9)*size/24))
    if rnd.random()<0.3:
        f=rnd.uniform(max(0.5,14/size),0.9); s=im.resize((max(4,int(W*f)),max(4,int(H*f))),Image.BILINEAR); im=s.resize((W,H),Image.BILINEAR)
    a=np.asarray(im).astype(np.float32)
    clean=a<(fg+bg)/2
    cy,cx=np.nonzero(clean)
    if len(cy)<2: return None
    cy0,cy1,cx0,cx1=cy.min(),cy.max()+1,cx.min(),cx.max()+1
    if rnd.random()<0.5:  # uneven light
        g=np.linspace(rnd.uniform(-20,0),rnd.uniform(0,20),W)[None,:]; a=a+g
    if rnd.random()<0.6: a=a+np.random.default_rng(rnd.randrange(1<<30)).normal(0,rnd.uniform(1,0.1*(bg-fg)),a.shape)
    a=np.clip(a,0,255).astype(np.uint8)
    if rnd.random()<0.4:
        buf=io.BytesIO(); Image.fromarray(a).save(buf,'JPEG',quality=rnd.randint(30,90)); a=np.asarray(Image.open(buf).convert('L'))
    a=a.astype(np.float32)
    th=(fg+bg)/2+rnd.uniform(-0.15,0.15)*(bg-fg)
    b=a<th
    # the glyph box comes from the clean shape; noise inside the box stays (as in real images)
    b=b[cy0:cy1,cx0:cx1]
    ys,xs=np.nonzero(b)
    if len(ys)<2: return None
    y0,y1,x0,x1=cy0+ys.min(),cy0+ys.max()+1,cx0+xs.min(),cx0+xs.max()+1
    b=b[ys.min():ys.max()+1,xs.min():xs.max()+1]
    T0,H0=refs[rnd.randrange(3)]
    T0=T0+(base-int(size*1.5))
    jit=rnd.uniform(-0.05,0.05)*H0
    P=normalize(b.astype(np.float32))
    geo=np.array([(x1-x0)/H0,(y1-y0)/H0,(y0+jit-T0)/H0,(y1+jit-T0)/H0],np.float32)
    return (P*255+0.5).astype(np.uint8),geo
def job(args):
    path,idx,chars,seed,per=args
    rnd=random.Random(seed); X=[];G=[];Y=[]
    fonts={}
    for ci,ch in chars:
        for k in range(per):
            size=rnd.choice((16,20,24,30,38,46))
            if size not in fonts:
                f=ImageFont.truetype(path,size,index=idx); fonts[size]=(f,[ref(f,size,q) for q in range(3)])
            f,refs=fonts[size]
            try:
                if f.getmask(ch).size[0]==0: break
            except Exception: break
            r=make(f,size,ch,rnd,refs)
            if r is None: continue
            X.append(r[0]); G.append(r[1]); Y.append(ci)
    return X,G,Y
if __name__=='__main__':
    which=sys.argv[1]; per=int(sys.argv[2]); seed0=int(sys.argv[3])
    idx=list(enumerate(CHARS)); lat=[(i,c) for i,c in idx if c in A_ or c in E_]
    fonts=[(p,i,idx) for p,i in KR+WQY]+[(p,i,lat) for p,i in LAT]
    jobs=[]; s=seed0
    for p,i,ch in fonts:
        for k in range(0,len(ch),250): s+=1; jobs.append((p,i,ch[k:k+250],s,per))
    with Pool(os.cpu_count()) as pool: res=pool.map(job,jobs,chunksize=2)
    X=np.stack([x for r in res for x in r[0]]); G=np.stack([g for r in res for g in r[1]]); Y=np.array([y for r in res for y in r[2]],np.int16)
    np.savez(which+'.npz',X=X,G=G,Y=Y); print(which,X.shape,len(set(Y.tolist())))
