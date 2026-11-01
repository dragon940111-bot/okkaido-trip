# -*- coding: utf-8 -*-
import os, json, html, urllib.parse
from data import R, A, DAYS, DROPPED, REGIONS, ALTS
E = html.escape
HERE = os.path.dirname(os.path.abspath(__file__))
META = json.load(open(os.path.join(HERE, 'img/meta.json')))
HAVE = {k for k in META if os.path.exists(os.path.join(HERE, f'img/{k}.jpg'))}
KANJI = dict(sushi='鮨', jingisukan='羊', yakitori='鶏', omucurry='咖', yakitori2='酒', soba='蕎', kaisendon='海', yakiniku='牛',
             hamburg='洋', muroyakitori='串', butadon='豚', sweets='菓', spaghetti='伊', misoramen='麺', kakuni='煮', asahiramen='麺',
             napolitan='喫', castella='菓', soft='乳', soupcurry='湯', cheesecake='菓', tendon='天', curryramen='麺')
USED = set()

def gsearch(q, pid=None):
    u = 'https://www.google.com/maps/search/?api=1&query=' + urllib.parse.quote(q)
    if pid: u += '&query_place_id=' + pid
    return u
def gnav(q, pid=None):
    u = 'https://www.google.com/maps/dir/?api=1&travelmode=driving&destination=' + urllib.parse.quote(q)
    if pid: u += '&destination_place_id=' + pid
    return u
def groute(o, d, wps):
    u = 'https://www.google.com/maps/dir/?api=1&travelmode=driving&origin=' + urllib.parse.quote(o) + '&destination=' + urllib.parse.quote(d)
    if wps: u += '&waypoints=' + urllib.parse.quote('|'.join(wps))
    return u
def a(href, text, cls='lnk'):
    return f'<a class="{cls}" href="{E(href)}" target="_blank" rel="noopener">{text}</a>'

def badge(orig, opt=False):
    if orig: return f'<span class="badge orig" title="처음 일정표 PDF에 있던 곳">기존 #{E(orig)}</span>'
    if opt: return '<span class="badge opt">선택 · 신규</span>'
    return '<span class="badge new" title="이번에 새로 추가">신규</span>'

def photo(key, alt, shop=False):
    if key in HAVE:
        USED.add(key)
        cap = '이 가게 메뉴 (Wikimedia)' if shop else '예시 사진 · 이 가게 아님'
        return f'<figure class="ph"><img src="img/{key}.jpg" alt="{E(alt)}" loading="lazy" width="330" height="240"><figcaption>{cap}</figcaption></figure>'
    return f'<figure class="ph ph-k" aria-hidden="true"><span lang="ja">{KANJI.get(key, "食")}</span><figcaption>사진은 아래 링크</figcaption></figure>'

def rating(g, gn, t):
    out = []
    if g: out.append(f'<span class="rt"><b>Google</b> ★ {g}<small>({gn})</small></span>')
    if t: out.append(f'<span class="rt tb"><b lang="ja">食べログ</b> {t}</span>')
    return '<div class="rts">' + ''.join(out) + '</div>' if out else ''

def eat_card(key, ctx=None):
    r = R[key]
    q = r.get('q') or r['name']
    links = [a(gsearch(q, r.get('pid')), '구글맵'), a(gnav(q, r.get('pid')), '길안내')]
    if r.get('tb'):
        links += [a('https://tabelog.com' + r['tb'], '타베로그'), a('https://tabelog.com' + r['tb'] + 'dtlphotolst/smp2/', '가게 사진')]
    return f'''<article class="card eat">
  {photo(r['img'], r['genre'], r.get('photo_is_shop'))}
  <div class="cb">
    <div class="meta">{badge(r['orig'])}<span class="genre">{E(r['genre'])}</span></div>
    <h4><span lang="ja">{E(r['name'])}</span> <small>{E(r['ko'])} · {E(r['area'])}</small></h4>
    {rating(r['g'], r['gn'], r['t'])}
    {('<div class="reason"><b>추천 이유</b><p>' + E(r['why']) + '</p></div>') if r.get('why') else ''}
    <dl>
      <div><dt>영업</dt><dd>{E(r['hours'])}</dd></div>
      <div><dt>휴무</dt><dd>{E(r['closed'])}</dd></div>
      <div><dt>가격</dt><dd>{E(r['price'])}</dd></div>
    </dl>
    <p class="tip">{E(r['tip'])}</p>
    <div class="links">{''.join(links)}</div>
  </div>
</article>'''

def act_card(key):
    x = A[key]
    q = x['name'].split(' (')[0]
    facts = ''.join(f'<li>{E(f)}</li>' for f in x['facts'])
    rt = rating(x.get('g'), x.get('gn'), None)
    return f'''<article class="card act">
  <div class="cb">
    <div class="meta">{badge(x['orig'], x.get('opt'))}<span class="genre">{E(x['area'])}</span></div>
    <h4><span lang="ja">{E(x['name'])}</span></h4>
    {rt}
    <ul class="flist">{facts}</ul>
    <div class="links">{a(gsearch(q, x.get('pid')), '구글맵')}{a(gnav(q, x.get('pid')), '길안내')}</div>
  </div>
</article>'''

def day_html(d):
    rows = []
    for t, kind, ref, title, sub in d['items']:
        body = f'<p class="it-t">{E(title)}</p>' + (f'<p class="it-s">{E(sub)}</p>' if sub else '')
        if ref and kind == 'eat':
            for rr in (ref if isinstance(ref, tuple) else (ref,)): body += eat_card(rr)
        elif ref and ref in A: body += act_card(ref)
        rows.append(f'<li class="it k-{kind}"><time>{t}</time><span class="dot" aria-hidden="true"></span><div class="it-b">{body}</div></li>')
    routes = ''.join(a(groute(o, de, w), f'{E(lbl)} 구글맵', 'btn') for lbl, o, de, w in d['routes'])
    return f'''<section class="day {d['color']}" id="day{d['n']}">
  <header class="dh">
    <p class="eyebrow">DAY {d['n']} · {d['date']} ({E(d['dow'])})</p>
    <h3>{E(d['title'])}</h3>
    <div class="dstats"><span>{E(d['km'])}</span><span>{E(d['drive'])}</span></div>
    <p class="wx"><b>날씨</b> {E(d['wx'])}</p>
    <p class="why"><b>이렇게 짠 이유</b> {E(d['why'])}</p>
    <div class="routes">{routes}</div>
  </header>
  <ol class="tl">{''.join(rows)}</ol>
</section>'''

def openmark(op):
    m = {'o': ('영업', 'ok'), 'x': ('휴무', 'no'), '?': ('확인', 'q')}
    return ''.join(f'<span class="op {m[v][1]}">{k} {m[v][0]}</span>' for k, v in op.items())

def reg_card(it):
    links = [a(gsearch(it['q']), '구글맵'), a('https://tabelog.com' + it['tb'], '타베로그'), a('https://tabelog.com' + it['tb'] + 'dtlphotolst/smp2/', '가게 사진')]
    inplan = f'<span class="badge inplan">일정 포함 · {E(it["inplan"])}</span>' if it.get('inplan') else ''
    award = f'<p class="award">{E(it["award"])}</p>' if it.get('award') else ''
    return f'''<article class="card rg">
  {photo(it['img'], it['genre'])}
  <div class="cb">
    <div class="meta"><span class="genre strong">{E(it['genre'])}</span>{inplan}</div>
    <h4><span lang="ja">{E(it['name'])}</span> <small>{E(it['ko'])} · {E(it['town'])}</small></h4>
    {rating(it['g'], it['gn'], it['t'])}
    {award}
    <p class="dish">{E(it['dish'])}</p>
    <p class="why2">{E(it['why'])}</p>
    <dl>
      <div><dt>영업</dt><dd>{E(it['hours'])}</dd></div>
      <div><dt>휴무</dt><dd>{E(it['closed'])}</dd></div>
      <div><dt>가격</dt><dd>{E(it['price'])}</dd></div>
    </dl>
    <div class="ops">{openmark(it['open'])}</div>
    <p class="tip">{E(it['tip'])}</p>
    <div class="links">{''.join(links)}</div>
  </div>
</article>'''

def region_html(rg):
    brief = ''.join(f'<li>{E(b)}</li>' for b in rg['brief'])
    cards = ''.join(reg_card(it) for it in rg['items'])
    return f'''<section class="region" id="r-{rg['key']}">
  <header class="rh">
    <h3>{E(rg['name'])} <small>{E(rg['sub'])}</small></h3>
    <p class="rmeta"><span>{E(rg['days'])}</span><span>{E(rg['drive'])}</span></p>
  </header>
  <div class="rgrid">{cards}</div>
  <div class="rbrief"><h4>현지 상황 (2026년 11월 초)</h4><ul>{brief}</ul><p class="more">{E(rg['ramen'])}</p></div>
</section>'''

WX = [
 ('11/2 월', [('c','흐림 0mm'),('r','새벽 비·눈 → 흐림'),('r','새벽 비·눈 → 흐림'),('c','흐림 0mm')], 0, '삿포로 시내'),
 ('11/3 화', [('s','흐림 → 오후 맑음'),('r','오전 비 → 12–18시 맑음'),('s','맑음 0mm'),('n','비·눈 4–11mm')], 1, '삿포로 → 오타루 오후'),
 ('11/4 수', [('r','새벽 진눈깨비 → 맑음'),('r','오전 비 → 오후 맑음'),('s','맑음 0mm · 신뢰도 A'),('n','오전 눈 → 오후 맑음')], 2, '남쪽'),
 ('11/5 목', [('c','흐림 · 밤 비'),('c','흐림 0mm'),('r','오후부터 비 4–11mm'),('s','오전 맑음 0mm · 신설')], 3, '북쪽'),
 ('11/6 금', [('r','새벽 비 → 흐림'),('r','비 5mm'),('r','새벽 비 → 갬'),('r','오후 비')], 0, '공항'),
]
def wx_table():
    rows = []
    for day, cells, pick, plan in WX:
        tds = ''.join(f'<td class="w-{c}{" pick" if i == pick or (day=="11/3 화" and i in (0,1)) else ""}">{E(t)}</td>' for i, (c, t) in enumerate(cells))
        rows.append(f'<tr><th scope="row">{day}</th>{tds}<td class="plan">{E(plan)}</td></tr>')
    return f'''<div class="tblwrap"><table class="wxt">
<thead><tr><th></th><th>삿포로</th><th>오타루</th><th>남쪽<small>도야·노보리베쓰·도마코마이</small></th><th>북쪽<small>아사히카와·비에이·히가시카와</small></th><th>일정</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>'''

BOOK = [
 ('bk2', '天ぷら 梵 (そよぎ)', '11/3 17:00 · 3명', '전화 <span class="num">0134-24-7220</span> (일본어, 카운터 9석)', None),
 ('bk3', 'しろくま 札幌本店', '11/2 19:00 · 3명', '타베로그 넷예약 또는 전화 <span class="num">011-552-4690</span>', 'https://tabelog.com/hokkaido/A0101/A010103/1000800/'),
 ('bk4', 'ログハウスびび', '11/4 19:00 · 3명 (L.O. 19:30)', '전화 예약 (번호는 공식 사이트)', 'https://restaurant-bibi.jp/'),
 ('bk6', '[당일] 아사히다케 운행 · 青葉 영업', '11/5 아침', '공식 사이트 운행 정보 · 青葉 <span class="num">0166-23-2820</span>', 'https://asahidake.hokkaido.jp/'),
 ('bk7', '예약 안 받는 곳 (줄 서기)', '彩未 · 翁 · マルトマ · Suage+ · 르타오(공휴일)', '시간표의 도착 시각을 지키면 대기가 가장 짧음', None),
]
def book_html():
    lis = []
    for i, name, when, how, url in BOOK:
        link = a(url, '사이트') if url else ''
        lis.append(f'<li><input type="checkbox" id="{i}"><label for="{i}"><b>{E(name)}</b><span>{E(when)}</span><span>{how} {link}</span></label></li>')
    return '<ul class="book">' + ''.join(lis) + '</ul>'

def dropped_html():
    rows = ''.join(f'<tr><td class="num">#{E(n)}</td><td>{E(nm)}</td><td>{E(why)}</td><td>{E(rev)}</td></tr>' for n, nm, why, rev in DROPPED)
    return f'<div class="tblwrap"><table class="drop"><thead><tr><th>PDF</th><th>장소</th><th>뺀 이유</th><th>살리려면</th></tr></thead><tbody>{rows}</tbody></table></div>'

def alts_html():
    return '<div class="alts">' + ''.join(f'<article class="alt"><p class="eyebrow">{E(x["when"])}</p><h4>{E(x["title"])}</h4><p>{E(x["body"])}</p><p class="cost"><b>대신 잃는 것</b> {E(x["cost"])}</p></article>' for x in ALTS) + '</div>'

body_days = ''.join(day_html(d) for d in DAYS)
body_regions = ''.join(region_html(r) for r in REGIONS)

def credits():
    out = []
    for k in sorted(USED):
        m = META[k]
        au = m.get('author') or '작성자는 파일 페이지 참조'
        lic = m.get('license') or ''
        lname = 'CC0' if 'zero' in lic else ('퍼블릭 도메인' if 'Public_domain' in lic else (lic.rstrip('/').split('/licenses/')[-1].upper().replace('/', ' ') if '/licenses/' in lic else '라이선스는 파일 페이지'))
        if '/licenses/' in lic: lname = 'CC ' + lname
        out.append(f'<li>{a(m["page"], E(m["file"].replace("_", " ")), "plain")} · {E(au)} · {E(lname)}</li>')
    return '<ul class="credits">' + ''.join(out) + '</ul>'

TPL = open(os.path.join(HERE, 'tpl.html'), encoding='utf-8').read()
page = (TPL.replace('{{WX}}', wx_table()).replace('{{BOOK}}', book_html()).replace('{{DAYS}}', body_days)
        .replace('{{DROPPED}}', dropped_html()).replace('{{ALTS}}', alts_html()).replace('{{REGIONS}}', body_regions)
        .replace('{{CREDITS}}', credits()))
os.makedirs(os.path.join(HERE, 'site/img'), exist_ok=True)
open(os.path.join(HERE, 'site/hokkaido-trip.html'), 'w', encoding='utf-8').write(page)
print('ok', len(page), 'used imgs', sorted(USED), 'missing', sorted(set(KANJI) - HAVE))
