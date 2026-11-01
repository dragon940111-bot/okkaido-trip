import json,re,html,subprocess,time,urllib.parse,os
m=json.load(open('img/meta.json'))
for k,v in m.items():
    if v.get('author_ok') or not os.path.exists(f'img/{k}.jpg'): continue
    s=subprocess.run(['curl','-s','-A','HokkaidoTripPlanner/1.0 (personal itinerary)',v['page']],capture_output=True,text=True).stdout
    time.sleep(12)
    x=re.search(r'fileinfotpl(?:_|&#95;)aut".*?</td>\s*<td[^>]*>(.*?)</td>',s,re.S)
    if x:
        t=html.unescape(re.sub(r'<[^>]+>','',x.group(1))); t=re.sub(r'\s+',' ',t).strip()
        v['author']=t[:90]; v['author_ok']=True
    lic=re.search(r'"license":"([^"]+)"',s)
    if lic: v['license']=lic.group(1).replace('\\/','/')
    print(k,v.get('author'),v.get('license'),flush=True)
    json.dump(m,open('img/meta.json','w'),ensure_ascii=False,indent=1)
