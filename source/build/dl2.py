import json,re,html,subprocess,time,urllib.parse,os,hashlib
from PIL import Image
UA='HokkaidoTripPlanner/1.0 (personal itinerary)'
import sys
picks=json.load(open(sys.argv[1] if len(sys.argv)>1 else 'picks.json'))
meta=json.load(open('img/meta.json'))
def page_meta(f):
    s=subprocess.run(['curl','-s','-A',UA,'https://commons.wikimedia.org/wiki/File:'+urllib.parse.quote(f)],capture_output=True,text=True).stdout
    lic=re.search(r'"license":"([^"]+)"',s); lic=lic.group(1).replace('\\/','/') if lic else None
    x=re.search(r'fileinfotpl(?:_|&#95;)aut".*?</td>\s*<td[^>]*>(.*?)</td>',s,re.S)
    au=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>','',x.group(1)))).strip()[:90] if x else None
    return lic,au
for rnd in range(6):
    left=[(k,f) for k,f in picks if not os.path.exists(f'img/{k}.jpg')]
    if not left: break
    for k,f in left:
        if k not in meta or not meta[k].get('license'):
            lic,au=page_meta(f); time.sleep(3)
            meta[k]={'file':f,'page':'https://commons.wikimedia.org/wiki/File:'+urllib.parse.quote(f),'license':lic,'author':au,'author_ok':bool(au)}
            json.dump(meta,open('img/meta.json','w'),ensure_ascii=False,indent=1)
        h=hashlib.md5(f.encode()).hexdigest(); q=urllib.parse.quote(f)
        ok=False
        for w in (330,500,250):
            u=f'https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{q}/{w}px-{q}'
            r=subprocess.run(['curl','-s','-A',UA,'-o',f'img/{k}.raw','-w','%{http_code}',u],capture_output=True,text=True).stdout
            if r=='200':
                try:
                    im=Image.open(f'img/{k}.raw').convert('RGB'); im.thumbnail((560,560)); im.save(f'img/{k}.jpg',quality=74,optimize=True,progressive=True); ok=True
                except Exception as e: pass
                break
            time.sleep(8)
        if os.path.exists(f'img/{k}.raw'): os.remove(f'img/{k}.raw')
        print(rnd,k,'OK' if ok else 'fail',meta[k].get('license'),meta[k].get('author'),flush=True)
        time.sleep(22 if ok else 45)
