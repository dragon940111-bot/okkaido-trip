s=open('data.py').read()
old1=s[s.index("   routes=[('하루 경로', '新千歳空港', '北18条駅', ['丘珠空港','gopのアナグラ','喫茶ちゃっかる'])],"):s.index(" dict(n=2,")]
new1='''   routes=[('하루 경로', '新千歳空港', '北18条駅', ['gopのアナグラ','喫茶ちゃっかる'])],
   items=[
    ('11:15','note',None,'LJ203 신치토세 국제선 도착','입국·수하물 찾고 나오면 약 11:50'),
    ('12:00','stay','jnet','Jnet 렌터카 픽업','도착 로비에서 셔틀(약 10분). 늦어지면 영업소에 연락. 4WD·스터드리스·ETC 카드 확인'),
    ('12:40','move',None,'gop로 (약 1시간, 道央道)',None),
    ('13:40','eat','gop','늦은 점심: 수프카레',None),
    ('15:00','eat','chakkaru','[선택] 킷사텐 커피·나폴리탄','월요일 18:30까지'),
    ('16:00','stay',None,'숙소 체크인 · 휴식','FlexCella North17 B, 무료 주차 1대. 北18条역 근처'),
    ('19:00','eat','shirokuma','저녁: 징기스칸 (지하철 이동)','南北線 北18条 → すすきの 약 8분. 차는 숙소에 두고 맥주 가능. 대안: 이타다키마스 (기존 14)'),
   ]),
'''
s=s.replace(old1,new1)
s=s.replace("title='도착 · 삿포로 시내', color='d1', km='약 75km', drive='운전 약 2시간',","title='도착 · 삿포로 시내', color='d1', km='약 65km', drive='운전 약 1시간 30분',")
i0=s.index(" dict(n=3,"); i1=s.index(" dict(n=4,")
new3=open('day3.txt').read()
s=s[:i0]+new3+s[i1:]
s=s.replace("('19:00','eat','suage','저녁: 수프카레 (지하철 이동)','옵션: 후라노 唯我独尊 오무카레로 17:00 저녁 → 20:00 귀가'),",
            "('19:00','eat',('suage','yuiga'),'저녁: 수프카레 (지하철 이동)','옵션: 귀갓길 후라노에서 唯我独尊 오무카레로 17:00 저녁 → 20:00 귀가 (아래 두 번째 카드)'),")
s=s.replace("'11/2 오후 SKY 크루즈를 빼면 들를 수 있음'","'11/2 오후(15–16시)에 넣을 수 있음. 월요일 개관 여부는 확인 필요'")
s=s.replace(" 'jnet': dict(name='Jnet 렌터카 新千歳空港店',",
 " 'chikyu': dict(name='地球岬 (チキウ岬)', area='무로란', pid='ChIJq8GrwjjQn18RVcPtj0eFJqM', orig=None, g='4.2', gn='',\n   facts=['태평양 쪽 절벽 위 등대 전망대', '주차 ¥500 (2026/4부터 유료, 36대)', '일몰 16:20 전후']),\n 'jnet': dict(name='Jnet 렌터카 新千歳空港店',")
s=s.replace("q='マルトマ食堂 苫小牧市汐見町1-1-13'),","q='マルトマ食堂 苫小牧市汐見町1-1-13', inplan='11/4 아침'),")
open('data.py','w').write(s)
d=s[s.index('DAYS = ['):]
print(s.count("inplan="), 'skycruise' in d, 'oceandays' in d, 'chikyu' in s)
