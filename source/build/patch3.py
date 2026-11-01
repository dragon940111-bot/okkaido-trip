s=open('data.py').read()
s=s.replace("구글 4.4(616건)로 이 지역 고깃집 중 가장 높고, '마블링이 입에서 녹는다'는 평이 많습니다.","구글 평점 4.4(616건)로 평가가 높고, '마블링이 입에서 녹는다'는 평이 많습니다.")
s=s.replace("진한 카레 국물에 쫄깃한 굵은 면이 들어가 홋카이도에서도 이 지역에서만 흔한 메뉴입니다.","카레 국물 라멘은 무로란 일대의 향토 메뉴라 이 지역에 온 김에 맛보기 좋습니다.")
open('data.py','w').write(s)
b=open('build.py').read()
b=b.replace("""    {rating(r['g'], r['gn'], r['t'])}
    <dl>""","""    {rating(r['g'], r['gn'], r['t'])}
    {('<div class="reason"><b>추천 이유</b><p>' + E(r['why']) + '</p></div>') if r.get('why') else ''}
    <dl>""",1)
i=b.index("BOOK = ["); j=b.index("]\n",i)+2
b=b[:i]+'''BOOK = [
 ('bk2', '天ぷら 梵 (そよぎ)', '11/3 17:00 · 3명', '전화 <span class="num">0134-24-7220</span> (일본어, 카운터 9석)', None),
 ('bk3', 'しろくま 札幌本店', '11/2 19:00 · 3명', '타베로그 넷예약 또는 전화 <span class="num">011-552-4690</span>', 'https://tabelog.com/hokkaido/A0101/A010103/1000800/'),
 ('bk4', 'ログハウスびび', '11/4 19:00 · 3명 (L.O. 19:30)', '전화 예약 (번호는 공식 사이트)', 'https://restaurant-bibi.jp/'),
 ('bk6', '[당일] 아사히다케 운행 · 青葉 영업', '11/5 아침', '공식 사이트 운행 정보 · 青葉 <span class="num">0166-23-2820</span>', 'https://asahidake.hokkaido.jp/'),
 ('bk7', '예약 안 받는 곳 (줄 서기)', '彩未 · 翁 · マルトマ · Suage+ · 르타오(공휴일)', '시간표의 도착 시각을 지키면 대기가 가장 짧음', None),
]
'''+b[j:]
open('build.py','w').write(b)
t=open('tpl.html').read()
t=t.replace(".tip{font-size:13px;",".reason{background:color-mix(in srgb,var(--accent) 8%,var(--card));border-radius:8px;padding:9px 11px;display:grid;gap:3px}\n.reason b{font-size:12px;letter-spacing:.04em;color:var(--accent)}\n.reason p{font-size:13.5px;line-height:1.65}\n.tip{font-size:13px;",1)
open('tpl.html','w').write(t)
