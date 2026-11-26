"""Font lists for training (v2: more Korean typefaces) and which characters each font really has."""
import os
from fontTools.ttLib import TTFont
F=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','fonts'))
N='/usr/share/fonts/opentype/noto/'; D='/usr/share/fonts/truetype/'; TG='/usr/share/texmf/fonts/opentype/public/tex-gyre/'
NOTO=[(N+'NotoSansCJK-%s.ttc'%w,1) for w in ['Thin','Light','DemiLight','Regular','Medium','Bold','Black']]+\
     [(N+'NotoSerifCJK-%s.ttc'%w,1) for w in ['ExtraLight','Light','Regular','Medium','SemiBold','Bold','Black']]+\
     [(N+'NotoSansCJK-Regular.ttc',6),(N+'NotoSansCJK-Bold.ttc',6)]
WQY=[(D+'wqy/wqy-zenhei.ttc',0),(D+'wqy/wqy-zenhei.ttc',2)]
PRET=[(F+'/x_pretendard/public/static/alternative/Pretendard-%s.ttf'%w,0) for w in ['Light','Regular','Medium','SemiBold','Bold','ExtraBold']]
PLEX=[(F+'/x_plex/ibm-plex-sans-kr/fonts/complete/ttf/unhinted/IBMPlexSansKR-%s.ttf'%w,0) for w in ['Light','Regular','Medium','SemiBold','Bold']]
SPOQA=[(F+'/x_spoqa/SpoqaHanSansNeo_all/SpoqaHanSansNeo_TTF_original/SpoqaHanSansNeo-%s.ttf'%w,0) for w in ['Light','Regular','Medium','Bold']]
D2=[(F+'/x_d2coding/D2Coding/D2Coding-Ver1.3.2-20180524.ttf',0),(F+'/x_d2coding/D2Coding/D2CodingBold-Ver1.3.2-20180524.ttf',0)]
KR_TRAIN=NOTO+WQY+PRET+PLEX+SPOQA+D2
LAT_TRAIN=[(D+'dejavu/DejaVuSans.ttf',0),(D+'dejavu/DejaVuSans-Bold.ttf',0),(D+'dejavu/DejaVuSerif.ttf',0),(D+'freefont/FreeSans.ttf',0),(D+'freefont/FreeSerif.ttf',0),
     (D+'freefont/FreeSansBold.ttf',0),(D+'crosextra/Carlito-Regular.ttf',0),(D+'crosextra/Carlito-Bold.ttf',0),(D+'crosextra/Caladea-Regular.ttf',0),
     (D+'dejavu/DejaVuSansMono.ttf',0),(D+'freefont/FreeMono.ttf',0),('/usr/share/fonts/opentype/inter/Inter-Regular.otf',0),('/usr/share/fonts/opentype/inter/Inter-Bold.otf',0)]+\
     [(TG+'texgyre%s-%s.otf'%(n,w),0) for n in ['heros','termes','pagella','bonum','schola'] for w in ['regular','bold']]
# kept out of training: used only to test typefaces the reader has never seen
KR_HOLD=[(F+'/x_wanted/ttf/WantedSans-%s.ttf'%w,0) for w in ['Regular','Bold']]
LAT_HOLD=[(TG+'texgyreadventor-regular.otf',0),(TG+'texgyreadventor-bold.otf',0)]
_cov={}
def covers(path,idx):
    k=(path,idx)
    if k not in _cov:
        f=TTFont(path,fontNumber=idx,lazy=True); _cov[k]=set(f.getBestCmap().keys()); f.close()
    return _cov[k]
def has(path,idx,ch): return ord(ch) in covers(path,idx)
if __name__=='__main__':
    from chars import charset
    H,J,A,E=charset(); allc=H+J+A+E
    for p,i in KR_TRAIN+LAT_TRAIN+KR_HOLD+LAT_HOLD:
        assert os.path.exists(p),p
        c=covers(p,i); print(os.path.basename(p),i,'hangul',sum(ord(x) in c for x in H),'other',sum(ord(x) in c for x in A+E),'/',len(A+E))
