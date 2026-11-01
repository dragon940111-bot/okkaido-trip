import json,os,sys
from PIL import Image,ImageDraw,ImageFont
P=json.load(open('photos.json'))
F=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',16,index=1)
items=[]
for card,lst in P.items():
    for k,f,s in lst:
        if k.startswith('n4_') and os.path.exists(f'img/{k}.jpg'): items.append((card,k))
cols=5; W=300; H=240
pages=[items[i:i+20] for i in range(0,len(items),20)]
for pi,pg in enumerate(pages):
    sh=Image.new('RGB',(cols*W,((len(pg)+cols-1)//cols)*H),'white'); d=ImageDraw.Draw(sh)
    for i,(card,k) in enumerate(pg):
        im=Image.open(f'img/{k}.jpg'); im.thumbnail((W-10,H-40))
        x,y=(i%cols)*W,(i//cols)*H
        sh.paste(im,(x+5,y+5)); d.text((x+5,y+H-32),(card[:14]+' '+k[3:])[:30],font=F,fill='black')
    sh.save(f'/tmp/claude-0/-home-claude/58f40eb2-f22c-5aa9-8b4e-f6f17c8a5199/scratchpad/sheet4_{pi}.jpg',quality=80)
    print('page',pi,len(pg))
