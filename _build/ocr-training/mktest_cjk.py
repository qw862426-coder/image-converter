"""Test images for the Japanese / Chinese readers (own sentences, not from the site text)."""
import numpy as np, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cjk
T={'ja':["明日の会議は午前十時から三階の会議室で行います。","この商品は送料無料でお届けします。","駅から歩いて五分の場所にあります。",
         "パスワードを忘れた場合は、こちらから再設定してください。","価格：1,280円（税込）","雨の日は電車が遅れることがあります。"],
   'zh':["明天上午十点在三楼会议室开会。","这个商品免运费，三天内送到。","从车站步行五分钟就能到达。",
         "如果忘记密码，请点击这里重新设置。","价格：128元（含税）","下雨天地铁可能会晚点。"]}
for lang in ['ja','zh']:
    tr,ho=cjk.fonts(lang); meta=[]
    for name,(path,idx),size,photo in [('hold22',ho[0],22,False),('hold15',ho[0],15,False),('holdB18',ho[-1],18,True),('noto20',tr[3],20,False),('serif16',tr[9],16,False)]:
        font=ImageFont.truetype(path,size,index=idx); texts=T[lang]
        W=max(int(font.getlength(t)) for t in texts)+40; lh=int(size*1.7); H=lh*len(texts)+30
        im=Image.new('RGB',(W,H),(255,255,255)); d=ImageDraw.Draw(im)
        for i,t in enumerate(texts): d.text((20,15+i*lh),t,fill=(20,20,20),font=font)
        if photo:
            a=np.asarray(im).astype(np.float32); yy,xx=np.mgrid[0:H,0:W]; light=0.75+0.25*np.cos((xx/W-0.3)*2)*np.cos((yy/H-0.5)*1.5)
            a=a*light[...,None]*0.9+15; a+=np.random.default_rng(0).normal(0,6,a.shape)
            im=Image.fromarray(np.clip(a,0,255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7))
        n='t%s_%s'%(lang,name); im.save(n+'.png'); np.asarray(im.convert('RGBA')).tofile(n+'.rgba')
        meta.append({'name':n,'w':W,'h':H,'texts':texts})
    json.dump({'cases':meta,'texts':[]},open('tests_%s.json'%lang,'w'),ensure_ascii=False)
print('ok')
