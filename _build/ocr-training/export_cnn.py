"""Export cnn.npz → ocr-net.bin + ocr-net.json (8-bit weights, one float scale per output)."""
import numpy as np, json, sys
from cnn import Net
p=dict(np.load(sys.argv[1] if len(sys.argv)>1 else 'cnn.npz'))
names=[('k1','b1'),('k2','b2'),('k3','b3'),('w4','b4'),('w5','b5')]
layers=[]; fl=[]; qs=[]; deq={}
for k,b in names:
    W=p[k].astype(np.float32); sc=np.abs(W).max(0)/127+1e-12
    q=np.clip(np.round(W/sc),-127,127).astype(np.int8)
    layers.append({'name':k,'rows':int(W.shape[0]),'cols':int(W.shape[1])})
    fl+=[sc.astype(np.float32),p[b].astype(np.float32)]; qs.append(q)
    deq[k]=(q.astype(np.float32)*sc).astype(np.float32); deq[b]=p[b]
buf=b''.join(a.tobytes() for a in fl)+b''.join(q.tobytes() for q in qs)
open((sys.argv[2] if len(sys.argv)>2 else 'out')+'/ocr-net.bin','wb').write(buf); json.dump({'layers':layers},open((sys.argv[2] if len(sys.argv)>2 else 'out')+'/ocr-net.json','w'))
print('bytes',len(buf))
va=np.load('val.npz'); Xv=va['X'][:20000].astype(np.float32)/255; Gv=va['G'][:20000]; Yv=va['Y'][:20000]
for tag,P in (('float',p),('int8',deq)):
    n=Net(int(p['b5'].shape[0])); n.p=P; ok=0
    for i in range(0,len(Xv),1000): o,_=n.forward(Xv[i:i+1000],Gv[i:i+1000]); ok+=(o.argmax(1)==Yv[i:i+1000]).sum()
    print(tag,'val acc',ok/len(Xv))
