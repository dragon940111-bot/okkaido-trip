# -*- coding: utf-8 -*-
# v19.2 숙소 체크인·가는 길 (FlexCella N17-B)
# 출처: 호스트 체크인 안내 PDF 2개 (사용자가 11/1에 전달)
#   찾아가는 길  https://cohabit-home.net/housemanual/how2FLX17.pdf   (6쪽)
#   체크인·주차  https://cohabit-home.net/housemanual/fx/N17-B_Key_.pdf (5쪽)
# + 숙소 재조사 보고서(03_숙소·렌터카 조사/Sapporo_13_Stays_Recheck_20261028.csv, 10/28 조회)
# + 운전 경로: OSRM(2026/11/1) — 실제는 10–20% 더 걸린다고 보고 여유를 붙임
# 보안: 우편함 다이얼 번호·Wi-Fi 비밀번호는 페이지에 쓰지 않음(PDF 링크로만 안내). 코드가 찍힌 PDF 쪽은 이미지로도 넣지 않음.

PDF_WAY = 'https://cohabit-home.net/housemanual/how2FLX17.pdf'
PDF_KEY = 'https://cohabit-home.net/housemanual/fx/N17-B_Key_.pdf'
ADDR_JA = '札幌市東区北17条東2丁目4-32'
MAPCODE = '9582538*77'

def _a(href, text):
    return f'<a class="lnk" href="{href}" target="_blank" rel="noopener">{text}</a>'

STAY_TITLE = '숙소 FlexCella N17-B · 가는 길 · 주차 · 체크인'

STAY_SUMMARY_HTML = (
    f'<span lang="ja">フレックスセラ N17-B</span> · <span lang="ja">{ADDR_JA}</span> · '
    '체크인 16:00부터 / 체크아웃 11:00 · <b>B 전용 무료 주차 1칸</b> · 지하철 <span lang="ja">北18条</span>역 걸어서 약 11분'
    f'<span class="staylinks">{_a(PDF_WAY, "찾아가는 길 PDF")}{_a(PDF_KEY, "체크인·주차 PDF")}</span>'
)

STAY_IMAGES = [
    ('stay_building', '숙소 건물 (FLEX CELLA 글자, 오른쪽 끝이 N17-B) · 안내 PDF', 'stay_way'),
    ('stay_entrance', 'A·B 현관이 따로 있음 — 문 위의 B를 확인 · 안내 PDF', 'stay_way'),
    ('stay_walk', '걸어서 올 때 표지: URVAN HOTEL MARUKO 앞 신호 건너 오른쪽 → 진입 금지 표지에서 왼쪽 · 안내 PDF', 'stay_way'),
    ('stay_parking', 'B 전용 주차 칸 (빨간 테두리, 건물 옆) · 안내 PDF', 'stay_car'),
    ('stay_oneway', '건물 양옆 두 길은 일방통행 (화살표 방향으로만) · 안내 PDF', 'stay_car'),
]

def _fig(key, cap):
    return f'<figure><img src="img/{key}.jpg" alt="{cap}" loading="lazy"><figcaption>{cap}</figcaption></figure>'

def _figs(sec):
    f = [_fig(k, c) for k, c, s in STAY_IMAGES if s == sec]
    return f'<div class="stayfigs n{len(f)}">{"".join(f)}</div>' if f else ''

STAY_SECTIONS = [
 dict(id='stay_car', title='렌터카로 가는 길 · 주차', html=(
  '<h5>11/2 일정대로 갈 때</h5>'
  '<p>공항 Jnet → 도마코마이 → 시코쓰호 → 찻카루 → <span lang="ja">木多郎</span>(17:30 저녁) → 숙소 19:00. '
  '마지막 구간 <span lang="ja">木多郎 澄川本店</span> → 숙소는 약 13km, <b>20–25분</b>(<span lang="ja">五輪通</span>·<span lang="ja">真駒内</span> 쪽 길로 시내에 들어와 '
  '<span lang="ja">創成川通</span>를 따라 북쪽으로).</p>'
  '<h5>공항에서 바로 갈 때 (날씨가 나빠 시코쓰호를 뺄 때 등)</h5>'
  '<p>Jnet 신치토세공항점 → 숙소 약 45km, <b>약 50분–1시간 10분</b>(지도 계산 42분 + 여유, 저녁 퇴근길엔 더). '
  '지도 계산 경로는 <span lang="ja">国道36号</span> → <span lang="ja">月寒通</span> → <span lang="ja">創成川通</span>이고, 내비가 고속도로(<span lang="ja">道央道</span>)로 안내할 수도 있음.</p>'
  '<h5>내비에 넣을 것</h5>'
  f'<ul><li>맵코드 <b class="num">{MAPCODE}</b> (안내 PDF) — 내비에 맵코드 메뉴 있으면 이게 제일 정확함.</li>'
  f'<li>또는 주소 <span lang="ja" class="num">{ADDR_JA}</span> (건물 이름 <span lang="ja">フレックスセラ N17</span>)</li>'
  '<li>호스트 전화번호로 검색하면 안 됨 — 관리 회사로 안내될 수 있음.</li></ul>'
  '<h5>마지막 몇 블록</h5>'
  '<ul><li><b>건물 양옆 두 길은 일방통행</b>(서쪽 길은 북쪽으로만, 동쪽 길은 남쪽으로만). 표지 꼭 보기.</li>'
  '<li>지도 계산 경로로는 <span lang="ja">創成川通</span>를 북쪽으로 → <span lang="ja">環状通</span>에서 오른쪽 → 서쪽 길로 북쪽 약 300m → 오른쪽 → 다시 오른쪽으로 조금 가면 도착. '
  '마지막 골목 순서는 확인 못 함 → 내비랑 일방통행 표지 따라가기.</li>'
  '<li>빨간 원에 흰 가로 막대 표지(진입 금지) 있는 쪽으로는 들어가면 안 됨.</li></ul>'
  + _figs('stay_car') +
  '<h5>주차</h5>'
  '<ul><li><b>B 전용 무료 주차 1칸</b>: 건물 옆, 위 사진 빨간 칸. 칸 밖으로 안 튀어나오게 세우기.</li>'
  '<li>안내 사진에 SUV(스바루 XV급)가 서 있어서 시엔타급도 들어갈 듯함(칸 크기는 확인 못 함).</li>'
  '<li><b>길가 주차 금지</b>: 길에 세워서 생긴 문제는 호스트가 안 봐줌. 차 더 있으면 근처 코인 주차장(안내 PDF 지도에 표시) 쓰기.</li>'
  '<li>눈 오면 주차 칸에 눈 쌓여 있을 수 있음. 비치된 눈삽으로 치우고, 눈은 <b>도로·이웃 땅에 버리면 안 됨</b>.</li>'
  '<li>11/2 밤 <span lang="ja">しろくま</span>는 차 숙소에 두고 지하철로 감. 11/6은 8:15 체크아웃하고 차로 공항(DAY 5).</li></ul>'
 )),
 dict(id='stay_way', title='찾아가는 길 (지하철·걸어서)', html=(
  f'<p class="stayaddr"><span lang="ja">〒065-0017 {ADDR_JA} フレックスセラ N17-B</span><br>'
  f'4-32, Kita 17-jo Higashi 2-chome, Higashi-ku, Sapporo · 맵코드 <span class="num">{MAPCODE}</span></p>'
  '<h5><span lang="ja">北18条</span>역(지하철 <span lang="ja">南北線</span>)에서 걸어서 약 11분</h5>'
  '<ol class="staysteps">'
  '<li>개찰구 나오면 앞에 2번 엘리베이터 → 타고 올라감.</li>'
  '<li>나와서 <b>왼쪽</b>으로, 첫 교차로까지.</li>'
  '<li>신호등에서 <b>오른쪽</b>으로 꺾어서 직진.</li>'
  '<li>신호 두 개 지나서 계속 직진.</li>'
  '<li>다음 신호 <b>6차선 큰길</b>도 건너서 직진.</li>'
  '<li>신호 하나 더 지나면 다음 신호 앞에 <b>URVAN HOTEL MARUKO</b> 호텔 → 그 신호 건너서 <b>오른쪽</b>.</li>'
  '<li>진입 금지 표지(빨간 원에 흰 막대) 보이면 <b>왼쪽</b>.</li>'
  '<li>몇 미터 가면 왼쪽에 <b>FLEX CELLA</b> 건물. 입구가 A·B로 나뉘어 있으니 문 위 <b>B</b> 확인.</li>'
  '</ol>'
  + _figs('stay_way') +
  '<h5>밤에 스스키노 갈 때 · 돌아올 때</h5>'
  '<p>위 길을 거꾸로 걸어 <span lang="ja">北18条</span>역 → <span lang="ja">南北線</span> <span lang="ja">真駒内</span> 방면 → <span lang="ja">すすきの</span> 약 8분. '
  '돌아올 땐 <span lang="ja">麻生</span> 방면 타고 <span lang="ja">北18条</span>에서 내림.</p>'
  '<h5>참고: 렌터카 없이 공항에서 전철로 올 때 (안내 PDF)</h5>'
  '<p>JR <span lang="ja">新千歳空港</span>역 → <span lang="ja">快速エアポート</span> → JR <span lang="ja">札幌</span>역 → 초록색 표시를 따라 지하철 <span lang="ja">南北線</span>으로 갈아타기 → '
  '<b>2번 승강장 <span lang="ja">麻生</span> 방면</b> → <span lang="ja">北18条</span>에서 내림.</p>'
 )),
 dict(id='stay_in', title='체크인 · 체크아웃', html=(
  '<ul>'
  '<li><b>체크인 16:00부터 · 체크아웃 11:00</b> (Airbnb 숙소 정보, 10/28 조회 — 예약 확인 화면에서 한 번 더 확인)</li>'
  '<li><b>미리: 숙박자 명부 온라인 제출</b> — 입실 비밀번호 받으려면 예약 확정 1시간 뒤 온 메일에서 명부를 미리 내야 함(찾아가는 길 PDF). 냈는지는 확인 못 함.</li>'
  '</ul>'
  '<h5>들어가는 법 (체크인·주차 PDF)</h5>'
  '<ol class="staysteps">'
  '<li>열쇠는 <b>B 현관문 옆 우편함(MAILBOX)</b> 안에 있음.</li>'
  '<li>우편함 다이얼을 PDF 순서대로(왼쪽·왼쪽·오른쪽) 맞춰서 열기. <b>번호는 체크인·주차 PDF 2쪽</b>(여기엔 안 적음).</li>'
  '<li>열쇠는 줄·카라비너로 우편함에 묶여 있음. <b>줄째로 당겨서</b> 현관 문 열기.</li>'
  '<li>문 열리면 <b>열쇠 다시 우편함에 넣고 잠그기.</b></li>'
  '</ol>'
  '<ul>'
  '<li>Wi-Fi는 체크인·주차 PDF 4쪽(여기엔 안 적음).</li>'
  '<li>체크아웃 방법(열쇠·쓰레기)은 PDF에 없음 — Airbnb 메시지나 숙소 안 안내문 확인.</li>'
  '<li>연락: 기본은 Airbnb 메시지, 급할 때 호스트(COHABIT HOME) <span class="num">+81-11-215-1939</span> (체크인·주차 PDF)</li>'
  '</ul>'
 )),
 dict(id='stay_warn', title='주의', html=(
  '<ul>'
  '<li><b>열쇠 우편함에서 절대 빼지 말기</b>(카라비너도 풀지 말기). 잃어버리면 수만 엔 나옴.</li>'
  '<li>A·B 입구 헷갈리지 않게 문 위 글자 확인.</li>'
  '<li>길가 주차 금지, 건물 양옆 길은 일방통행.</li>'
  '<li>패널히터라 늦게 데워진다는 후기 있음. 도착 전에 Airbnb 메시지로 히터 미리 켜 달라고 하면 좋음.</li>'
  '<li>열쇠 문제로 1시간 반 기다렸다는 후기(2025/8) 있음. PDF 폰에 저장해 두고, 문제 생기면 바로 메시지·전화.</li>'
  '<li>세탁기만 있고 건조기 없음. 실내 흡연 금지.</li>'
  '</ul>'
 )),
]
