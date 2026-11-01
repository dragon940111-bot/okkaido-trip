import subprocess,re,json,time,urllib.parse
C=['Parfaits','Parfaits_in_Japan','Parfaits_of_Japan','Ice_cream_sundaes','Affogato','Toyama_black_ramen','Shio_ramen','Shio-ramen','Tori_paitan_ramen','Chicken_ramen','Tebasaki','Chicken_wings_as_food','Zangi','Karaage','Squid_sashimi','Ika-sōmen','Sebastolobus_macrochir','Robatayaki','Tsukune','Negima_(yakitori)','Sushi_restaurants_in_Japan','Tachigui_sushi','Ikura','Toro_(sushi)','Gunkanmaki','Ramen_in_Sapporo']
out={}
for c in C:
    s=subprocess.run(['curl','-s','-A','HokkaidoTripPlanner/1.0 (personal itinerary)','https://commons.wikimedia.org/wiki/Category:'+c],capture_output=True,text=True).stdout
    files=sorted(set(urllib.parse.unquote(f) for f in re.findall(r'href="/wiki/File:([^"]+)"',s)))
    out[c]=files; print(c,len(files),('429' if 'too many' in s.lower() else ''),flush=True); time.sleep(4)
json.dump(out,open('cats5.json','w'),ensure_ascii=False,indent=0)
