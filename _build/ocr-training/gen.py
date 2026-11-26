import numpy as np, sys, os, random, pickle
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from multiprocessing import Pool
from feat import features
from chars import charset
H_,J_,A_,E_=charset(); CHARS=H_+J_+A_+E_
N='/usr/share/fonts/opentype/noto/'
KR=[(N+'NotoSansCJK-%s.ttc'%w,1) for w in ['Thin','Light','DemiLight','Regular','Medium','Bold','Black']]+\
   [(N+'NotoSerifCJK-%s.ttc'%w,1) for w in ['ExtraLight','Light','Regular','Medium','SemiBold','Bold','Black']]+\
   [(N+'NotoSansCJK-Regular.ttc',6),(N+'NotoSansCJK-Bold.ttc',6)]
D='/usr/share/fonts/truetype/'
LAT=[(D+'dejavu/DejaVuSans.ttf',0),(D+'dejavu/DejaVuSans-Bold.ttf',0),(D+'dejavu/DejaVuSerif.ttf',0),(D+'freefont/FreeSans.ttf',0),(D+'freefont/FreeSerif.ttf',0),(D+'freefont/FreeSansBold.ttf',0),
     (D+'crosextra/Carlito-Regular.ttf',0),(D+'crosextra/Carlito-Bold.ttf',0),(D+'crosextra/Caladea-Regular.ttf',0),(D+'dejavu/DejaVuSansMono.ttf',0),(D+'freefont/FreeMono.ttf',0)]
import glob
inter=sorted(glob.glob('/usr/share/fonts/**/Inter*Regular*.tt*',recursive=True)+glob.glob('/usr/share/fonts/**/Inter*Bold*.tt*',recursive=True))[:2]
LAT+= [(f,0) for f in inter]
REFS=['한국어가나다라','ABHEkdlhb','가나ABk다라hd']
def render(font,text,size):
    W=int(size*len(text)*1.6)+20; Hh=int(size*2.2)
    im=Image.new('L',(W,Hh),0); d=ImageDraw.Draw(im); base=int(size*1.5)
    d.text((10,base),text,fill=255,font=font,anchor='ls')
    return im
def boxes(font,text,size):
    # per-character ink boxes at a fixed baseline
    out=[]
    x=10; base=int(size*1.5)
    for ch in text:
        im=Image.new('L',(int(size*2.5),int(size*2.2)),0); d=ImageDraw.Draw(im); d.text((5,base),ch,fill=255,font=font,anchor='ls')
        a=np.asarray(im)>100; ys,xs=np.nonzero(a)
        if len(ys): out.append((ys.min(),ys.max()+1))
    return out
def ref(font,size,which):
    b=boxes(font,REFS[which],size); hs=[y1-y0 for y0,y1 in b]; mh=max(hs)
    tall=[(y0,y1) for (y0,y1) in b if y1-y0>=0.55*mh]
    T0=float(np.median([t for t,_ in tall])); B0=float(np.median([b_ for _,b_ in tall])); return T0,B0-T0
def sample(args):
    path,idx,chars,seed=args
    rnd=random.Random(seed); out=[]
    for size in (18,26,38):
        font=ImageFont.truetype(path,size,index=idx)
        refs=[ref(font,size,k) for k in range(3)]
        for ci,ch in chars:
            try: m=font.getmask(ch)
            except Exception: continue
            if m.size[0]==0: continue
            im=Image.new('L',(int(size*2.5),int(size*2.2)),0); d=ImageDraw.Draw(im); base=int(size*1.5); d.text((5,base),ch,fill=255,font=font,anchor='ls')
            for k in range(2):
                g=im
                if k==1:
                    sx=rnd.uniform(0.85,1.15); sh=rnd.uniform(-0.15,0.15)
                    g=g.transform(g.size,Image.AFFINE,(1/sx,sh,0,0,1,0),resample=Image.BILINEAR)
                if rnd.random()<0.5: g=g.filter(ImageFilter.GaussianBlur(rnd.uniform(0.3,0.9)))
                a=np.asarray(g).astype(np.float32)/255
                th=rnd.uniform(0.35,0.6); b=a>th
                if rnd.random()<0.15:
                    import scipy.ndimage as nd
                    b=nd.binary_dilation(b) if rnd.random()<0.5 else (nd.binary_erosion(b) if b.sum()>40 else b)
                ys,xs=np.nonzero(b)
                if len(ys)==0: continue
                y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
                T0,H0=refs[rnd.randrange(3)]
                jit=rnd.uniform(-0.04,0.04)*H0
                f=features(b[y0:y1,x0:x1].astype(np.float32),y0+jit,y1+jit,x0,x1,T0,H0)
                out.append((ci,f))
    return out
if __name__=='__main__':
    which=sys.argv[1]
    jobs=[]; seed=0
    idx=list(enumerate(CHARS))
    kr_idx=idx  # Korean fonts cover everything
    lat_idx=[(i,c) for i,c in idx if c in A_ or c in E_]
    if which in ('train','final'):
        fonts=[(p,i,kr_idx) for p,i in KR]+[(p,i,lat_idx) for p,i in LAT]
        if which=='final': fonts+=[('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',0,kr_idx),('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',2,kr_idx)]
    else:
        fonts=[('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',0,kr_idx)]
    for p,i,ch in fonts:
        for k in range(0,len(ch),300):
            seed+=1; jobs.append((p,i,ch[k:k+300],seed))
    with Pool(os.cpu_count()) as pool:
        res=pool.map(sample,jobs,chunksize=1)
    ys=np.array([c for r in res for c,_ in r],np.int32); X=np.stack([f for r in res for _,f in r]).astype(np.float32)
    np.save(which+'_X.npy',X); np.save(which+'_y.npy',ys); print(which,X.shape,len(set(ys.tolist())))
