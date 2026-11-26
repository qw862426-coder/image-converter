import numpy as np, json, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
N='/usr/share/fonts/opentype/noto/'
texts=["대한민국은 민주공화국이다. 모든 권력은 국민으로부터 나온다.",
"오늘 회의는 오후 3시에 2층 회의실에서 진행됩니다.",
"사진을 PDF로 바꾸는 무료 도구 PicShifter를 사용해 보세요!",
"가격: 12,500원 (부가세 포함) / 배송비 3,000원",
"The quick brown fox jumps over the lazy dog 1234567890.",
"고객님의 주문이 정상적으로 접수되었습니다. 감사합니다."]
cases=[('sans24',N+'NotoSansCJK-Regular.ttc',1,24,False),('sans16',N+'NotoSansCJK-Regular.ttc',1,16,False),('serif24',N+'NotoSerifCJK-Regular.ttc',1,24,False),('bold20',N+'NotoSansCJK-Bold.ttc',1,20,False),('wqy22',"/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",0,22,False),('photo24',N+'NotoSansCJK-Medium.ttc',1,24,True),('sans13',N+'NotoSansCJK-Regular.ttc',1,13,False),('serif14',N+'NotoSerifCJK-Regular.ttc',1,14,False)]
meta=[]
for name,path,idx,size,photo in cases:
    font=ImageFont.truetype(path,size,index=idx)
    W=max(int(font.getlength(t)) for t in texts)+40; lh=int(size*1.7); H=lh*len(texts)+30
    im=Image.new('RGB',(W,H),(255,255,255)); d=ImageDraw.Draw(im)
    for i,t in enumerate(texts): d.text((20,15+i*lh),t,fill=(20,20,20),font=font)
    if photo:
        a=np.asarray(im).astype(np.float32)
        yy,xx=np.mgrid[0:H,0:W]; light=0.75+0.25*np.cos((xx/W-0.3)*2)*np.cos((yy/H-0.5)*1.5)
        a=a*light[...,None]*0.9+15; a+=np.random.default_rng(0).normal(0,6,a.shape)
        im=Image.fromarray(np.clip(a,0,255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7))
    im.save(name+'.png'); np.asarray(im.convert('RGBA')).tofile(name+'.rgba')
    meta.append({'name':name,'w':W,'h':H})
json.dump({'cases':meta,'texts':texts},open('tests.json','w'),ensure_ascii=False)
