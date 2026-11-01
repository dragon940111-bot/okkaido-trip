import subprocess,re,json,time,urllib.parse
C=['Soup_curry','Sapporo_ramen','Asahikawa_ramen','Shoyu-ramen','Miso-ramen','Butadon','Jingisukan','Tendon_(Tempura-Donburi)','Tempura','Zaru_soba','Kaisen-don','Hamburg_steaks','Omurice','Furano_Omu-Curry','Japanese_curry','Yakiniku','Wagyu','Yakitori','Naporitan','Cheesecakes','Gelato','Soft_serve_ice_cream','Castella_(food)','Nigirizushi','Sushi_in_Hokkaido','Muroran_curry_ramen','Muroran_yakitori','Rokkatei','LeTAO','Kissaten','Seafood_donburi','Tonkatsu','Ramen_in_Hokkaido','Food_of_Hokkaido','Cuisine_of_Hokkaido','Shinkoyaki','Soba_in_Japan','Hamburg_steak_in_Japan','Japanese_desserts']
out={}
for c in C:
    s=subprocess.run(['curl','-s','-A','HokkaidoTripPlanner/1.0 (personal itinerary)','https://commons.wikimedia.org/wiki/Category:'+c],capture_output=True,text=True).stdout
    files=sorted(set(urllib.parse.unquote(f) for f in re.findall(r'href="/wiki/File:([^"]+)"',s)))
    out[c]=files; print(c,len(files),flush=True); time.sleep(4)
json.dump(out,open('cats.json','w'),ensure_ascii=False,indent=0)
