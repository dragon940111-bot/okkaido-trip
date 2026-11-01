# 대안 상세 일정 데이터 작성 규칙 (공통)

## 여행 기본 정보
- 홋카이도 맛집 투어, 3명 (동재·현준·경일), 렌터카 4WD 스터드리스 (Jnet 신치토세공항점).
- 숙소: FlexCella North17 B, 삿포로 北18条역 근처 (지하철 南北線). 무료 주차 1대. 지도 출발점 = 숙소.
- 날짜·요일: 11/2(월) · **11/3(화, 공휴일 文化の日)** · 11/4(수) · 11/5(목) · 11/6(금, 출국). 오늘은 2026/10/31.
- 일몰 약 16:20. 11월 홋카이도는 산길 결빙, 해 진 뒤 사슴·블랙아이스 주의.
- 화면은 한국어. 일본 가게 이름은 원문 그대로(name) + 한글 읽기(ko). 문장은 자연스러운 일상 한국어, "~입니다/~합니다" 체.

## 금지 사항 (반드시 지킬 것)
- 예약 확정·결제·가게에 메시지/폼 보내기 금지. 로그인·개인정보 입력 금지. CAPTCHA 풀지 말 것.
- **WebFetch 도구 사용 금지** (사용자가 거부함). WebSearch는 써도 됨.
- Chrome: 반드시 `tabs_create_mcp`로 **자기 탭을 새로 만들어** 쓰고, 끝나면 `tabs_close_mcp`로 닫을 것. 다른 탭(특히 1535386950, 1535387754)은 건드리지 말 것.
- 사용자 이메일 등 개인정보를 외부에 보내지 말 것.
- 이 폴더(`build/`) 안의 기존 파일(data2.py, build2.py, photos.json 등)은 **수정하지 말 것**. 자기 결과 파일만 쓸 것.

## 조사 방법
1. **타베로그**: Chrome에서 자기 탭을 만들고 `https://tabelog.com/hokkaido/` 아무 페이지로 이동한 뒤 `javascript_tool`로 같은 출처 fetch + DOMParser를 씁니다 (curl은 403). 아래 함수를 먼저 정의하세요. 출력이 약 2,000자에서 잘리니 4곳씩 나눠 조회.
```js
window.tbList = async (u) => { const t = await (await fetch(u)).text(); const d = new DOMParser().parseFromString(t,'text/html');
 return [...d.querySelectorAll('.list-rst')].map(e=>{const a=e.querySelector('.list-rst__rst-name-target'); return [a?.textContent.trim(), (a?.getAttribute('href')||'').replace('https://tabelog.com',''), e.querySelector('.c-rating__val')?.textContent.trim(), e.querySelector('.list-rst__rvw-count-num')?.textContent.trim(), e.querySelector('.list-rst__area-genre')?.textContent.replace(/\s+/g,' ').trim(), e.querySelector('.list-rst__holiday-text')?.textContent.trim()].join(' | ')}); };
window.tbInfo = async (p) => { const t = await (await fetch('https://tabelog.com'+p)).text(); const d = new DOMParser().parseFromString(t,'text/html');
 const g = s => d.querySelector(s)?.textContent.replace(/\s+/g,' ').trim(); const rows = {};
 d.querySelectorAll('.rstinfo-table__table tr').forEach(tr=>{const k=tr.querySelector('th')?.textContent.trim(); const v=tr.querySelector('td')?.textContent.replace(/\s+/g,' ').trim(); if(k) rows[k]=v;});
 return {name:g('.display-name'), rating:g('.rdheader-rating__score-val-dtl'), rv:g('.rdheader-rating__review-target .num'), genre:rows['ジャンル'], hours:(rows['営業時間']||'').slice(0,400), price:rows['予算'], pay:(rows['支払い方法']||'').slice(0,60), award:g('.rstinfo-table__award')||g('.rdheader-award'), addr:(rows['住所']||'').slice(0,60), resv:rows['予約可否']}; };
window.cl = s => (s||'').replace(/営業時間・定休日は変更となる場合がございますので、ご来店前に店舗にご確認ください。/g,'').replace(/大きな地図を見る 周辺のお店を探す.*/,'').replace(/\s+/g,' ').trim();
window.tbS = async p => { const o = await tbInfo(p); return [o.name,o.rating,o.rv,(o.genre||'').slice(0,25),cl(o.hours).slice(0,200),(o.price||'').slice(0,25),(o.pay||'').includes('カード可')?'card':'nocard',cl(o.addr).replace('北海道','').slice(0,22),(o.resv||'').slice(0,6),(o.award||'').slice(0,40)].join(' | '); };
```
   - 지역 랭킹: `https://tabelog.com/hokkaido/<A코드>/<세부코드>/rstLst/?SrtT=rt` (2페이지는 `rstLst/2/?SrtT=rt`). 장르: `.../rstLst/ramen/?SrtT=rt` 등.
   - 리뷰(최근 평)를 보고 싶으면 `p + 'dtlrvwlst/?srt=visit'` 페이지에서 `.rvw-item__rvw-comment` 등을 짧게 뽑기.
2. **구글 평점·영업시간**: `mcp__widgets__places_search` (한 번에 최대 10개 쿼리, 쿼리마다 max_results 1). 결과의 `special_days`에 11/3 등이 있으면 그날 시간이 다름 → `weekday_hours`를 확인. 결과는 지도 카드로 보여줄 필요 없음(사용자에게 안 보임).
3. **운전 시간**: `curl -s "https://router.project-osrm.org/route/v1/driving/LON1,LAT1;LON2,LAT2?overview=false"` → duration(초)·distance(m). 실제 일본 도로는 OSRM보다 10–20% 더 걸리니 반올림해 보수적으로.
4. 공식 사이트·인스타 공지(11월 휴무일, 시즌 종료)는 WebSearch로 확인. 11월은 니세코·소운쿄 비수기라 휴업이 많으니 꼭 확인.

## 맛집 선정 기준 (상세 일정과 같은 조건)
- 타베로그 3.5 이상 + 리뷰 충분(대략 100건 이상), 구글 4.0 이상 + 리뷰 수백 건 이상을 기본으로. 지역 최고점이 낮으면(예: 3.4대) 그 지역 상위권에서 고름.
- **그날·그 시간에 실제로 영업**: 요일 휴무, 공휴일 규칙(11/3 공휴일 영업/휴무, 다음 날 대체 휴무), 11월 부정기 휴무, 시즌 종료, 라스트오더, 재료 소진 마감까지 확인.
- 끼니마다 **메인 1곳 + 대안 3–5곳**. 대안은 장르를 섞고(같은 장르만 5개 X), 동선에서 크게 벗어나지 않게.
- 메인은 동선·시간이 가장 잘 맞고 평이 가장 좋은 곳. 원래 일정(PDF) 장소가 있으면 우선.
- 디저트·카페·간식 슬롯도 같은 기준.

## 결과 파일 형식
`build/scen/scen_<글자>.py` 하나에 아래 변수들을 정의 (파이썬 문법 오류 없게, `python3 -c "import ast;ast.parse(open(f).read())"`로 확인).

```python
NEW_R = {   # 새 맛집만. 키는 소문자 영문+숫자, 대안 글자 접두사 (예: 'a_tonta', 'g_kitanogurume')
  'a_xxx': dict(
    name='ジンギスカン白樺', ko='징기스칸 시라카바', genre='양념 징기스칸',
    area='오비히로 기요카와초 (오비히로역에서 차로 25분, 주차 있음)',
    g='4.4', gn='1,107', t='3.66', award='',          # 타베로그 百名店 등 있으면
    hours='화–일 11:00–14:00 (재료 소진 시 종료)', closed='월요일 (공휴일이면 다음 날) · 11월 휴무 2·9·10·16·17·24·30일',
    price='램 ¥950/1인분 · 머튼 ¥730 (2026/9 리뷰) · 1인 ¥2,000–3,000',
    why='추천 이유 2–4문장: 무엇이 유명한지, 평점·리뷰 수, 최근 리뷰(연/월 표기)에서 반복되는 칭찬과 단점.',
    tip='예약 가능 여부 · 현금/카드 · 줄 · 주차 · 주문 팁.',
    tb='/hokkaido/A0111/A011101/1000130/', q='ジンギスカン白樺 帯広本店', pid='구글 place_id(있으면)'),
}
NEW_A = {   # 새 볼거리 (기존 A 키는 그대로 재사용 가능)
  'a_kofuku': dict(name='幸福駅 (고후쿠역)', area='오비히로 남쪽 고후쿠초', q='幸福駅 帯広', pid='', g='4.1', gn='315',
     facts=['폐역 플랫폼·나무 역사, 무료 · 24시간', '...', '...']),   # 3–4줄, 요금·시간·주차·11월 상황
}
SCN = {
 'A': dict(
   days=[dict(
     day=1,                       # 여행 날짜 인덱스: 11/2=0, 11/3=1, 11/4=2, 11/5=3, 11/6=4
     date='11/3', dow='화·공휴일',
     title='오비히로·도카치 당일치기: 징기스칸 · 정원 · 롯카테이 · 부타동',
     km='약 430km', drive='운전 약 5시간 50분',
     wx='오비히로 맑음 3–13℃ (10/31 예보) · ...',
     why='이렇게 짠 이유 2–3문장',
     routes=[('숙소 → 시라카바', '北18条駅', 'ジンギスカン白樺 帯広本店', []), ...],   # 구글맵 경로 버튼: (라벨, 출발 검색어, 도착 검색어, [경유지 검색어])
     items=[
       # (시각, 종류, 참조, 제목, 보조설명 또는 None, 지도번호 또는 None, 대안키 리스트 또는 None)
       ('09:00','move',None,'출발 → 오비히로 (약 2시간 50분, 道央道·道東道)','占冠PA에서 쉬어 가기 · 통행료 편도 ¥4,860',None,None),
       ('12:00','eat','a_shirakaba','점심: 양념 징기스칸','예약 불가 · 공휴일이라 11:30 전 도착 권장','1',['a_jhokkaido','a_kashiwa','biba','a_indian']),
       ('13:15','see','a_kofuku','고후쿠역 · 행복의 역','무료','2',None),
       ('16:00','same','day2','21:00 야식 グルマンズいとう는 그대로','DAY 2 시간표와 같음',None,None),   # 바뀌지 않는 부분은 kind='same', ref='day1'..'day5'
     ]),
   ],
   status={'a_shirakaba':'11/3(화·공휴일) ✅ 11:00–14:00', 'saimi':'11/4(수) ✅ 11:00–15:15', ...},  # 이 대안에 나오는 모든 맛집(메인·대안, 기존 키 포함)의 그날 영업 한 줄
   notes={'a_jhokkaido':'이 가게로 바꾸면 … (일정이 어떻게 바뀌는지 1–2문장)', ...},              # 모든 대안 맛집
   map=[('lodging',43.0866,141.3411,'숙소'), ('shirakaba',42.86,143.15,'시라카바 징기스칸'), ...], # 지도에 찍을 순서(숙소 출발·도착 포함) + 좌표 + 라벨. 번호는 items의 지도번호와 일치
   summary_plan=[('09:00','출발 → ...'), ...],   # 위쪽 요약 시간표(짧게 6–9줄)도 새 일정에 맞게
   out=['麺屋 彩未', ...], inn=['白樺 징기스칸', ...],   # 빠지는 곳 / 새로 들어오는 곳
   other='전체 영향 1–2문장', cost='부담 한 줄',
 )
}
```
- kind: `move`(이동, 제목에 소요시간·도로), `eat`(ref=맛집 키, 두 곳이면 튜플), `see`(ref=볼거리 키), `stay`(숙소·렌터카), `note`(기타), `same`(그대로인 구간; ref='day1'~'day5').
- 기존 키(아래 existing_R.txt)를 재사용할 때는 NEW_R에 다시 쓰지 말고 키만 쓰되, `status`에 그날 영업 줄을 꼭 넣을 것.
- 시간표는 상세 일정처럼 **이동 줄까지 모두** 넣고, 시각은 운전 시간과 영업시간에 맞게 계산. 라스트오더·마감 전에 도착하는지 확인.
- 확인 못 한 정보는 지어내지 말고 "(미확인)" 또는 "방문 전 확인"이라고 쓸 것. 가격엔 출처 시점(예: 2026/9 리뷰, 공식)을 붙임.

## 참고 파일
- `build/scen/existing_R.txt`: 기존 맛집·볼거리·상세 일정·외곽 지역 메모 (이미 조사한 데이터 — 재확인 후 재사용).
- `build/scen/existing_SCEN.txt`: 지금 대안 A–G의 요약 데이터.
