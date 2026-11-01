import json,subprocess,time
from pts import P,DAYS
res={}
for d,seq in DAYS.items():
    coords=';'.join(f'{P[k][1]},{P[k][0]}' for k in seq)
    url=f'https://router.project-osrm.org/route/v1/driving/{coords}?overview=full&geometries=geojson&steps=false'
    r=json.loads(subprocess.run(['curl','-s',url],capture_output=True,text=True).stdout)
    rt=r['routes'][0]
    legs=[(seq[i],seq[i+1],round(l['duration']/60),round(l['distance']/1000,1)) for i,l in enumerate(rt['legs'])]
    res[d]={'geom':rt['geometry']['coordinates'],'legs':legs,'dist':round(rt['distance']/1000),'dur':round(rt['duration']/60)}
    print(d,res[d]['dist'],'km',res[d]['dur'],'min',legs)
    time.sleep(1)
json.dump(res,open('routes.json','w'))
