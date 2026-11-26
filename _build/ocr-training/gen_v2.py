"""LDA training samples (v2): more Korean typefaces + accented letters; only characters each font really has."""
import numpy as np, sys, os
from multiprocessing import Pool
import gen
from fonts import KR_TRAIN, LAT_TRAIN, KR_HOLD, LAT_HOLD, has
CH=list(enumerate(gen.CHARS))
if __name__=='__main__':
    which=sys.argv[1]
    fonts=KR_TRAIN+LAT_TRAIN if which=='train' else KR_HOLD+LAT_HOLD
    jobs=[]; seed=1000 if which=='train' else 5000
    for p,i in fonts:
        chs=[(ci,c) for ci,c in CH if has(p,i,c)]
        for k in range(0,len(chs),300): seed+=1; jobs.append((p,i,chs[k:k+300],seed))
    print('jobs',len(jobs),flush=True)
    with Pool(2) as pool: res=pool.map(gen.sample,jobs,chunksize=1)
    n=sum(len(r) for r in res); X=np.lib.format.open_memmap(which+'2_X.npy','w+',np.float32,(n,516)); ys=np.zeros(n,np.int32); o=0
    for r in res:
        for c,f in r: X[o]=f; ys[o]=c; o+=1
    X.flush(); np.save(which+'2_y.npy',ys); print(which,n,len(set(ys.tolist())))
