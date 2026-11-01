# -*- coding: utf-8 -*-
# v19.2 "미리 할 것" — 본 일정(DAY 1–5) 예약·준비·당일 확인 목록 + 렌터카 가는 길(접기)
# 만든 날: 2026/11/1 (KST) · Claude B
# 근거:
#  - 기존 build2.py BOOK, data2.py DAYS·R (전화번호·예약 방법·영업시간)
#  - Jnet 新千歳空港店 매장 정보: 楽天トラベル 렌터카 매장 페이지 (https://cars.travel.rakuten.co.jp/cars/rcf130a.do?v=1&eid=15051, 2026/11/1 확인)
#    · 공식 사이트(j-netrentacar.co.jp)는 11/1 확인 때 '시스템 점검 중'이라 못 봄
#  - 新千歳空港 층별 안내도 PDF (北海道エアポート, ja_dom_12.pdf): 국내선 1층 버스 정류장 1번 위치, Jnet 전화
#  - 新千歳空港 공식 렌터카 안내 (https://www.hokkaido-airports.com/ja/new-chitose/access/rentacar/)
#  - 和牛レストラン ログハウスびび 공식 (https://restaurant-bibi.jp/ , /reserve) — 전화·겨울 영업시간·예약 폼 마감
#  - Visit Japan Web 공식 (デジタル庁 services.digital.go.jp/visit-japan-web)
#  - 인계 문서 2장(항공·렌터카·숙소), 3장(드론)
# 체크박스 id: 기존 bk1–bk10 그대로 유지(브라우저에 저장된 체크가 이어지게), 새 항목은 bk11부터 / 숙소는 bk_stay
# 화면 표시 상태(status): 예약됨 · 지금 예약 · 준비 · 선택 · 당일 확인 · 줄 서기

BOOK19_SECTION_ID = 'booking'          # body2.html의 <section id="booking"> 그대로
BOOK19_STORAGE_KEY = 'hk-trip-book'    # body2.html 체크박스 스크립트의 localStorage 키 그대로
BOOK19_TITLE = '미리 할 것'
BOOK19_INTRO = ('출발 전에 예약·준비할 것, 당일 아침에 확인할 것 순서대로 모았음. '
                '체크 표시는 이 폰(브라우저)에만 저장됨. 전화번호는 길게 눌러서 복사. '
                '대안으로 바꿀 때 필요한 예약은 맨 아래 접힌 칸에 따로 있음.')

GROUPS = [
    ('pre',  '출발 전 · 준비', '항공·입국·렌터카·숙소 — 이미 예약된 것은 내용만 확인'),
    ('rsv',  '출발 전 · 식당 예약', '전화나 타베로그 넷예약으로 지금 잡아 둘 곳 (3명)'),
    ('day',  '여행 중 · 그날 확인', '날짜순'),
    ('line', '예약 없이 줄 서는 곳', '예약을 안 받는 곳 — 시간표의 도착 시각을 지키면 대기가 가장 짧음'),
]

_SRC = '<p class="bksrc">{}</p>'

# ── 렌터카: 공항에서 영업소까지 가는 길 (접기) ─────────────────────────────
RENTAL_ROUTE_HTML = '''
<ol class="bkroute">
  <li><b>11:15 신치토세 국제선 도착</b> 입국심사 → 짐 찾기 → 세관. Visit Japan Web QR 미리 띄워 두면 빠름. 도착 로비 나오면 대략 11:45–12:00 (입국 줄에 따라 다름).</li>
  <li><b>국제선 → 국내선으로 건너가기 (약 10분)</b> 2층 연결통로(무빙워크)로 감. 3층 통로는 공사 중이라 꼭 2층으로. 도착 디저트(우유 카스텔라·요츠바 소프트)도 국내선 쪽이라 가는 길에 들름.</li>
  <li><b>국내선 1층 → 밖으로</b> 국내선 1층 도착 로비로 내려가서 <b>到着口5(JAL·스카이마크 쪽, 동쪽 끝)</b> 근처로 나감. Jnet은 <b>공항 안에 카운터 없음</b> → 바로 버스 타는 곳으로.</li>
  <li><b>셔틀 타는 곳 = 「許可車乗降所」(허가차 승하차장)</b> 밖에서 버스·택시 레인 따라 <b>왼쪽(정류장 번호 작아지는 쪽)</b>으로 걸어서 <b>1번 정류장</b> 조금 지나면 <b>交番(파출소) 옆</b>에 있음. 여기가 Jnet 셔틀 타는 곳. 1번 정류장 = 국내선 동쪽 끝(진료소 앞).</li>
  <li><b>Jnet 무료 셔틀 (예약 필요 없음)</b> 11–3월 8:15–18:30, <b>약 15분 간격</b>이라 오는 Jnet 버스 타면 됨. 영업소까지 약 10분. 셔틀 안 보이면 <span class="num">0120-302-554</span> → 음성 안내 <b>1번</b>. 단, 0120 번호는 한국 폰 로밍으로 안 걸릴 수 있음(확인 못 함).</li>
  <li><b>영업소 (千歳市流通3-2-8 · 11/1–3/31 영업 08:00–19:00)</b>
    <ul>
      <li>예약번호 <b>R0V66VWT</b>랑 예약자 이름 말하기. 「予約しています。R0V66VWTです。」(요야쿠시테 이마스)</li>
      <li><b>운전은 경일 혼자</b>: 한국 면허증 + 국제면허증 + 여권 보여 주고 운전자 등록. 등록 안 한 사람은 운전 못 함.</li>
      <li>예약에 넣은 것 확인: 면책보상 + 안심보상 와이드(NOC) + ETC 카드. 보상은 매장에서도 고를 수 있다는 안내가 있어, 이미 넣었다고 한 번 더 말하기.</li>
      <li>차 받기: 시엔타·프리드급(차종 지정 불가, 클래스업 가능), 4WD·스터드리스 확인. 출발 전에 차 둘레 흠집 폰으로 찍어 두면 반납 때 편함.</li>
      <li>ETC 카드가 차에 꽂혀 있는지 확인 → 고속도로는 ETC 차로로.</li>
      <li>내비 목적지: みなと食堂(도마코마이) 전화번호 <span class="num">0144-34-1777</span> 입력 → 출발 전에 같은 번호로 남은 메뉴 확인.</li>
    </ul></li>
  <li><b>11/6 반납 날 (거꾸로)</b>
    <ul>
      <li>08:15 숙소 출발 → 09:10 영업소 근처 주유소에서 <b>가득(満タン) 채우기</b>, 영수증 챙기기 → <b>09:20 반납</b> (예약상 반납 기한 11:00).</li>
      <li>셔틀로 공항(약 10분). 국제선 간다고 말하면 됨: 「国際線ターミナルまでお願いします。」(고쿠사이센 타-미나루마데 오네가이시마스). 국내선 쪽에 내리면 2층 연결통로로 국제선까지 약 10분.</li>
      <li>09:45 국제선 도착 → LJ204(12:15 출발) 체크인부터. 카운터가 아직 안 열렸으면 이치겐 라멘 먼저. 카운터 여는 시각·마감 시각은 e티켓·진에어 앱에서 확인(직접 보지 못함).</li>
    </ul></li>
</ol>
''' + _SRC.format('근거: Jnet 매장 정보(라쿠텐 트래블, 11/1) · 신치토세 공항 층별 안내도. '
                  '<b>국제선 쪽에서 바로 태워 주는 곳이 있는지는 확인 못 함</b> — 렌터카에 도착 연락할 때 같이 물어보기.')

ICHII_SCRIPT = ('<details class="script"><summary>전화할 때 쓸 일본어 문장 보기</summary>'
                '<span class="jn" lang="ja">「11月5日（木）20時から3名で、おまかせコース（9,000円）をお願いしたいのですが、空いていますか。できればカウンターでお願いします。」</span> <br>'
                '한글 발음: "주이치가쓰 이쓰카(모쿠) 니주지카라 산메이데, 오마카세 코-스(큐-센엔)오 오네가이시타이노데스가, 아이테이마스카. 데키레바 카운타-데 오네가이시마스."<br>'
                '뜻: "11월 5일(목) 20시부터 3명, 오마카세 코스(9,000엔)로 부탁드리고 싶은데 자리 있나요? 가능하면 카운터로 부탁드려요."</details>')
SOYOGI_SCRIPT = ('<details class="script"><summary>전화할 때 쓸 일본어 문장 보기</summary>'
                 '<span class="jn" lang="ja">「11月3日（祝日）17時から3名で予約をお願いしたいのですが、空いていますか。」</span> <br>'
                 '한글 발음: "주이치가쓰 밋카(슈쿠지쓰) 주시치지카라 산메이데 요야쿠오 오네가이시타이노데스가, 아이테이마스카."<br>'
                 '뜻: "11월 3일(공휴일) 17시부터 3명 예약하고 싶은데 자리 있나요?"</details>')
BIBI_SCRIPT = ('<details class="script"><summary>전화할 때 쓸 일본어 문장 보기</summary>'
               '<span class="jn" lang="ja">「11月4日（水）18時半から3名で予約をお願いしたいのですが、空いていますか。」</span> <br>'
               '한글 발음: "주이치가쓰 욧카(스이) 주하치지 한카라 산메이데 요야쿠오 오네가이시타이노데스가, 아이테이마스카."<br>'
               '뜻: "11월 4일(수) 18시 반부터 3명 예약하고 싶은데 자리 있나요?"</details>')
NAME_TIP = '<span class="bkhint">이름을 물으면 「チェです」(체데스).</span>'

DRONE_HTML = '''
<ul class="bklist">
  <li>Potensic ATOM 2는 100g 이상이라 일본 <b>DIPS 2.0 기체 등록</b> 필요(수수료 약 ¥1,450).</li>
  <li>등록번호(JU…) 받으면 기체에 표시.</li>
  <li>원격ID: Potensic ATOM 2는 일본 원격ID 적합 목록에 있음(2025/2/25 등재).</li>
  <li>국립공원(시코쓰·도야, 다이세쓰산 등) 안에서 날리려면 환경성 사무소에 미리 문의, 고도는 150m 미만.</li>
  <li>자세한 절차는 별도 대화 "포텐식 atom2 dips 가입 및 납부 방법"과 폴더 <code>06_드론_참고자료</code>.</li>
</ul>'''

BOOK19 = [
    # ── 출발 전 · 준비 ──
    dict(id='bk11', group='pre', name='항공권 · 여권 이름 확인', when='출발 전 · 인천 11/2 06:30쯤 도착',
         how_html='진에어 <b>LJ203</b> 11/2 08:30 인천 → 11:15 신치토세 · <b>LJ204</b> 11/6 12:15 신치토세 → 15:30 인천 · 예약 <b>JHG9TP</b>(트래블버킷). '
                  '각자 e티켓 영문 이름이 여권과 똑같은지 확인 — 경일 e티켓은 <b>KYUNGIK</b>로 보였음(여권 KYUNGIL) → 다르면 출발 전에 진에어·트래블버킷에 문의. 수하물·사전 체크인 조건은 e티켓에서 확인(직접 보지 못함).',
         url=None, status='예약됨', detail_title=None, detail_html=None),
    dict(id='bk12', group='pre', name='Visit Japan Web 등록 (각자)', when='출발 전 · 휴대폰으로 5–10분',
         how_html='입국심사·세관신고를 QR 하나로 하는 일본 정부 서비스. 회원 가입 → 본인 정보·여권 → 여행 일정(입국 11/2 LJ203, 숙소 주소) → 입국심사·세관 정보 등록 → QR 화면 캡처. 안 해도 입국은 되는데 하면 줄이 짧아짐.',
         url='https://services.digital.go.jp/visit-japan-web/', status='준비', detail_title=None, detail_html=None),
    dict(id='bk1', group='pre', name='Jnet 렌터카 (新千歳空港店)', when='11/2 12:00 예약 → 12:30쯤 도착 · 11/6 11:00까지 반납',
         how_html='예약 <b>R0V66VWT</b> · 시엔타·프리드급 4WD·스터드리스 · 면책 + 안심보상 와이드(NOC) + ETC · ¥27,830. '
                  '<b>미리 할 것:</b> ① 예약 시각보다 늦은 <b>12:30쯤 간다고 연락</b> (☎<span class="num">0120-302-554</span> — 한국 휴대폰 로밍으로는 0120 번호가 안 걸릴 수 있음, 해외 문의 메일 h_yoyakucenter@j-netrentacar.co.jp) ② 운전하는 경일은 <b>한국 면허증 + 국제운전면허증 + 여권</b> 챙기기.',
         url=None, status='예약됨', detail_title='공항에서 렌터카 영업소까지 가는 길 (11/6 반납 포함)', detail_id='car_route', detail_html=RENTAL_ROUTE_HTML),
    dict(id='bk_stay', group='pre', name='숙소 FlexCella North17 B (Airbnb)', when='11/2 체크인 → 11/6 체크아웃 · 4박',
         how_html='北18条역 근처 · 침실 3개 · 무료 주차 1대. 체크인 방법·열쇠·주차·가는 길(렌터카 경로 포함)은 아래 숙소 안내에.',
         url=None, status='예약됨', detail_title=None, detail_html=None),
    dict(id='bk13', group='pre', name='[선택] 드론을 가져갈 경우', when='출발 전',
         how_html='가져가지 않으면 건너뛰기.', url=None, status='선택',
         detail_title='드론 준비 (DIPS 등록·원격ID·국립공원)', detail_html=DRONE_HTML),

    # ── 출발 전 · 식당 예약 ──
    dict(id='bk3', group='rsv', name='しろくま 札幌本店 (징기스칸)', when='11/2(월) 20:30 · 3명',
         how_html='타베로그 넷예약 또는 전화 <span class="num">011-552-4690</span>. 당일 취소는 1인 ¥5,000, 붐비면 90분 제한. 19:00으로 잡아 두었다면 20:30으로 변경.',
         url='https://tabelog.com/hokkaido/A0101/A010103/1000800/', status='지금 예약', detail_title=None, detail_html=None),
    dict(id='bk2', group='rsv', name='天ぷら 梵 (そよぎ) (덴푸라 · 오타루)', when='11/3(화·공휴일) 17:00 · 3명',
         how_html='<b>전화만</b> <span class="num">0134-24-7220</span> (일본어 · 카운터 9석, 주인 혼자 운영). ' + NAME_TIP + ' 안 잡히면 시간표 11/3 저녁 대안 참고.', after_html=SOYOGI_SCRIPT,
         url='https://tabelog.com/hokkaido/A0106/A010601/1043274/', status='지금 예약', detail_title=None, detail_html=None),
    dict(id='bk8', group='rsv', name='焼肉 グルマンズいとう (야키니쿠 · 야식)', when='11/3(화·공휴일) 21:00 · 3명',
         how_html='타베로그 넷예약 또는 전화 <span class="num">011-596-9029</span>. 2개월 전부터 받고 21시 이후가 비교적 여유. 안 되면 대안 1순위 芯々 (넷예약 21:00 가능, ☎<span class="num">011-206-9009</span>).',
         url='https://tabelog.com/hokkaido/A0101/A010103/1068431/', status='지금 예약', detail_title=None, detail_html=None),
    dict(id='bk4', group='rsv', name='ログハウスびび (와규 · 시라오이)', when='11/4(수) 18:30–18:35 · 3명 · L.O. 19:30',
         how_html='<b>전화</b> <span class="num">0144-58-3456</span> (11:00–20:00 · 11–3월은 20시 마감). 공식 웹 예약 폼은 <b>3일 전(=11/1)까지</b>이고 가게가 전화로 확인해야 확정이라, 지금은 전화가 확실합니다. ' + NAME_TIP, after_html=BIBI_SCRIPT,
         url='https://restaurant-bibi.jp/reserve/', status='지금 예약', detail_title=None, detail_html=None),
    dict(id='bk9', group='rsv', name='鮨処いちい (스시 오마카세)', when='11/5(목) 20:00 · 3명 · おまかせ ¥9,000',
         how_html='전화 <span class="num">011-232-2321</span> (넷예약에는 3명 자리가 없음). ' + NAME_TIP + ' 안 되면 鮨処 凜 20:00 넷예약.', after_html=ICHII_SCRIPT,
         url='https://tabelog.com/hokkaido/A0101/A010102/1002533/', status='지금 예약', detail_title=None, detail_html=None),

    # ── 여행 중 · 그날 확인 ──
    dict(id='bk10', group='day', name='[11/2] みなと食堂 남은 메뉴 확인', when='11/2 12:30 차 받을 때',
         how_html='예약 불가 · 현금만 · 13시 넘으면 일부 품절 → 전화 <span class="num">0144-34-1777</span>로 남은 메뉴 확인 후 출발.',
         url='https://tabelog.com/hokkaido/A0108/A010802/1057683/', status='당일 확인', detail_title=None, detail_html=None),
    dict(id='bk14', group='day', name='[11/3] 르타오 파토스 번호표', when='11/3 14:20 도착하자마자',
         how_html='공휴일은 좌석 예약을 안 받음 → 매장에서 번호표 발권 + LINE 순서 알림 → 기다리는 동안 사카이마치 산책. 특약 주차장 휴일 ¥300/시간.',
         url='https://tabelog.com/hokkaido/A0106/A010601/1033815/', status='당일 확인', detail_title=None, detail_html=None),
    dict(id='bk6', group='day', name='[11/5] 아침에 아사히다케 운행 · 天金 영업 확인', when='11/5 아침 출발 전',
         how_html='아사히다케 로프웨이는 강풍이면 운휴(공식 사이트 운행 상황), 天金은 부정기 휴무.',
         url='https://asahidake.hokkaido.jp/', status='당일 확인', detail_title=None, detail_html=None),
    dict(id='bk15', group='day', name='[11/6] 주유 → 렌터카 반납 → 체크인', when='11/6 09:10 주유 · 09:20 반납 · 09:45 체크인',
         how_html='영업소 근처 주유소에서 가득 채워 반납(영수증 챙기기) → 반납 기한 11:00 → 셔틀로 공항 → LJ204 체크인 먼저, 그다음 一幻 새우 라멘(10:05쯤). 순서는 위 렌터카 항목의 "가는 길" 7번.',
         url=None, status='당일 확인', detail_title=None, detail_html=None),

    # ── 예약 없이 줄 서는 곳 ──
    dict(id='bk7', group='line', name='예약 안 받는 곳 (줄 서기)', when='시간표 도착 시각 지키기',
         how_html='<b>11/2</b> みなと食堂 13:20 · 木多郎 17:30 오픈에 맞춰(현금만) · <b>11/3</b> 彩未 10:05(공휴일, 붐비면 10:30 오픈) · 르타오 번호표 · '
                  '<b>11/4</b> 伊達 翁 11:05(11:30 오픈) · <b>11/5</b> 天金 11:00 · <b>11/6</b> 一幻(체크인 먼저).',
         url=None, status='줄 서기', detail_title=None, detail_html=None),
]

STATUS_CLASS = {'예약됨': 'done', '지금 예약': 'now', '준비': 'prep', '선택': 'opt', '당일 확인': 'day', '줄 서기': 'line'}


def render_book19(E, a, lodging_html=''):
    """E = html.escape, a = build2.py의 a(href, text, cls) 함수.
    lodging_html: 숙소 안내(lodging19가 만든 접힌 블록) — bk_stay 항목 안 접힌 칸으로 붙임."""
    out = []
    for gk, gt, gs in GROUPS:
        lis = []
        for it in [x for x in BOOK19 if x['group'] == gk]:
            link = a(it['url'], '사이트') if it['url'] else ''
            st = it['status']
            chip = f'<span class="bkst {STATUS_CLASS.get(st, "prep")}">{E(st)}</span>'
            det = it.get('after_html') or ''
            if it['detail_html']:
                det = f'<details class="bkdet"{(' id="'+it["detail_id"]+'"') if it.get("detail_id") else ''}><summary>{E(it["detail_title"])}</summary><div class="bkdetin">{it["detail_html"]}</div></details>'
            if it['id'] == 'bk_stay' and lodging_html:
                det += lodging_html
            wide = ' bkwide' if det else ''
            lis.append(f'<li class="bki{wide}"><input type="checkbox" id="{it["id"]}"><label for="{it["id"]}">'
                       f'<span class="bkh"><b>{E(it["name"])}</b>{chip}</span><span class="bkwhen">{E(it["when"])}</span>'
                       f'<span class="bkhow">{it["how_html"]} {link}</span></label>{det}</li>')
        out.append(f'<details class="bkgrp" id="bk-{gk}"><summary class="bkgt"><span class="bkgtt">{E(gt)}</span><span class="bkgn">{len(lis)}가지</span><small>{E(gs)}</small></summary><ul class="book">{"".join(lis)}</ul></details>')
    return '<div class="bkwrap">' + ''.join(out) + '</div>'


if __name__ == '__main__':
    import html
    print(len(BOOK19), 'items', {g: sum(1 for x in BOOK19 if x['group'] == g) for g, *_ in GROUPS})
    ids = [x['id'] for x in BOOK19]; assert len(ids) == len(set(ids)), 'dup id'
    h = render_book19(html.escape, lambda u, t, c='lnk': f'<a class="{c}" href="{html.escape(u)}" target="_blank" rel="noopener">{t}</a>')
    print(len(h), 'chars')
