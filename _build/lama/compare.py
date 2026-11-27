import numpy as np, onnxruntime as ort, time, sys
from PIL import Image
img=np.asarray(Image.open('../inp/clean.png').convert('RGB')).astype(np.float32); mk=np.asarray(Image.open('../inp/mask.png'))>127
H,W=mk.shape; ys,xs=np.where(mk); bx0,bx1,by0,by1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
side=max(max(bx1-bx0,by1-by0)*2,min(512,W,H)); rw=int(min(side,W)); rh=int(min(side,H))
rx=int(min(max((bx0+bx1)/2-rw/2,0),W-rw)); ry=int(min(max((by0+by1)/2-rh/2,0),H-rh))
N=512
crop=Image.fromarray(img[ry:ry+rh,rx:rx+rw].astype(np.uint8)).resize((N,N),Image.BICUBIC); c=np.asarray(crop).astype(np.float32)
m=np.asarray(Image.fromarray((mk[ry:ry+rh,rx:rx+rw]*255).astype(np.uint8)).resize((N,N),Image.BILINEAR))>8
from scipy.ndimage import binary_dilation
R=max(4,round(N*0.012)); yy,xx=np.mgrid[-R:R+1,-R:R+1]; m=binary_dilation(m,structure=(xx*xx+yy*yy)<=R*R)
truth=np.asarray(Image.fromarray(img[ry:ry+rh,rx:rx+rw].astype(np.uint8)).resize((N,N),Image.BICUBIC)).astype(np.float32)
res={}
s=ort.InferenceSession('../migan/migan.onnx'); k=1-m
inp=np.concatenate([(0.5-m)[None],(c.transpose(2,0,1)/127.5-1)*k[None]],0)[None].astype(np.float32)
t=time.time(); o=s.run(None,{s.get_inputs()[0].name:inp})[0][0]; res['MI-GAN']=(np.clip(o.transpose(1,2,0)*0.5+0.5,0,1)*255,time.time()-t)
for f in sys.argv[1:]:
    s=ort.InferenceSession(f); t=time.time()
    o=s.run(None,{'img':(c.transpose(2,0,1)/255)[None].astype(np.float32),'mask':m[None,None].astype(np.float32)})[0][0]
    res[f]=(np.clip(o.transpose(1,2,0),0,1)*255,time.time()-t)
tiles=[c*(1-m[...,None])+255*m[...,None]*np.array([1,0,1]),truth]
for k_,(o,dt) in res.items():
    e=np.abs(o-truth)[m].mean(); print('%-20s error in hole %.1f  time %.1fs'%(k_,e,dt)); tiles.append(o)
Image.fromarray(np.concatenate(tiles,1).astype(np.uint8)).resize((256*len(tiles),256)).save('cmp.png')
