import math,os,subprocess,json,time
from PIL import Image,ImageDraw,ImageFont,ImageEnhance
from pts import P,DAYS
R=json.load(open('routes.json'))
os.makedirs('tiles',exist_ok=True)
FB='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'; FR='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
def font(sz,b=True): return ImageFont.truetype(FB if b else FR,sz,index=1)
SYM=lambda sz: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',sz)
COL={1:(232,89,12),2:(28,126,214),3:(47,158,68),4:(156,54,181),5:(73,80,87)}
def px(lat,lon,z):
    n=256*2**z; x=(lon+180)/360*n
    y=(1-math.log(math.tan(math.radians(lat))+1/math.cos(math.radians(lat)))/math.pi)/2*n
    return x,y
def tile(z,x,y):
    p=f'tiles/{z}_{x}_{y}.png'
    if not os.path.exists(p) or os.path.getsize(p)<100:
        subprocess.run(['curl','-s','-A','HokkaidoTripPlanner/1.0 (personal one-off map)','-o',p,f'https://tile.openstreetmap.org/{z}/{x}/{y}.png'])
        time.sleep(0.15)
    return Image.open(p).convert('RGB')
def base(z,lat0,lat1,lon0,lon1):
    x0,y0=px(lat1,lon0,z); x1,y1=px(lat0,lon1,z)
    tx0,ty0,tx1,ty1=int(x0//256),int(y0//256),int(x1//256),int(y1//256)
    W=(tx1-tx0+1)*256; H=(ty1-ty0+1)*256
    im=Image.new('RGB',(W,H))
    for tx in range(tx0,tx1+1):
        for ty in range(ty0,ty1+1):
            im.paste(tile(z,tx,ty),((tx-tx0)*256,(ty-ty0)*256))
    ox,oy=x0-tx0*256,y0-ty0*256
    im=im.crop((int(ox),int(oy),int(ox+x1-x0),int(oy+y1-y0)))
    im=ImageEnhance.Color(im).enhance(0.55); im=Image.blend(im,Image.new('RGB',im.size,(255,255,255)),0.22)
    f=lambda lat,lon:(px(lat,lon,z)[0]-x0,px(lat,lon,z)[1]-y0)
    return im,f
def offset(pts,d):
    out=[]
    for i,(x,y) in enumerate(pts):
        a=pts[max(i-1,0)]; b=pts[min(i+1,len(pts)-1)]
        dx,dy=b[0]-a[0],b[1]-a[1]; L=math.hypot(dx,dy) or 1
        out.append((x-dy/L*d,y+dx/L*d))
    return out
def draw_routes(dr,f,w,offs):
    for d in [5,1,2,3,4]:
        pts=[f(lat,lon) for lon,lat in R[str(d)]['geom']]
        pts=offset(pts,offs[d])
        ww=w if d!=5 else int(w*0.7)
        dr.line(pts,fill=(255,255,255),width=ww+5,joint='curve')
    for d in [5,1,2,3,4]:
        pts=[f(lat,lon) for lon,lat in R[str(d)]['geom']]
        pts=offset(pts,offs[d])
        ww=w if d!=5 else int(w*0.7)
        dr.line(pts,fill=COL[d],width=ww,joint='curve')
def label(dr,xy,text,sz,fill=(25,25,25),anchor='lm'):
    dr.text(xy,text,font=font(sz),fill=fill,stroke_width=max(3,sz//6),stroke_fill=(255,255,255),anchor=anchor)
def dot(dr,xy,col,r,txt=None,sz=None):
    x,y=xy; dr.ellipse((x-r-3,y-r-3,x+r+3,y+r+3),fill=(255,255,255)); dr.ellipse((x-r,y-r,x+r,y+r),fill=col)
    if txt: dr.text((x,y+1),txt,font=font(sz or int(r*1.3)),fill=(255,255,255),anchor='mm')
def special(dr,xy,kind,r):
    x,y=xy
    col=(16,42,92) if kind=='air' else (201,42,42)
    dr.ellipse((x-r-4,y-r-4,x+r+4,y+r+4),fill=(255,255,255)); dr.ellipse((x-r,y-r,x+r,y+r),fill=col)
    dr.text((x,y+1),'✈' if kind=='air' else '★',font=SYM(int(r*1.35)),fill=(255,255,255),anchor='mm')
def hollow(dr,xy,r):
    x,y=xy; dr.ellipse((x-r,y-r,x+r,y+r),outline=(90,90,90),width=4,fill=(255,255,255))

# ---------- main map z10 ----------
im,f=base(10,42.27,44.02,140.50,143.36)
dr=ImageDraw.Draw(im,'RGBA')
draw_routes(dr,f,8,{1:-7,2:7,3:0,4:-3,5:4})
# sapporo box
bx0,by0=f(43.135,141.20); bx1,by1=f(42.905,141.48)
dr.rounded_rectangle((bx0,by0,bx1,by1),radius=10,outline=(60,60,60,200),width=3)
label(dr,(bx0+4,by1+20),'▲ 삿포로 시내 → 확대지도 참조',21,anchor='lm')
stops={1:[('minato','도마코마이  미나토 식당 (카이센동)','r'),('shikotsu','시코쓰호 산책','l')],
 2:[('pathos','오타루  르타오 · 운하 · 덴푸라 소요기','r')],
 3:[('okina','다테  오키나 (소바)','l'),('lakehill','레이크힐 팜 (젤라토)','r'),('usuzan','쇼와신잔 · 우스잔','r'),('jigokudani','노보리베쓰  지옥계곡·온천','r'),('bibi','로그하우스 비비 (시라오이 와규)','rb')],
 4:[('tenkin','아사히카와  덴킨 라멘','r'),('asahidake','아사히다케 로프웨이','r'),('shirahige','시라히게 폭포','r'),('bluepond','아오이이케','l'),('shikisai','시키사이노오카','l')]}
for d,lst in stops.items():
    for k,t,side in lst:
        x,y=f(*P[k]); dot(dr,(x,y),COL[d],13,str(d),17)
        if t:
            if side=='rb': label(dr,(x+20,y+26),t,24,anchor='lm')
            else: label(dr,(x+22,y) if side=='r' else (x-22,y),t,24,anchor='lm' if side=='r' else 'rm')
for k,t in [('kurodake','대안  소운쿄·구로다케'),('obihiro','대안  오비히로·도카치')]:
    x,y=f(*P[k]); hollow(dr,(x,y),13); label(dr,(x-20,y),t,22,fill=(80,80,80),anchor='rm')
for k,t,side in [('makkari','니세코·요테이','r'),('yoichi','요이치·샤코탄','l'),('ishikari_kd','이시카리','l'),('mashike','마시케·루모이 해안','r'),('bibai','소라치 (비바이·스나가와)','r'),('kuriyama','나가누마·구리야마','r')]:
    x,y=f(*P[k]); hollow(dr,(x,y),12)
    label(dr,(x+19,y) if side=='r' else (x-19,y),t,22,fill=(80,80,80),anchor='lm' if side=='r' else 'rm')
x,y=f(*P['airport']); special(dr,(x,y),'air',20); label(dr,(x+30,y-22),'신치토세 공항 · Jnet 렌터카',26,anchor='lm')
x,y=f(*P['lodging']); special(dr,(x,y),'home',17); label(dr,(x-26,y-26),'숙소 (북17조)',26,fill=(201,42,42),anchor='rm')
# title
label(dr,(30,40),'홋카이도 4박5일 드라이브 루트',40,anchor='lm')
label(dr,(30,88),'11/2(월) – 11/6(금) · 숙소 삿포로 북17조 · 매일 9시 이후 출발',22,fill=(70,70,70),anchor='lm')
# legend
W,H=im.size
lg=[(1,'11/2 월','공항 → 도마코마이 → 시코쓰호 → 삿포로','%dkm'%R['1']['dist']),(2,'11/3 화·휴일','삿포로 → 대불 → 오타루','117km'),(3,'11/4 수','남쪽 루프 (다테·도야·노보리베쓰)','%dkm'%R['3']['dist']),(4,'11/5 목','북쪽 (아사히카와·아사히다케·비에이)','%dkm'%R['4']['dist']),(5,'11/6 금','숙소 → 렌터카 반납 → 공항','51km')]
lx,ly=W-700,H-330
dr.rounded_rectangle((lx,ly,W-24,H-24),radius=16,fill=(255,255,255,235),outline=(200,200,200),width=2)
for i,(d,dt,t,km) in enumerate(lg):
    yy=ly+34+i*44
    dr.line((lx+24,yy,lx+84,yy),fill=COL[d],width=9)
    dr.text((lx+100,yy),dt,font=font(22),fill=(20,20,20),anchor='lm')
    dr.text((lx+262,yy),t,font=font(20,False),fill=(40,40,40),anchor='lm')
    dr.text((W-44,yy),km,font=font(18,False),fill=(110,110,110),anchor='rm')
yy=ly+34+5*44
special(dr,(lx+38,yy),'air',12); dr.text((lx+58,yy),'공항',font=font(19,False),fill=(40,40,40),anchor='lm')
special(dr,(lx+128,yy),'home',12); dr.text((lx+148,yy),'숙소',font=font(19,False),fill=(40,40,40),anchor='lm')
hollow(dr,(lx+218,yy),10); dr.text((lx+236,yy),'대안·지역 맛집',font=font(19,False),fill=(40,40,40),anchor='lm')
dr.text((W-44,H-44),'지도 © OpenStreetMap contributors · 경로 OSRM',font=font(15,False),fill=(90,90,90),anchor='rm')
im.save('map_main.png',optimize=True)
im.convert('RGB').save('map_main.jpg',quality=82,optimize=True,progressive=True)
print('main',im.size,os.path.getsize('map_main.jpg'))

# ---------- Sapporo inset z12 ----------
im,f=base(12,42.905,43.135,141.20,141.54)
dr=ImageDraw.Draw(im,'RGBA')
draw_routes(dr,f,8,{1:-7,2:7,3:0,4:-3,5:4})
items=[('kitaro',1,'기타로 (수프카레)','r'),('chakkaru',1,'찻카루 (커피)','r'),
('saimi',2,'멘야 사이미 (미소라멘)','r'),('daibutsu',2,'두대불','r')]
for k,d,t,side in items:
    x,y=f(*P[k]); dot(dr,(x,y),COL[d],14,str(d),18)
    if k=='chakkaru': label(dr,(x-24,y+4),t,24,anchor='rm')
    else: label(dr,(x+24,y),t,24)
for k,t in [('shirokuma',''),('gurumans',''),('marusushi','')]:
    x,y=f(*P[k]); dr.ellipse((x-11,y-11,x+11,y+11),fill=(255,255,255),outline=(201,42,42),width=4)
x,y=f(*P['shirokuma']); label(dr,(x+18,y+34),'스스키노 (지하철): 11/2·11/3 야식 · 11/5 스시',22,fill=(150,30,30))
x,y=f(*P['lodging']); special(dr,(x,y),'home',18); label(dr,(x+28,y-8),'숙소 North17 B (대략 위치)',24,fill=(201,42,42))
xs,ys=f(43.0816,141.3468); dr.rectangle((xs-7,ys-7,xs+7,ys+7),fill=(30,30,30)); label(dr,(xs-12,ys+14),'기타18조역',18,fill=(30,30,30),anchor='rm')
label(dr,(24,34),'삿포로 시내 확대',32)
W,H=im.size
dr.text((W-16,H-16),'© OpenStreetMap contributors',font=font(15,False),fill=(90,90,90),anchor='rd')
im.convert('RGB').save('map_sapporo.jpg',quality=82,optimize=True,progressive=True)
print('inset',im.size,os.path.getsize('map_sapporo.jpg'))
