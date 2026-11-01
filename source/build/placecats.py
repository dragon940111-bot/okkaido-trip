import subprocess,re,json,time,urllib.parse,sys
UA='HokkaidoTripPlanner/1.0 (personal itinerary)'
C=sys.argv[1:]
out={}
for c in C:
    s=subprocess.run(['curl','-s','-A',UA,'https://commons.wikimedia.org/wiki/Category:'+c],capture_output=True,text=True).stdout
    files=[urllib.parse.unquote(f) for f in re.findall(r'href="/wiki/File:([^"]+)"',s)]
    seen=[];[seen.append(f) for f in files if f not in seen]
    subs=sorted(set(urllib.parse.unquote(x) for x in re.findall(r'href="/wiki/Category:([^"]+)"',s)))
    out[c]={'files':seen,'subs':[x for x in subs if not x.startswith(('Lakes_','Media','Pages','CC-','Files','Hidden','Uploaded'))][:25]}
    print(c,len(seen),flush=True); time.sleep(3)
old={}
try: old=json.load(open('placecats.json'))
except Exception: pass
old.update(out); json.dump(old,open('placecats.json','w'),ensure_ascii=False,indent=0)
