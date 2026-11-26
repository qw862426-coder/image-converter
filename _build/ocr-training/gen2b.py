"""Single-glyph samples (v2): more Korean typefaces + accented letters; only characters each font has."""
import numpy as np, sys, os
from multiprocessing import Pool
import gen2
from fonts import KR_TRAIN, LAT_TRAIN, has
if __name__=='__main__':
    which=sys.argv[1]; per=int(sys.argv[2]); s=int(sys.argv[3])
    idx=list(enumerate(gen2.CHARS)); jobs=[]
    for p,i in KR_TRAIN+LAT_TRAIN:
        ch=[(ci,c) for ci,c in idx if has(p,i,c)]
        for k in range(0,len(ch),250): s+=1; jobs.append((p,i,ch[k:k+250],s,per))
    with Pool(2) as pool: res=pool.map(gen2.job,jobs,chunksize=2)
    X=np.stack([x for r in res for x in r[0]]); G=np.stack([g for r in res for g in r[1]]); Y=np.array([y for r in res for y in r[2]],np.int16)
    np.savez(which+'.npz',X=X,G=G,Y=Y); print(which,X.shape,len(set(Y.tolist())))
