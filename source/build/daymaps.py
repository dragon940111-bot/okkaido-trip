import math,os,subprocess,json,time
from PIL import Image,ImageDraw,ImageFont,ImageEnhance
from pts import P
G=json.load(open('geo2.json'))
for k,v in G.items(): P[k]=tuple(v)
P['okina']=(42.4602,140.8893); P['lakehill']=(42.6138,140.7856); P['takikawa']=(43.5580,141.9080)
P['jigoku']=(42.4962,141.1460)
FB='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def font(sz): return ImageFont.truetype(FB,sz,index=1)
SYM=lambda sz: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',sz)
COL={1:(232,89,12),2:(28,126,214),3:(47,158,68),4:(156,54,181),5:(73,80,87),'A':(200,120,0),'B':(0,128,140),'D':(162,62,98),'E':(94,122,30),'F':(61,111,176),'G':(156,74,26)}
def px(lat,lon,z):
    n=256*2**z; x=(lon+180)/360*n
    y=(1-math.log(math.tan(math.radians(lat))+1/math.cos(math.radians(lat)))/math.pi)/2*n
    return x,y
def tile(z,x,y):
    p=f'tiles/{z}_{x}_{y}.png'
    if not os.path.exists(p) or os.path.getsize(p)<100:
        subprocess.run(['curl','-s','-A','HokkaidoTripPlanner/1.0 (personal one-off map)','-o',p,f'https://tile.openstreetmap.org/{z}/{x}/{y}.png']); time.sleep(0.12)
    return Image.open(p).convert('RGB')
def route(seq):
    coords=';'.join(f'{P[k][1]},{P[k][0]}' for k in seq)
    r=json.loads(subprocess.run(['curl','-s',f'https://router.project-osrm.org/route/v1/driving/{coords}?overview=full&geometries=geojson'],capture_output=True,text=True).stdout)
    rt=r['routes'][0]; time.sleep(1)
    return rt['geometry']['coordinates'],round(rt['distance']/1000),[round(l['duration']/60) for l in rt['legs']]
def render(name,col,seq,stops,title,extra=None,hollow=()):
    geom,km,legs=route(seq)
    lats=[c[1] for c in geom]+[P[k][0] for k,_,_ in stops]; lons=[c[0] for c in geom]+[P[k][1] for k,_,_ in stops]
    la0,la1,lo0,lo1=min(lats),max(lats),min(lons),max(lons)
    for z in range(13,7,-1):
        x0,y0=px(la1,lo0,z); x1,y1=px(la0,lo1,z)
        if (x1-x0)*1.22<=1500 and (y1-y0)*1.3<=1050: break
    padx=max((x1-x0)*0.12,60); pady=max((y1-y0)*0.15,70)
    W=max(x1-x0+2*padx,1150); H=max(y1-y0+2*pady,720)
    cx,cy=(x0+x1)/2,(y0+y1)/2; X0,Y0=cx-W/2,cy-H/2
    tx0,ty0,tx1,ty1=int(X0//256),int(Y0//256),int((X0+W)//256),int((Y0+H)//256)
    im=Image.new('RGB',((tx1-tx0+1)*256,(ty1-ty0+1)*256))
    for tx in range(tx0,tx1+1):
        for ty in range(ty0,ty1+1): im.paste(tile(z,tx,ty),((tx-tx0)*256,(ty-ty0)*256))
    ox,oy=X0-tx0*256,Y0-ty0*256
    im=im.crop((int(ox),int(oy),int(ox+W),int(oy+H)))
    im=ImageEnhance.Color(im).enhance(0.5); im=Image.blend(im,Image.new('RGB',im.size,(255,255,255)),0.25)
    f=lambda lat,lon:(px(lat,lon,z)[0]-X0,px(lat,lon,z)[1]-Y0)
    dr=ImageDraw.Draw(im,'RGBA')
    pts=[f(la,lo) for lo,la in geom]
    dr.line(pts,fill=(255,255,255),width=12,joint='curve'); dr.line(pts,fill=col,width=7,joint='curve')
    if extra:  # dashed subway line
        a,b,lbl=extra; xa,ya=f(*P[a]); xb,yb=f(*P[b]); n=14
        for i in range(n):
            if i%2==0: dr.line((xa+(xb-xa)*i/n,ya+(yb-ya)*i/n,xa+(xb-xa)*(i+1)/n,ya+(yb-ya)*(i+1)/n),fill=(201,42,42),width=5)
        dr.text(((xa+xb)/2+12,(ya+yb)/2),lbl,font=font(20),fill=(150,30,30),stroke_width=4,stroke_fill=(255,255,255),anchor='lm')
    for k,t in hollow:
        x,y=f(*P[k]); dr.ellipse((x-12,y-12,x+12,y+12),outline=(90,90,90),width=4,fill=(255,255,255))
        dr.text((x+20,y),t,font=font(21),fill=(90,90,90),stroke_width=4,stroke_fill=(255,255,255),anchor='lm')
    for k in ('airport','lodging'):
        if k in seq or k in [s[0] for s in stops]:
            x,y=f(*P[k]); r=19; c=(16,42,92) if k=='airport' else (201,42,42)
            dr.ellipse((x-r-4,y-r-4,x+r+4,y+r+4),fill=(255,255,255)); dr.ellipse((x-r,y-r,x+r,y+r),fill=c)
            dr.text((x,y+1),'✈' if k=='airport' else '★',font=SYM(26),fill=(255,255,255),anchor='mm')
            if k=='lodging': dr.text((x-30,y-24),'숙소',font=font(26),fill=(201,42,42),stroke_width=4,stroke_fill=(255,255,255),anchor='rm')
    boxes=[]
    for k,num,t in stops:
        x,y=f(*P[k])
        if k=='airport': x+=34; y+=30
        boxes.append((x-22,y-22,x+22,y+22))
    for k in ('airport','lodging'):
        if k in seq: x,y=f(*P[k]); boxes.append((x-26,y-26,x+26,y+26))
    def hit(b):
        return any(not(b[2]<o[0] or b[0]>o[2] or b[3]<o[1] or b[1]>o[3]) for o in boxes)
    FT=font(26)
    for k,num,t in stops:
        x,y=f(*P[k]); r=19
        if k=='airport': x+=34; y+=30
        dr.ellipse((x-r-3,y-r-3,x+r+3,y+r+3),fill=(255,255,255)); dr.ellipse((x-r,y-r,x+r,y+r),fill=col)
        dr.text((x,y+1),num,font=font(22),fill=(255,255,255),anchor='mm')
        tw=FT.getlength(t); th=30
        cands=[(x+28,y,'lm'),(x-28,y,'rm'),(x+22,y-34,'lm'),(x+22,y+34,'lm'),(x-22,y-34,'rm'),(x-22,y+34,'rm'),(x+30,y-62,'lm'),(x+30,y+62,'lm'),(x-30,y-62,'rm'),(x-30,y+62,'rm')]
        W_,H_=im.size; best=None
        for cx,cy,an in cands:
            b=(cx,cy-th/2,cx+tw,cy+th/2) if an=='lm' else (cx-tw,cy-th/2,cx,cy+th/2)
            if b[0]<4 or b[2]>W_-4 or b[1]<70 or b[3]>H_-24: continue
            if not hit(b): best=(cx,cy,an,b); break
        if not best:
            cx,cy,an=cands[0]; best=(cx,cy,an,(cx,cy-th/2,cx+tw,cy+th/2))
        cx,cy,an,b=best; boxes.append(b)
        if abs(cy-y)>40: dr.line((x,y,cx,cy),fill=col,width=2)
        dr.text((cx,cy),t,font=FT,fill=(20,20,20),stroke_width=5,stroke_fill=(255,255,255),anchor=an)
    tw=font(30).getlength(title)
    dr.rounded_rectangle((14,14,14+tw+36,66),radius=10,fill=(255,255,255,235))
    dr.text((32,40),title,font=font(30),fill=col,anchor='lm')
    w,h=im.size
    dr.text((w-12,h-10),'© OpenStreetMap contributors',font=font(14),fill=(80,80,80),anchor='rd',stroke_width=2,stroke_fill=(255,255,255))
    im.save(f'site/map/{name}.jpg',quality=80,optimize=True,progressive=True)
    print(name,z,im.size,km,'km',legs,os.path.getsize(f'site/map/{name}.jpg'))
    return km,legs
res={}
import sys
ONLY=sys.argv[1:]
_r=render
def render(name,*a,**k):
    if ONLY and name not in ONLY: return None
    return _r(name,*a,**k)
res['d1']=render('d1',COL[1],['airport','jnet','minato','shikotsu','via_453','chakkaru','kitaro','lodging'],[('airport','1','공항 디저트'),('jnet','2','Jnet 렌터카'),('minato','3','미나토 식당 (카이센동)'),('shikotsu','4','시코쓰호 산책'),('chakkaru','5','찻카루 (커피)'),('kitaro','6','기타로 (수프카레)'),('shirokuma','7','시로쿠마 (야식 · 지하철)')],'11/2 월 · 공항 → 도마코마이 → 시코쓰호 → 삿포로',extra=('lodging','shirokuma',''))
res['d2']=render('d2',COL[2],['lodging','saimi','daibutsu','pathos','soyogi','lodging'],[('saimi','1','멘야 사이미 (미소라멘)'),('daibutsu','2','두대불'),('pathos','3','르타오 파토스'),('canal','4','오타루 운하'),('soyogi','5','덴푸라 소요기'),('gurumans','6','야식 구루만즈 이토 (야키니쿠)')],'11/3 화 · 삿포로 남쪽 → 오타루 · 야식은 지하철',extra=('lodging','gurumans','지하철 南北線 8분'))
P['via_tmk']=(42.6420,141.5600)
res['d3']=render('d3',COL[3],['lodging','via_tmk','okina','lakehill','usuzan','jigoku','bibi','lodging'],[('okina','1','다테 오키나 (소바)'),('lakehill','2','레이크힐 팜'),('usuzan','3','쇼와신잔 · 우스잔 (자유시간)'),('jigoku','4','지옥계곡 · 온천가 (자유시간)'),('bibi','5','로그하우스 비비 (와규)')],'11/4 수 · 남쪽 루프',hollow=[('chikyu','지구곶 (옵션)')])
res['d4']=render('d4',COL[4],['lodging','tenkin','asahidake','shirahige','bluepond','shikisai','takikawa','lodging'],[('tenkin','1','덴킨 (라멘)'),('asahidake','2','아사히다케 로프웨이'),('shirahige','3','시라히게 폭포'),('bluepond','4','아오이이케'),('shikisai','5','시키사이노오카 (일몰)')],'11/5 목 · 북쪽 설경 → 저녁은 삿포로 스시')
res['d5']=render('d5',COL[5],['lodging','jnet','airport'],[('jnet','1','주유 · Jnet 반납'),('airport','2','공항 · 이치겐 라멘')],'11/6 금 · 출국')
res['sa']=render('sa',COL['A'],['lodging','shirakaba','kofuku','manabe','rokkatei','lodging'],[('shirakaba','1','시라카바 징기스칸'),('kofuku','2','고후쿠역'),('manabe','3','마나베 정원'),('rokkatei','4','롯카테이 · 판초 부타동')],'대안 A · 11/3 오비히로')
res['sb']=render('sb',COL['B'],['lodging','kurodake','asahishoku','daikokuya','lodging'],[('kurodake','1','구로다케 로프웨이 · 긴가 폭포'),('asahishoku','2','아사히 식당 (가미카와)'),('daikokuya','3','다이코쿠야 징기스칸')],'대안 B · 11/5 소운쿄',hollow=[('asahidake','아사히다케 (옵션)')])
res['sd']=render('sd',COL['D'],['lodging','fukidashi','jin','makkarina','takahashi','lodging'],[('fukidashi','1','교고쿠 후키다시 공원'),('jin','2','불랑제리 진'),('makkarina','3','레스토랑 맛카리나'),('takahashi','4','다카하시 목장')],'대안 D · 11/5 니세코·요테이산')
res['se']=render('se',COL['E'],['lodging','saimi','nikka','pathos','soyogi','lodging'],[('saimi','1','멘야 사이미'),('nikka','2','닛카 요이치 증류소'),('pathos','3','르타오 파토스 · 운하'),('soyogi','4','덴푸라 소요기')],'대안 E · 11/3 두대불 대신 요이치')
res['sf']=render('sf',COL['F'],['lodging','hokudai','akarenga','tvtower','suage'],[('hokudai','1','홋카이도대학 은행나무길'),('akarenga','2','아카렌가 · 시계탑'),('tvtower','3','오도리 · 테레비탑'),('suage','4','스아게+ (저녁) · 시로쿠마 (야식)')],'대안 F · 11/2 오후 삿포로 시내 (공항·도마코마이는 그대로)')
res['sg']=render('sg',COL['G'],['lodging','hokudai','meshiya','beermuseum','akarenga','tvtower','saera','lodging'],[('hokudai','1','홋카이도대학 은행나무길'),('meshiya','2','조가이 시장 메시야'),('beermuseum','3','삿포로 맥주박물관'),('akarenga','4','아카렌가 · 시계탑'),('tvtower','5','오도리 · 테레비탑'),('saera','6','사에라 · 다누키코지')],'대안 G · 11/5 삿포로 시내 (차 없이)')
json.dump(res,open('daymaps_se.json','w'))
