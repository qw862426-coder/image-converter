import numpy as np, onnxruntime as ort, time, sys
from PIL import Image
import skimage.data as sd
imgs={'astronaut':sd.astronaut(),'cat':sd.chelsea(),'coffee':sd.coffee(),'rocket':sd.rocket(),'hopper':np.asarray(Image.open('/usr/local/lib/python3.13/dist-packages/matplotlib/mpl-data/sample_data/grace_hopper.jpg').convert('RGB')),'moto':sd.stereo_motorcycle()[0]}
def prep(im,S,mean,std):
    x=np.asarray(Image.fromarray(im).resize((S,S),Image.BILINEAR)).astype(np.float32)/255
    if mean=='max': x=x/max(x.max(),1e-6); mean,std=(0.485,0.456,0.406),(0.229,0.224,0.225)
    return ((x-np.array(mean))/np.array(std)).transpose(2,0,1)[None].astype(np.float32)
MODELS={'silueta (now)':('silueta.onnx',320,'max',None,False),'ISNet':('isnet-general-use.onnx',1024,(0.5,0.5,0.5),(1,1,1),False)}
def chk(h,w):
    yy,xx=np.mgrid[0:h,0:w]; return np.where(((yy//16+xx//16)%2)[...,None],200,255).astype(np.float32)*np.ones(3)
rows=[]
SESS={mn:ort.InferenceSession(v[0]) for mn,v in MODELS.items()}
for name,im in imgs.items():
    h,w=im.shape[:2]; row=[im.astype(np.float32)]
    for mn,(f,S,mean,std,sig) in MODELS.items():
        s=SESS[mn]; t=time.time(); o=s.run(None,{s.get_inputs()[0].name:prep(im,S,mean,std)})[0][0,0]; dt=time.time()-t
        if sig: o=1/(1+np.exp(-o))
        o=(o-o.min())/(o.max()-o.min()+1e-8)
        a=np.asarray(Image.fromarray((o*255).astype(np.uint8)).resize((w,h),Image.BILINEAR)).astype(np.float32)[...,None]/255
        row.append(im*a+chk(h,w)*(1-a)); print(name,mn,'%.1fs'%dt)
    rows.append(np.concatenate([np.asarray(Image.fromarray(r.astype(np.uint8)).resize((300,int(300*h/w)))) for r in row],1))
W=max(r.shape[1] for r in rows); Image.fromarray(np.concatenate([np.pad(r,((0,4),(0,W-r.shape[1]),(0,0)),constant_values=255) for r in rows],0)).save('cmp.png')
