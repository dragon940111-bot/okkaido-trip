import json,re,html,subprocess,time,urllib.parse
UA='HokkaidoTripPlanner/1.0 (personal itinerary)'
P=json.load(open('photos.json'))
meta=json.load(open('img/meta.json'))
for card,lst in P.items():
    for k,f,shop in lst:
        if k in meta and meta[k].get('license') and meta[k].get('author'): continue
        page='https://commons.wikimedia.org/wiki/File:'+urllib.parse.quote(f)
        s=subprocess.run(['curl','-s','-A',UA,page],capture_output=True,text=True).stdout
        lic=re.search(r'"license":"([^"]+)"',s); lic=lic.group(1).replace('\\/','/') if lic else None
        x=re.search(r'fileinfotpl(?:_|&#95;)aut".*?</td>\s*<td[^>]*>(.*?)</td>',s,re.S)
        au=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>','',x.group(1)))).strip()[:90] if x else None
        meta[k]={'file':f,'page':page,'license':lic,'author':au}
        json.dump(meta,open('img/meta.json.tmp','w'),ensure_ascii=False,indent=1)
        print(k,lic,au,flush=True); time.sleep(2)
import os; os.replace('img/meta.json.tmp','img/meta.json')
print('DONE')
