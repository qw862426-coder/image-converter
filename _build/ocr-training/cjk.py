"""Character lists and fonts for the Japanese and Chinese readers (separate models, picked on the page)."""
import os
F=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','fonts'))
N='/usr/share/fonts/opentype/noto/'; WQ='/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
SANS=['Thin','Light','DemiLight','Regular','Medium','Bold','Black']; SERIF=['ExtraLight','Light','Regular','Medium','SemiBold','Bold','Black']
ASCII=[chr(c) for c in range(33,127)]
def _euc(enc,rows):
    out=[]
    for hi in rows:
        for lo in range(0xA1,0xFF):
            try:
                c=bytes([hi,lo]).decode(enc)
                if len(c)==1: out.append(c)
            except Exception: pass
    return out
def charset(lang):
    if lang=='ja':
        kana=[chr(c) for c in range(0x3041,0x3097)]+[chr(c) for c in range(0x30A1,0x30FB)]+['ー']
        kanji=_euc('euc_jp',range(0xB0,0xD0))            # JIS X 0208 level 1: 2,965 common kanji
        punct=list('、。「」『』【】（）！？：・〜…※→←↑↓○●□■△▲☆★〒々〆￥')
    else:
        kana=[]
        kanji=_euc('gb2312',range(0xB0,0xD8))           # GB2312 level 1: 3,755 common hanzi
        punct=list('，。、；：？！“”‘’（）《》【】「」—…·￥※→←↑↓○●□■△▲☆★')
    out=[]; seen=set()
    for c in kanji+kana+ASCII+punct:
        if c not in seen: seen.add(c); out.append(c)
    return out
def fonts(lang):
    if lang=='ja':
        train=[(N+'NotoSansCJK-%s.ttc'%w,0) for w in SANS]+[(N+'NotoSerifCJK-%s.ttc'%w,0) for w in SERIF]+\
              [(F+'/x_plexjp/ibm-plex-sans-jp/fonts/complete/ttf/unhinted/IBMPlexSansJP-%s.ttf'%w,0) for w in ['Light','Regular','Medium','SemiBold','Bold']]+\
              [(F+'/x_wenkai/lxgw-wenkai-v1.330/LXGWWenKai-Regular.ttf',0)]
        hold=[(F+'/x_bizud/morisawa-biz-ud-gothic-fonts/fonts/ttf/BIZUDGothic-Regular.ttf',0),(F+'/x_bizud/morisawa-biz-ud-gothic-fonts/fonts/ttf/BIZUDGothic-Bold.ttf',0)]
    else:
        train=[(N+'NotoSansCJK-%s.ttc'%w,2) for w in SANS]+[(N+'NotoSerifCJK-%s.ttc'%w,2) for w in SERIF]+[(WQ,0),(WQ,2)]+\
              [(F+'/x_plexsc/ibm-plex-sans-sc/fonts/complete/ttf/unhinted/IBMPlexSansSC-%s.ttf'%w,0) for w in ['Light','Regular','Medium','SemiBold','Bold']]+\
              [(F+'/x_wenkai/lxgw-wenkai-v1.330/LXGWWenKai-Regular.ttf',0)]
        hold=[(F+'/neoxihei.ttf',0)]
    return train,hold
REFS={'ja':['日本語の文字','ABHEkdlhb','日本ABk語hd'],'zh':['中文汉字测试','ABHEkdlhb','中文ABk汉hd']}
if __name__=='__main__':
    from fonts import covers
    for lang in ['ja','zh']:
        cs=charset(lang); tr,ho=fonts(lang); print(lang,'chars',len(cs))
        for p,i in tr+ho:
            assert os.path.exists(p),p
            c=covers(p,i); print('  ',os.path.basename(p),i,sum(ord(x) in c for x in cs),'/',len(cs))
