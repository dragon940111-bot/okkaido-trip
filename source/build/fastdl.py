import json,subprocess,time,urllib.parse,os,hashlib
from PIL import Image
UA='HokkaidoTripPlanner/1.0 (personal itinerary)'
picks=json.load(open('picks_all.json'))
for rnd in range(40):
    left=[(k,f) for k,f in picks if not os.path.exists(f'img/{k}.jpg')]
    print('round',rnd,'left',len(left),flush=True)
    if not left: break
    for k,f in left:
        h=hashlib.md5(f.encode()).hexdigest(); q=urllib.parse.quote(f)
        w=[330,250,500][rnd%3]
        u=f'https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{q}/{w}px-{q}'
        r=subprocess.run(['curl','-s','-A',UA,'-o',f'img/{k}.raw','-w','%{http_code}',u],capture_output=True,text=True).stdout
        if r=='200':
            try:
                im=Image.open(f'img/{k}.raw').convert('RGB'); im.thumbnail((560,560)); im.save(f'img/{k}.jpg',quality=76,optimize=True,progressive=True)
                print('OK',k,flush=True)
            except Exception as e: print('bad',k,e,flush=True)
        elif r=='404': print('404',k,f,flush=True)
        if os.path.exists(f'img/{k}.raw'): os.remove(f'img/{k}.raw')
        time.sleep(2.5)
    time.sleep(10)
