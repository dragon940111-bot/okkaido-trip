import subprocess,re,json,time,urllib.parse,html,sys,os
from PIL import Image
F={
'castella':'Castella_002.jpg',
'soft':'Soft_Ice_cream.jpg',
'soupcurry':'スープカレー_Soup_Curry.jpg',
'napolitan':'Neapolitan,_spaghetti_of_Japanese_origin.jpg',
'jingisukan':'ジンギスカン（ゆきだるま）.jpg',
'misoramen':'151010_Sapporo_ramen_at_Susukino_Sapporo_Hokkaido_Japan01s.jpg',
'cheesecake':'Cheesecake.jpg',
'tendon':'Tendon.jpg',
'soba':'Seiro_soba_at_Takasho_in_Nezu,_Tokyo.jpg',
'curryramen':'Muroran_Curry_Ramen_Ajino-Daioh_Muroran_Honten.jpg',
'yakiniku':'Yakiniku_002.jpg',
'asahiramen':'Baikohken_Ramen.jpg',
'sushi':'Hokkaido_hotatekai_nigiri.jpg',
'butadon':'Tokachi_Butadon_Ippin_Butadon.jpg',
'muroyakitori':'Muroran_Yakitori.jpg',
'hamburg':'Hamburg_steak.jpg',
'omucurry':'Furano_Omu-Curry.jpg',
'kaisendon':'Kaisendon.jpg',
'yakitori':'Typical_yakitori_001.jpg',
'spaghetti':'Spaghetti.jpg',
}
UA='HokkaidoTripPlanner/1.0 (personal itinerary)'
meta={}
if os.path.exists('img/meta.json'): meta=json.load(open('img/meta.json'))
for k,f in F.items():
    if k in meta and os.path.exists(f'img/{k}.jpg'): continue
    page='https://commons.wikimedia.org/wiki/File:'+urllib.parse.quote(f)
    s=subprocess.run(['curl','-s','-A',UA,page],capture_output=True,text=True).stdout
    time.sleep(40)
    lic=re.search(r'"license":"([^"]+)"',s); lic=lic.group(1).replace('\\/','/') if lic else None
    m=re.search(r'\|\s*[Aa]uthor\s*=\s*([^|\n}]+)',s)
    auth=html.unescape(re.sub(r'\[\[[^|\]]*\|([^\]]*)\]\]',r'\1',re.sub(r'\[(\S+) ([^\]]+)\]',r'\2',m.group(1)))).strip() if m else None
    if not auth:
        m=re.search(r'id="fileinfotpl_aut".*?<td[^>]*>(.*?)</td>',s,re.S)
        auth=html.unescape(re.sub(r'<[^>]+>','',m.group(1))).strip()[:80] if m else None
    import hashlib
    h=hashlib.md5(f.encode()).hexdigest(); q=urllib.parse.quote(f)
    class U: pass
    up=U(); up.group=lambda i,u=f'https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{q}/330px-{q}': u
    raw=f'img/{k}.raw'
    r=subprocess.run(['curl','-s','-A',UA,'-o',raw,'-w','%{http_code}',up.group(1)],capture_output=True,text=True).stdout
    time.sleep(40)
    try:
        im=Image.open(raw).convert('RGB'); w,h=im.size
        im.thumbnail((560,560)); im.save(f'img/{k}.jpg',quality=72,optimize=True,progressive=True)
        os.remove(raw)
        meta[k]={'file':f,'page':page,'license':lic,'author':auth,'size':(w,h)}
        print(k,r,lic,auth,(w,h),os.path.getsize(f'img/{k}.jpg'))
    except Exception as e: print(k,'ERR',r,e)
    json.dump(meta,open('img/meta.json','w'),ensure_ascii=False,indent=1)
