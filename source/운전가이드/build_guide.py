# -*- coding: utf-8 -*-
# 일본 렌터카 운전 가이드북 페이지 만들기
#   python3 build_guide.py  →  site/guide.html (+ site/img/)
# 사진 자료: assets/hwy/hwy.json, assets/park/park.json 이 있으면 자동으로 들어감
#   형식: [{"file","title","caption","credit","section"}]
import os, re, json, html, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from figs import FIGS
E = html.escape

# ── 표지판 SVG (signs_src.html에서 가져옴) ──
_sh = open(os.path.join(HERE, 'signs_src.html'), encoding='utf-8').read()
SIGNS = re.findall(r'<div class="c">(<svg.*?</svg>)<div class="n">(.*?)</div><div class="j">(.*?)</div><div class="m">(.*?)</div></div>', _sh, re.S)

def photos(kind):
    p = os.path.join(HERE, 'assets', kind, f'{kind}.json')
    if not os.path.exists(p): return []
    try: lst = json.load(open(p, encoding='utf-8'))
    except Exception as e:
        print('WARN', kind, e); return []
    out = []
    for x in lst:
        src = os.path.join(HERE, 'assets', kind, x['file'])
        if not os.path.exists(src): continue
        dst = f'{kind}_{x["file"]}'
        shutil.copy(src, os.path.join(HERE, 'site', 'img', dst))
        out.append(dict(x, src='img/' + dst))
    return out

def gallery(kind, empty_note):
    lst = photos(kind)
    if not lst:
        return f'<p class="pending">{empty_note}</p>'
    groups = {}
    for x in lst: groups.setdefault(x.get('section') or '', []).append(x)
    out = []
    for sec, xs in groups.items():
        figs = ''.join(f'<figure class="ph"><img src="{E(x["src"])}" alt="{E(x.get("title",""))}" loading="lazy">'
                       f'<figcaption><b>{E(x.get("title",""))}</b><span>{E(x.get("caption",""))}</span>'
                       + (f'<small><a href="{E(x["page"])}" target="_blank" rel="noopener">{E(x.get("credit",""))}</a></small>' if x.get('page') else f'<small>{E(x.get("credit",""))}</small>')
                       + '</figcaption></figure>' for x in xs)
        out.append((f'<h4 class="subh">{E(sec)}</h4>' if sec else '') + f'<div class="phgrid">{figs}</div>')
    return ''.join(out)

def fig(key, n):
    fn, title, steps = FIGS[key]
    ol = ''.join(f'<li>{s}</li>' for s in steps)
    return (f'<figure class="sit" id="fig-{key}"><figcaption class="sit-h"><span class="fno">그림 {n}</span>{E(title)}</figcaption>'
            f'<div class="sit-b"><div class="sit-svg">{fn()}</div>'
            + (f'<ol class="steps">{ol}</ol>' if steps else '') + '</div></figure>')

def jp(ja, ko_pron, mean):
    return (f'<div class="jp"><p class="ja" lang="ja">{ja}</p><p class="pr">{E(ko_pron)}</p><p class="mn">{E(mean)}</p>'
            f'<button type="button" class="cp" data-copy="{E(ja)}">일본어 복사</button></div>')

def chapter(n, cid, color, title, summary, body):
    s = ''.join(f'<li>{x}</li>' for x in summary)
    return (f'<section class="ch c-{color}" id="{cid}"><details class="chd">'
            f'<summary><span class="chn">{n:02d}</span><span class="cht">{E(title)}</span>'
            f'<ul class="sum3">{s}</ul><span class="opn" aria-hidden="true"></span></summary>'
            f'<div class="chb">{body}<button type="button" class="closebtn">접기 ▴ <span>{E(title)}</span></button></div></details></section>')

def table(head, rows, cls=''):
    th = ''.join(f'<th>{h}</th>' for h in head)
    tr = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    return f'<div class="tw"><table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'

def tip(kind, title, text):
    lab = {'warn': '주의', 'tip': '팁', 'ok': '이렇게'}[kind]
    return f'<aside class="note n-{kind}"><b class="nlab">{lab}</b><div><b>{title}</b> {text}</div></aside>'

def img(src, alt, cap):
    return f'<figure class="draw"><img src="img/{src}" alt="{E(alt)}" loading="lazy"><figcaption>{cap}</figcaption></figure>'

J = lambda t: f'<span lang="ja">{t}</span>'

# ───────────────── 장 내용 ─────────────────
CH = []
CH.append(chapter(1, 'prep', 'blue', '출발 전 준비', [
    '운전할 사람은 <b>한국 면허증 + 책자형 국제면허 + 여권</b> 셋 다',
    '내비 목적지는 <b>전화번호·맵코드</b>가 가장 정확', 'ETC 카드가 꽂혀 있는지 출발 전에 확인'],
    table(['준비물', '확인할 점'], [
        ['국제운전면허증', '종이 책자형만(카드형·모바일 X). 발급 1년 이내'],
        ['한국 면허증', '원본. 국제면허와 같이 보여 줌'],
        ['여권', '자동 게이트로 들어오면 도장이 없을 수 있어 <b>유인 심사대에서 도장 받기</b>'],
        ['렌터카 예약', 'Jnet 신치토세공항점 · 예약번호 <code>R0V66VWT</code> · 운전자 전원 픽업 때 등록'],
        ['보험', '면책보상 + 안심보상 와이드(NOC) · ETC 카드 포함']])
    + '<h4 class="subh">우핸들 차 안</h4>'
    + img('cockpit.jpg', '우핸들 차의 깜빡이·와이퍼 레버 위치', '깜빡이는 <b>오른쪽 레버</b>, 와이퍼는 왼쪽 레버(도요타·혼다 등 대부분). 처음에 와이퍼가 켜져도 당황하지 말기.')
    + '<ul class="bl"><li><b>내비</b>: 가게 전화번호를 넣고 나온 이름을 꼭 확인. 숙소는 맵코드 <code>9582538*77</code>.</li>'
      '<li><b>휴대폰 길안내</b>: 구글맵은 조수석이 봅니다. 운전자는 화면을 만지지 않기.</li>'
      '<li><b>ETC 카드</b>: 차에 꽂혀 있는지 확인. 고속도로 요금은 반납 때 한꺼번에 정산.</li></ul>'))

CH.append(chapter(2, 'road', 'red', '도로 기본 규칙 · 상황별 그림', [
    '<b>왼쪽 차로</b>로 달리고, 운전석은 도로 <b>중앙선 쪽</b>', '우회전은 크게(맞은편 먼저), 좌회전은 작게',
    '止まれ·건널목은 <b>바퀴가 완전히 멈추게</b>'],
    tip('warn', '가장 헷갈리는 순간.', '회전한 직후, 그리고 빈 도로에서 출발할 때 한국 습관대로 오른쪽 차로로 들어가기 쉽습니다. 그때마다 “왼쪽 차로”를 소리 내어 확인하세요.')
    + table(['상황', '할 일'], [
        ['빨간불 + 초록 화살표', '화살표 방향으로만 갈 수 있음'],
        ['횡단보도', '건너려는 사람이 보이면 멈춰서 양보. 단속이 엄격함'],
        ['안전벨트', '뒷자리까지 전 좌석'],
        ['음주', '<b>한 모금도 안 됨.</b> 동승자·술을 권한 사람도 처벌'],
        ['휴대폰', '손에 들고 통화·화면 보기 금지. 내비 조작은 조수석이']])
    + '<h4 class="subh">속도 (제한 표지가 없을 때)</h4>'
    + '<div class="speeds"><div><b>60</b><span>km/h</span><p>중앙선이 있는 일반도로</p></div>'
      '<div class="hot"><b>30</b><span>km/h</span><p>중앙선 없는 좁은 길 (2026/9/1부터)</p></div>'
      '<div><b>100</b><span>km/h</span><p>고속도로 (전광판 숫자가 우선)</p></div></div>'
    + '<h4 class="subh">상황별 그림 — 파란 차가 우리 차, 초록이 먼저 가는 차</h4>'
    + '<div class="sits">' + fig('right', 1) + fig('left', 2) + fig('uturn', 3) + fig('stop', 4)
    + fig('rail', 5) + fig('signal', 6) + fig('round', 7) + fig('narrow', 8) + '</div>'))

signs_html = ''.join(f'<div class="sg"><div class="sgi">{svg}</div><p class="sgn">{n}</p><p class="sgj" lang="ja">{j}</p><p class="sgm">{m}</p></div>'
                     for svg, n, j, m in SIGNS)
CH.append(chapter(3, 'signs', 'red', '꼭 알아야 할 표지판', [
    '빨강 = <b>하지 말 것</b> · 파랑 = <b>해도 됨·안내</b> · 노랑 = <b>조심</b>',
    '止まれ(일시정지)는 <b>빨간 역삼각형</b>', '표지 아래 흰 작은 판은 시간·요일 조건'],
    f'<div class="signs">{signs_html}</div>'
    + '<h4 class="subh">표지 아래 작은 판(보조표지) 읽기</h4>'
    + table(['글자', '뜻'], [[J('8-20'), '오전 8시–오후 8시에만 적용'], [J('日曜・休日を除く'), '일요일·공휴일 제외'],
                            [J('ここから'), '여기부터'], [J('ここまで'), '여기까지'], [J('区域内'), '이 구역 전체']])
    + '<p class="src">표지 그림: 이 가이드를 위해 실제 일본 표지 모양대로 다시 그린 그림 (원본: Wikimedia Commons 일본 도로표지, 퍼블릭 도메인)</p>'))

CH.append(chapter(4, 'hwy', 'green', '고속도로 · ETC · 휴게소', [
    '요금소는 <b>보라 ETC 차로</b>로, <b>20km/h 이하</b>', '바가 안 열리면 <b>멈추고, 후진 금지</b>',
    '합류는 가속 차로 끝까지 · 본선은 <b>오른쪽</b>에 있음'],
    '<div class="sits">' + fig('etc', 9) + fig('merge', 10) + '</div>'
    + table(['요금소 표시', '뜻', '우리 차'], [['ETC専用 (보라)', 'ETC 카드 차만', '<b>여기로</b>'], ['ETC/一般', '둘 다 가능', '여기도 됨'],
                                            ['一般 (초록)', '표를 뽑고 나갈 때 현금·카드로', 'ETC가 안 될 때만']])
    + '<ul class="bl"><li><b>SA(サービスエリア)</b>: 주유소·식당이 있는 큰 휴게소. <b>PA(パーキングエリア)</b>: 화장실·매점 정도.</li>'
      '<li>홋카이도는 휴게소 간격이 깁니다. 주유는 <b>절반 남았을 때</b> 미리.</li>'
      '<li>추월은 오른쪽 차로로 하고 끝나면 왼쪽으로 돌아옵니다. 오른쪽 차로에 계속 있으면 위반.</li>'
      '<li>요금은 ETC 카드에 쌓였다가 <b>렌터카 반납 때 정산</b>. 11/3(공휴일)은 일부 구간 ETC 휴일 할인.</li></ul>'
    + '<h4 class="subh">실제 모습</h4>' + gallery('hwy', '사진 준비 중 — 이 자리에 요금소·ETC 차로·휴게소 사진이 들어갑니다.')
    + '<p class="src">출처: <a href="https://www.w-nexco.co.jp/etc/etc_info/safety/kaihei.html" target="_blank" rel="noopener">NEXCO 서일본 — ETC 차로 20km/h 이하</a></p>'))

CH.append(chapter(5, 'winter', 'yellow', '홋카이도 11월 운전', [
    '해는 <b>16:20쯤</b> 짐 · 아침·밤 산길은 얼어 있음', '다리 위·터널 출구·그늘 = <b>블랙아이스</b>',
    '사슴 한 마리 = 뒤에 더 있다 · 핸들 크게 꺾지 않기'],
    tip('warn', '스터드리스여도 미끄러집니다.', '급브레이크·급핸들·급가속을 하지 말고 차간거리를 평소의 2배 이상으로.')
    + '<ul class="bl"><li><b>矢羽根(야바네)</b>: 길가 기둥 위의 빨강·흰 화살표는 <b>길 가장자리</b>를 가리킵니다. 눈으로 차선이 안 보이면 화살표 안쪽으로.</li>'
      '<li><b>사슴(エゾシカ)</b>: 가을 해 질 무렵·밤에 산길에서 뛰어듭니다. 보이면 멈추고 기다리기. 여우는 만지지 않기(기생충).</li>'
      '<li><b>해 진 뒤 산길</b>: 가로등이 거의 없음. 맞은편 차가 없으면 상향등, 오면 바로 하향등.</li>'
      f'<li><b>전광판</b>: {J("凍結注意")} 결빙 주의 · {J("チェーン規制")} 체인 규제 · {J("通行止め")} 통행금지 → 그대로 따르기.</li></ul>'
    + '<h4 class="subh">셀프 주유 (セルフ)</h4>'
    + img('fuel.jpg', '셀프 주유 노즐 색과 요금소 차로', '노즐 색은 보통 <b>빨강 = レギュラー(보통 휘발유)</b>. 렌터카 시엔타급은 레기로(주유구 스티커로 확인).')
    + '<ol class="nl"><li>엔진을 끄고 주유구 쪽(계기판 ◀▶)에 세우기</li><li>결제 방법 고르기: 現金(현금) / クレジット(카드)</li>'
      '<li>유종 <b>レギュラー</b></li><li>양 <b>満タン(가득)</b></li><li><b>검은 정전기 패드를 손바닥으로 누르기</b>(겨울에 특히)</li>'
      '<li>노즐을 끝까지 넣고 당기면 가득 차면 자동으로 멈춤. 더 넣지 않기</li><li>뚜껑 닫고 영수증 받기</li></ol>'))

CH.append(chapter(6, 'park', 'blue', '주차 · 요금표 읽기 · 정산', [
    '길가에 세우지 말고 <b>큰 P 간판</b> 주차장에만', '들어가기 전 <b>최대요금 조건</b>과 <b>현금만인지</b> 확인',
    '11/3은 공휴일 — <b>최대요금 없는 곳</b>이 있음'],
    table(['종류', '간판·특징', '쓸 때'], [
        ['코인파킹 ' + J('コインパーキング'), '노랑·파랑 P, 空(빈자리)/満(만차) 표시. 무인', '시내 식당·관광지'],
        ['공영 주차장 ' + J('市営・町営'), '시·정이 운영. 관광지는 무료도 많음', '오타루 운하 등'],
        ['미치노에키 ' + J('道の駅'), '무료·화장실 24시간', '산길 중간 휴식'],
        ['제휴 주차장 ' + J('提携駐車場'), '산 금액만큼 무료·할인', '삿포로 도심']])
    + img('flap.jpg', '플랩식과 게이트식 코인파킹', '<b>플랩식</b>: 칸에 세우면 바닥 판이 올라와 잠김 → 나갈 때 칸 번호로 정산. <b>게이트식</b>: 입구에서 주차권 → 출구에서 정산.')
    + '<h4 class="subh">요금표 읽는 법 (설명용 예시)</h4>'
    + img('parking.jpg', '예시 코인파킹 요금표', '직접 만든 예시 요금표. 실제 숫자는 주차장마다 다릅니다.')
    + table(['요금표 문구', '뜻'], [
        [J('30分 200円'), '30분마다 200엔씩'], [J('昼間最大 / 夜間最大'), '낮/밤 시간대 안에서는 그 금액까지만'],
        [J('入庫後24時間最大'), '들어온 때부터 24시간 안에 합계 그 금액까지'], [J('当日最大'), '그날 자정까지만'],
        [J('最大料金は繰り返し適用されません'), '최대요금은 <b>한 번만</b>. 넘으면 다시 시간요금'],
        [J('土・日・祝日は最大料金の適用はありません'), '토·일·공휴일 최대요금 없음 (11/3!)'],
        [J('現金のみ / 千円札のみ'), '현금만 / 1,000엔 지폐만']], 'jpt')
    + '<h4 class="subh">계산해 보기 (위 예시 요금표: 낮 30분 200엔, 낮 최대 1,200엔)</h4>'
    + '<div class="calc"><div><span>평일 12–15시 (3시간)</span><b>1,200엔</b><small>200×6=1,200 → 낮 최대와 같음</small></div>'
      '<div class="hot"><span>공휴일 10–18시 (8시간)</span><b>3,200엔</b><small>최대요금 없음 → 200×16</small></div>'
      '<div><span>평일 21시–다음 날 9시</span><b>800엔</b><small>밤 최대 400 + 아침 8–9시 400</small></div></div>'
    + '<h4 class="subh">세우고 나가는 순서</h4>'
    + '<ol class="nl"><li>“空” 표시 보고 들어가 빈 칸에 <b>후진으로</b> 세우기</li><li>플랩식은 <b>칸 번호 사진</b>, 게이트식은 주차권을 지갑에</li>'
      '<li>정산기(精算機)에 칸 번호 입력 또는 주차권 → 금액 → 결제 → 領収書(영수증)</li><li>플랩이 내려간 것(차단기가 올라간 것)을 <b>눈으로 확인</b>하고 출발</li></ol>'
    + '<h4 class="subh">그림으로 보는 순서 · 플랩식과 게이트식</h4>'
    + img('park_draw_flap_steps.png', '플랩식 코인파킹 이용 순서', '플랩식: 바닥 잠금판이 올라와 차를 잡아 둠. 정산하면 내려감 (설명용 그림)')
    + img('park_draw_gate_steps.png', '게이트식 주차장 이용 순서', '게이트식: 들어갈 때 주차권, 나갈 때 정산하면 차단기가 올라감 (설명용 그림)')
    + img('park_draw_fee_table.png', '요금표 읽는 법 그림', '요금판에서 볼 곳 (설명용 그림)')
    + '<h4 class="subh">실제 표지·간판 모습</h4>' + gallery('park', '사진 준비 중 — 이 자리에 코인파킹 간판·요금판·정산기 사진이 들어갑니다.')
    + '<p class="src">출처: <a href="https://kuruma-news.jp/post/805881" target="_blank" rel="noopener">쿠루마노뉴스 — 코인파킹 최대요금 표시 주의</a></p>'))

CH.append(chapter(7, 'eat', 'green', '식당에서 주차하는 법', [
    '출발 전 <b>타베로그 「駐車場」 칸</b> 확인', '시골 식당은 대부분 가게 앞 무료, 시내는 근처 코인파킹',
    '<b>지정 번호 칸</b>이 있으면 그 칸에만'],
    table(['문구', '뜻', '할 일'], [
        [J('有 / 無料駐車場あり / 5台'), '있음 / 무료 / 5대', '가게 앞 간판 따라 들어감'],
        [J('無 / 近くにコインパーキングあり'), '없음 / 근처 코인파킹', '구글맵에서 「コインパーキング」 검색'],
        [J('お客様専用駐車場'), '손님 전용', '식사 안 하면 세우지 않기'],
        [J('第2駐車場'), '제2주차장(떨어진 곳)', '간판·지도에 위치'],
        [J('○番'), '지정 번호 칸', '<b>그 번호 칸에만</b>. 옆 가게 칸은 견인되기도'],
        [J('提携駐車場 / 駐車券'), '제휴 주차장 / 할인권', '계산할 때 “駐車券ありますか?”'],
        [J('無断駐車禁止 / 罰金'), '무단 주차 금지 / 벌금', '다른 가게·집 주차장']], 'jpt')
    + '<ol class="nl"><li>타베로그 「駐車場」 칸</li><li>구글맵 가게 사진에서 주차장·입구 모습</li><li>있으면 내비를 가게 전화번호로, 없으면 근처 코인파킹을 목적지로</li></ol>'
    + tip('tip', '줄 서는 인기 식당.', '주차장이 차면 길에서 기다리지 말고 한 바퀴 돌거나 코인파킹으로.')
    + jp('駐車場はありますか？', '주샤쥬와 아리마스까?', '주차장 있나요? — 예약 전화할 때 같이 묻기')))

CH.append(chapter(8, 'acc', 'red', '사고 · 고장이 나면', [
    '작은 사고도 <b>경찰 110</b>에 신고 (안 하면 보험이 안 될 수 있음)', '다친 사람이 있으면 <b>119</b>',
    '그 자리에서 <b>렌터카 회사</b>에 연락 · 현장에서 따로 합의 금지'],
    '<ol class="nl"><li>비상등, 차를 길 가로. 고속도로는 가드레일 밖으로 피하고 차 뒤에 삼각대</li>'
    '<li>다친 사람 → <b>119</b>, 사고 신고 → <b>110</b>. “事故です” + 위치(내비·구글맵 주소)</li>'
    '<li>렌터카 회사: 계약서·차 안 스티커의 사고 연락처 (Jnet 예약 문의 <code>0120-302-554</code>, 사고 전용 번호는 계약서 확인 — 직접 보지 못함)</li>'
    '<li>상대가 있으면 이름·연락처·차량번호·보험사, 현장·차 사진 여러 장</li>'
    '<li>펑크·방전·눈길에 빠짐 같은 고장도 먼저 렌터카 회사로</li></ol>'
    + jp('事故です。場所はここです。', '지코데스. 바쇼와 코코데스', '사고입니다. 장소는 여기예요 (화면 보여주기)')))

CH.append(chapter(9, 'ret', 'blue', '반납 (11/6)', [
    '<b>10:05까지</b> 가득 주유해서 Jnet 영업소에', '반납 때 ETC 요금 정산', '셔틀로 국제선 터미널 (LJ204 12:15)'],
    '<ul class="chk"><li>영업소 근처 주유소에서 <b>満タン</b>, 영수증 챙기기</li><li>차 안 쓰레기·짐·충전기 확인</li>'
    '<li>ETC 요금 정산(카드·현금)</li><li>출발 때 찍은 흠집 사진과 비교, 새 흠집은 그 자리에서 말하기</li></ul>'
    + jp('国際線ターミナルまでお願いします', '고쿠사이센 타-미나루마데 오네가이시마스', '국제선 터미널까지 부탁합니다')))

PHRASES = [('予約しています。R0V66VWTです。', '요야쿠시테 이마스. R0V66VWT 데스', '렌터카 픽업 — 예약했습니다'),
           ('レギュラー満タンでお願いします', '레기로 만탄데 오네가이시마스', '주유 — 레기로 가득 부탁합니다'),
           ('駐車場はありますか？', '주샤쥬와 아리마스까?', '주차장 있나요?'),
           ('どこに駐めたらいいですか？', '도코니 토메타라 이이데스까?', '어디에 세우면 돼요?'),
           ('駐車券ありますか？', '주샤켄 아리마스까?', '주차 할인권 있나요?'),
           ('ETCカードが読み取れません', '이티씨 카도가 요미토레마센', 'ETC 카드가 안 읽혀요'),
           ('事故です。場所はここです。', '지코데스. 바쇼와 코코데스', '사고입니다. 여기예요'),
           ('この道は一方通行ですか？', '코노 미치와 잇포츠코 데스까?', '이 길 일방통행인가요?'),
           ('国際線ターミナルまでお願いします', '고쿠사이센 타-미나루마데 오네가이시마스', '국제선 터미널까지')]
CH.append(chapter(10, 'jp', 'yellow', '바로 쓰는 일본어 한 줄', [
    '화면을 그대로 보여 줘도 됩니다', '복사 버튼으로 일본어를 붙여 넣기', '숫자·주소는 구글맵 화면으로'],
    '<div class="jps">' + ''.join(jp(a, b, c) for a, b, c in PHRASES) + '</div>'))

SOURCES = [('일본정부관광국 — 일본의 렌터카', 'https://www.japan.travel/ko/plan/getting-around/cars/'),
           ('구마니치니치신문(교도통신) — 생활도로 법정속도 30km/h', 'https://kumanichi.com/articles/2031071'),
           ('NEXCO 서일본 — ETC 차로 20km/h 이하', 'https://www.w-nexco.co.jp/etc/etc_info/safety/kaihei.html'),
           ('JAF Mate — 교통규칙 퀴즈(우회전 화살표 신호와 유턴)', 'https://jafmate.jp/safety/traffic_rules_quiz_20230524.html'),
           ('시가현 경찰 — 환상교차로(로터리) 통행 방법', 'https://www.pref.shiga.lg.jp/police/pa27/15837.html'),
           ('쿠루마노뉴스 — 코인파킹 최대요금 표시', 'https://kuruma-news.jp/post/805881'),
           ('일본 도로표지 — Wikimedia Commons (퍼블릭 도메인)', 'https://commons.wikimedia.org/wiki/Category:Road_signs_in_Japan')]

TOC = [('prep', 'blue', '출발 전'), ('road', 'red', '도로 규칙·그림'), ('signs', 'red', '표지판'), ('hwy', 'green', '고속도로·ETC'),
       ('winter', 'yellow', '11월 겨울길'), ('park', 'blue', '주차·요금표'), ('eat', 'green', '식당 주차'),
       ('acc', 'red', '사고·고장'), ('ret', 'blue', '반납'), ('jp', 'yellow', '일본어 한 줄')]

page = open(os.path.join(HERE, 'tpl.html'), encoding='utf-8').read()
toc = ''.join(f'<a class="tc c-{c}" href="#{i}"><span>{n+1:02d}</span>{E(t)}</a>' for n, (i, c, t) in enumerate(TOC))
src = ''.join(f'<li><a href="{u}" target="_blank" rel="noopener">{E(t)}</a></li>' for t, u in SOURCES)
side = ''.join(f'<a class="c-{c}" href="#{i}"><span>{n+1:02d}</span>{E(t)}</a>' for n, (i, c, t) in enumerate(TOC))
page = page.replace('{{SIDE}}', side).replace('{{TOC}}', toc).replace('{{CHAPTERS}}', ''.join(CH)).replace('{{SOURCES}}', src)
os.makedirs(os.path.join(HERE, 'site', 'img'), exist_ok=True)
open(os.path.join(HERE, 'site', 'guide.html'), 'w', encoding='utf-8').write(page)
print('ok', len(page), 'hwy', len(photos('hwy')), 'park', len(photos('park')))
