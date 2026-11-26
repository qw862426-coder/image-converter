"""Training material for the Japanese / Chinese readers.
  python3 gen_cjk.py ja lda train|hold      -> ja_lda_train_X.npy / _y.npy
  python3 gen_cjk.py ja glyph <per> <seed>  -> ja_glyph.npz   (single letters for the network)"""
import numpy as np, sys
from multiprocessing import Pool
import gen, gen2, cjk
from fonts import has
lang,mode=sys.argv[1],sys.argv[2]
gen.REFS=cjk.REFS[lang]
CH=list(enumerate(cjk.charset(lang)))
if __name__=='__main__':
    tr,ho=cjk.fonts(lang)
    if mode=='lda':
        which=sys.argv[3]; fonts=tr if which=='train' else ho; jobs=[]; seed=7000 if which=='train' else 9000
        for p,i in fonts:
            chs=[(ci,c) for ci,c in CH if has(p,i,c)]
            for k in range(0,len(chs),300): seed+=1; jobs.append((p,i,chs[k:k+300],seed))
        with Pool(2) as pool: res=pool.map(gen.sample,jobs,chunksize=1)
        n=sum(len(r) for r in res); X=np.lib.format.open_memmap('%s_lda_%s_X.npy'%(lang,which),'w+',np.float32,(n,516)); ys=np.zeros(n,np.int32); o=0
        for r in res:
            for c,f in r: X[o]=f; ys[o]=c; o+=1
        X.flush(); np.save('%s_lda_%s_y.npy'%(lang,which),ys); print(lang,which,n,len(set(ys.tolist())))
    else:
        per=int(sys.argv[3]); s=int(sys.argv[4]); jobs=[]
        for p,i in tr:
            ch=[(ci,c) for ci,c in CH if has(p,i,c)]
            for k in range(0,len(ch),250): s+=1; jobs.append((p,i,ch[k:k+250],s,per))
        with Pool(2) as pool: res=pool.map(gen2.job,jobs,chunksize=2)
        X=np.stack([x for r in res for x in r[0]]); G=np.stack([g for r in res for g in r[1]]); Y=np.array([y for r in res for y in r[2]],np.int16)
        np.savez('%s_glyph.npz'%lang,X=X,G=G,Y=Y); print(lang,'glyph',X.shape,len(set(Y.tolist())))
