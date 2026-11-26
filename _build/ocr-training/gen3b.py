"""Pages of text (made-up and real sentences) rendered like screenshots/scans/photos, with the box of every
character recorded, so the real reader can cut them up and each cut piece gets its true label."""
import numpy as np, sys, os, random, io, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from multiprocessing import Pool
from chars import charset
from fonts import KR_TRAIN, LAT_TRAIN, has
H_,J_,A_,E_=charset(); CHARS=H_+J_+A_+E_
C=json.load(open('corpus2_held.json'))
EUR=C['en']+C['de']+C['es']+C['fr']+C['pt']
LATC=A_+E_
# a few made-up word lists so Italian, Turkish, Polish and Vietnamese letters appear inside words
EXTRA_W=('perché città così più però già ciò università caffè '
 'güzel çocuk şehir ağaç öğrenci ılık gün değil yağmur kış '
 'zażółć gęślą jaźń łódź źródło mąka ćma żółw śnieg '
 'tiếng việt nhiều dấu thanh rất đẹp phức tạp người được không những trường học ở đây cũng vậy mình đã sẽ của').split()
def rand_line(rnd,latin):
    pool=LATC if latin else CHARS
    out=[]
    for k in range(rnd.randint(6,22)):
        w=''.join(rnd.choice(pool) for _ in range(rnd.randint(1,5)))
        if not latin and rnd.random()<0.3: w+=rnd.choice('.,!?:)')
        out.append(w)
    return ' '.join(out)
def text_line(rnd,latin):
    r=rnd.random()
    if latin:
        if r<0.55: s=rnd.choice(EUR); i=rnd.randint(0,max(0,len(s)-60)); return s[i:i+60]
        if r<0.8: return ' '.join(rnd.choice(EXTRA_W) for _ in range(rnd.randint(4,9)))
        return rand_line(rnd,True)
    if r<0.4: return rand_line(rnd,False)
    if r<0.85: s=rnd.choice(C['ko']); i=rnd.randint(0,max(0,len(s)-40)); return s[i:i+40]
    return rnd.choice(EUR)[:50]
def page(seed):
    rnd=random.Random(seed)
    latin=rnd.random()<0.3
    path,idx=rnd.choice(LAT_TRAIN+KR_TRAIN if latin else KR_TRAIN)
    size=rnd.choice([11,12,13,14,15,16,18,20,22,26,30,36])
    font=ImageFont.truetype(path,size,index=idx)
    lines=[text_line(rnd,latin) for _ in range(rnd.randint(4,9))]
    lines=[''.join(ch for ch in l if ch==' ' or has(path,idx,ch)) for l in lines]
    lines=[l for l in lines if l.strip()]
    lh=int(size*rnd.uniform(1.45,2.0)); W=int(max(font.getlength(l) for l in lines))+40; Hh=lh*len(lines)+30
    fg=rnd.randint(0,90); bg=rnd.randint(max(170,fg+100),255)
    im=Image.new('L',(W,Hh),bg); d=ImageDraw.Draw(im); boxes=[]
    for i,l in enumerate(lines):
        y=15+i*lh+int(size*1.1)
        d.text((20,y),l,fill=fg,font=font,anchor='ls')
        for j,ch in enumerate(l):
            if ch==' ': continue
            x0=20+font.getlength(l[:j]); x1=20+font.getlength(l[:j+1])
            bb=font.getbbox(ch,anchor='ls')
            boxes.append([x0,x1,y+bb[1],y+bb[3],CHARS.index(ch) if ch in CHARS else -1])
    a=np.asarray(im).astype(np.float32); sc=1.0
    if rnd.random()<0.35: im=Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.GaussianBlur(rnd.uniform(0.3,0.9))); a=np.asarray(im).astype(np.float32)
    if rnd.random()<0.25:  # photographed/scanned at lower resolution
        f=rnd.uniform(0.7,0.9); im=Image.fromarray(a.astype(np.uint8)).resize((int(W*f),int(Hh*f)),Image.BILINEAR); a=np.asarray(im).astype(np.float32); sc=f
    h2,w2=a.shape
    if rnd.random()<0.4:
        yy,xx=np.mgrid[0:h2,0:w2]; a=a*(0.8+0.2*np.cos((xx/w2-rnd.random())*2)*np.cos((yy/h2-rnd.random())*1.5))+rnd.uniform(0,20)
    if rnd.random()<0.5: a=a+np.random.default_rng(seed).normal(0,rnd.uniform(1,8),a.shape)
    a=np.clip(a,0,255).astype(np.uint8)
    if rnd.random()<0.3:
        buf=io.BytesIO(); Image.fromarray(a).save(buf,'JPEG',quality=rnd.randint(40,90)); a=np.asarray(Image.open(buf).convert('L'))
    if rnd.random()<0.12: a=255-a  # light text on dark background
    rgba=np.repeat(a[...,None],4,2).copy(); rgba[...,3]=255
    return rgba.tobytes(),w2,h2,[[b[0]*sc,b[1]*sc,b[2]*sc,b[3]*sc,b[4]] for b in boxes]
def job(args):
    start,n,out=args
    with open(out+'.bin','wb') as fb, open(out+'.json','w') as fj:
        meta=[]
        for s in range(start,start+n):
            try: b,w,h,boxes=page(s)
            except Exception as e: continue
            meta.append({'off':fb.tell(),'w':w,'h':h,'boxes':boxes}); fb.write(b)
        json.dump(meta,fj)
if __name__=='__main__':
    tag=sys.argv[1]; npages=int(sys.argv[2]); seed0=int(sys.argv[3]); os.makedirs('pages2',exist_ok=True)
    per=50; jobs=[(seed0+i,per,'pages2/%s_%04d'%(tag,i//per)) for i in range(0,npages,per)]
    with Pool(2) as p: p.map(job,jobs)
