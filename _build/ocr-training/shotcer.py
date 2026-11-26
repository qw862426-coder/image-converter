import re,sys
from corpus import clean
def ed(a,b):
    prev=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        cur=[i]+[0]*len(b)
        for j,cb in enumerate(b,1): cur[j]=min(prev[j]+1,cur[j-1]+1,prev[j-1]+(ca!=cb))
        prev=cur
    return prev
if __name__=='__main__':
    t=re.sub(r'\s+','',''.join(clean('/home/claude/image-converter/_build/posts/ko/heic-photos-wont-open.html')))
    for f in sys.argv[1:]:
        o=open(f).read(); o=re.sub(r'\s+','',o[o.find('왜 안'):])
        row=ed(t,o)  # truth vs output prefix: allow output to run past the truth end
        e=min(row); print(f,'truth chars',len(t),'errors',e,'CER %.1f%%'%(100*e/len(t)))
