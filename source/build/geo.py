import json,time,urllib.parse,subprocess,sys
Q={
'airport':['新千歳空港 国際線ターミナル','新千歳空港'],
'jnet':['北海道千歳市流通3丁目2'],
'okadama':['丘珠空港'],
'gop':['札幌市西区山の手3条6丁目'],
'chakkaru':['札幌市中央区大通西18丁目'],
'lodging':['札幌市東区北17条東2丁目','札幌市北区北17条西1丁目'],
'saimi':['麺屋彩未','札幌市豊平区美園10条5丁目'],
'daibutsu':['頭大仏','真駒内滝野霊園'],
'pathos':['小樽市堺町5','ルタオ'],
'canal':['浅草橋','小樽運河'],
'soyogi':['小樽市色内1丁目12'],
'oceandays':['支笏湖温泉','千歳市支笏湖温泉'],
'okina':['伊達市弄月町'],
'usuzan':['有珠山ロープウェイ','昭和新山'],
'jigokudani':['登別地獄谷','地獄谷'],
'bibi':['苫小牧市美沢'],
'chikyu':['地球岬'],
'asahidake':['旭岳ロープウェイ','大雪山旭岳ロープウェイ 山麓駅','旭岳温泉'],
'bluepond':['青い池','白金青い池'],
'shirahige':['白ひげの滝'],
'shikisai':['四季彩の丘'],
'baikohken':['旭川市2条通8丁目'],
'suage':['札幌市中央区南4条西5丁目'],
'shirokuma':['札幌市中央区南6条西3丁目'],
'ajinodaiou':['室蘭市中央町2丁目'],
'kurodake':['黒岳ロープウェイ','層雲峡'],
'obihiro':['帯広駅'],
}
out={}
for k,qs in Q.items():
    for q in qs:
        url='https://nominatim.openstreetmap.org/search?'+urllib.parse.urlencode({'q':q,'format':'json','limit':1,'countrycodes':'jp'})
        r=subprocess.run(['curl','-s','-A','trip-planner/1.0 (personal use)',url],capture_output=True,text=True).stdout
        time.sleep(1.2)
        try: j=json.loads(r)
        except: j=[]
        if j:
            out[k]=(float(j[0]['lat']),float(j[0]['lon']),q,j[0]['display_name'][:60]); break
    print(k,out.get(k),flush=True)
json.dump(out,open('geo.json','w'),ensure_ascii=False,indent=0)
