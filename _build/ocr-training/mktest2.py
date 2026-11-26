"""Test set 2: typefaces the reader never trained on (Wanted Sans, TeX Gyre Adventor) and European/Vietnamese text."""
import numpy as np, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from fonts import KR_HOLD, LAT_HOLD
KO=["내일 아침 아홉 시까지 보고서를 제출해 주세요.","이번 주말에는 비가 많이 올 예정이니 우산을 챙기세요.","회원 가입을 완료하면 첫 구매 할인 쿠폰을 드립니다.",
    "배터리가 20% 이하로 떨어지면 절전 모드가 켜집니다.","서울특별시 강남구 테헤란로 123, 4층","문의: 02-1234-5678 (평일 오전 10시~오후 6시)"]
EU=["Größere Häuser kosten mehr, aber die Straße ist ruhig.","Le garçon a mangé une crème brûlée à la fenêtre.","¿Dónde está la estación? ¡Mañana llegará el niño!",
    "A informação não está disponível; ação imediata é necessária.","Perché la città è così più bella in autunno?","Güzel bir gün; çocuklar şehirde ağaç dikiyor.",
    "Zażółć gęślą jaźń, łódź płynie po rzece.","Tiếng Việt có nhiều dấu thanh, rất đẹp và phức tạp."]
DV='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
cases=[('ko_wanted22',KR_HOLD[0],22,KO,False),('ko_wanted15',KR_HOLD[0],15,KO,False),('ko_wantedB18',KR_HOLD[1],18,KO,True),
       ('eu_adventor22',LAT_HOLD[0],22,EU,False),('eu_adventor15',LAT_HOLD[0],15,EU,False),('eu_dejavu18',(DV,0),18,EU,True)]
meta=[]
for name,(path,idx),size,texts,photo in cases:
    font=ImageFont.truetype(path,size,index=idx)
    W=max(int(font.getlength(t)) for t in texts)+40; lh=int(size*1.7); H=lh*len(texts)+30
    im=Image.new('RGB',(W,H),(255,255,255)); d=ImageDraw.Draw(im)
    for i,t in enumerate(texts): d.text((20,15+i*lh),t,fill=(20,20,20),font=font)
    if photo:
        a=np.asarray(im).astype(np.float32); yy,xx=np.mgrid[0:H,0:W]; light=0.75+0.25*np.cos((xx/W-0.3)*2)*np.cos((yy/H-0.5)*1.5)
        a=a*light[...,None]*0.9+15; a+=np.random.default_rng(0).normal(0,6,a.shape)
        im=Image.fromarray(np.clip(a,0,255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7))
    im.save('t2_'+name+'.png'); np.asarray(im.convert('RGBA')).tofile('t2_'+name+'.rgba')
    meta.append({'name':'t2_'+name,'w':W,'h':H,'texts':texts})
json.dump({'cases':meta,'texts':[]},open('tests2.json','w'),ensure_ascii=False)
