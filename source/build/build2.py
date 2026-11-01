import urllib.parse
# -*- coding: utf-8 -*-
import os, json, html, urllib.parse, sys, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data2 import R, A, DAYS, DROPPED, REGIONS, BASE, SCEN, MOVES, CHANGES, OTHER_PDF, ALTNOTE, FREE, DAY_TOWNS, TOWN_NAME
import re as _re, ko as _ko
def _clean(k): return _re.sub(r'\s*\([^)]*\)', '', k.split(' · ')[0]).strip()
KODICT = {}
for _r in R.values(): KODICT[_r['name']] = _clean(_r['ko'])
for _rg in REGIONS:
    for _it in _rg['items']: KODICT[_it['name']] = _clean(_it['ko'])
KODICT.update(json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kodict.json'), encoding='utf-8')))
ANN = _ko.Annotator(KODICT)
E = html.escape
HERE = os.path.dirname(os.path.abspath(__file__))
META = json.load(open(os.path.join(HERE, 'img/meta.json')))
USED = {}
PHOTOS = json.load(open(os.path.join(HERE, 'photos.json')))
# v19: 사진 담당 작업 결과(scen/photo_out_*.json)를 합침 — 같은 imgkey·같은 Commons 파일은 건너뜀
import glob as _glob
PHOTO_SKIP = []
_pk = {x[0] for v in PHOTOS.values() for x in v}
_pfiles = {x[1] for v in PHOTOS.values() for x in v}
for _pf in sorted(_glob.glob(os.path.join(HERE, 'scen', 'photo_out_*.json'))):
    try:
        _po = json.load(open(_pf, encoding='utf-8'))
    except Exception as _e:
        print('WARN photo_out 읽기 실패', os.path.basename(_pf), _e); continue
    _pm = _po.get('meta', {})
    for _card, _lst in _po.get('photos', {}).items():
        for _it in _lst:
            _k, _f = _it[0], _it[1]; _cap = _it[2] if len(_it) > 2 else 0
            if _k in _pk or _f in _pfiles: PHOTO_SKIP.append((os.path.basename(_pf), _card, _k, 'dup')); continue
            _m = META.get(_k) or _pm.get(_k)
            if not _m: PHOTO_SKIP.append((os.path.basename(_pf), _card, _k, 'nometa')); continue
            META.setdefault(_k, _m)
            PHOTOS.setdefault(_card, []).append([_k, _f, _cap]); _pk.add(_k); _pfiles.add(_f)
HAVE = {k for k in META if os.path.exists(os.path.join(HERE, f'img/{k}.jpg'))}
# v19.8: 여행자 제공 사진(u_*)은 아티팩트 자산 저장소에 올려 그 주소로 보여 줌(파일 수 511개 제한에 안 걸리게)
_AU = os.path.join(HERE, 'scen/userphotos/asset_urls.json')
ASSET_URL = json.load(open(_AU, encoding='utf-8')) if os.path.exists(_AU) else {}
def IMGSRC(k): return ASSET_URL.get(k) or f'img/{k}.jpg'
# 자산 주소가 아직 없는 u_* 사진은 빼고 빌드(파일 수가 넘쳐 큰 사진이 페이지에 박히는 것 방지). 확인용: USERPHOTO_LOCAL=1
if not os.environ.get('USERPHOTO_LOCAL'):
    HAVE = {k for k in HAVE if not k.startswith('u_') or k in ASSET_URL}
from PIL import Image as _I
MAPDIM = {os.path.basename(f)[:-4]: _I.open(f).size for f in _glob.glob(os.path.join(HERE, 'site/map/*.jpg'))}
MISSING = []
CUR = ['', '']          # 지금 그리는 구역 (이름, #앵커) — 사진이 처음 나온 곳 기록용
PHOTO_HOME = {}

def _taken(cardkey):
    """이 카드의 사진이 이미 페이지 앞쪽에 나왔으면 (이름, 앵커), 아니면 None."""
    return PHOTO_HOME.get(cardkey)
def _clash(cardkey, n):
    """보여 줄 사진 중 하나라도 이미 다른 카드에서 쓰였으면 True (대안 안에서는 사진을 빼고 그림)."""
    return any(k in USED for k in [k for k, f, s in PHOTOS.get(cardkey, []) if k in HAVE][:n])
def _phref(home, what='사진'):
    return f'<p class="phref">{what}은 <a href="{home[1]}">{E(home[0])}</a>에 있음</p>'

def gsearch(q, pid=None):
    u = 'https://www.google.com/maps/search/?api=1&query=' + urllib.parse.quote(q)
    return u + ('&query_place_id=' + pid if pid else '')
def gnav(q, pid=None):
    u = 'https://www.google.com/maps/dir/?api=1&travelmode=driving&destination=' + urllib.parse.quote(q)
    return u + ('&destination_place_id=' + pid if pid else '')
def groute(o, d, wps):
    u = 'https://www.google.com/maps/dir/?api=1&travelmode=driving&origin=' + urllib.parse.quote(o) + '&destination=' + urllib.parse.quote(d)
    return u + ('&waypoints=' + urllib.parse.quote('|'.join(wps)) if wps else '')
def a(href, text, cls='lnk'):
    return f'<a class="{cls}" href="{E(href)}" target="_blank" rel="noopener">{text}</a>'

def badge(orig, opt=False):
    if orig: return f'<span class="badge orig" title="동재·현준·경일 회의에서 정한 일정표(PDF)에 있던 곳">기존 #{E(orig)}</span>'
    if opt: return '<span class="badge opt">선택 · 신규</span>'
    return '<span class="badge new" title="이번에 새로 추가">신규</span>'

def photo(key, alt, owner, shop=False, cap=None):
    if key and key in HAVE:
        USED.setdefault(key, owner)  # v19.5: 같은 사진 재사용 허용, 출처는 처음 한 번만
        cap = cap or ('이 가게 메뉴 사진' if shop else '')
        return f'<figure class="ph"><img src="{IMGSRC(key)}" alt="{E(alt)}" loading="lazy" width="330" height="248"><figcaption>{cap}</figcaption></figure>'
    MISSING.append((owner, key))
    return ''


def _realphoto(tb, q, pid=None):
    """실제 가게 사진(타베로그 사진 모음, 없으면 구글 지도) 링크 — 사진을 옮겨 싣지 않고 원래 페이지로 보냄."""
    if tb: return ('https://tabelog.com' + tb + 'dtlphotolst/smp2/', '실제 가게 사진 보기 (타베로그)')
    return (gsearch(q, pid), '실제 가게 사진 보기 (구글 지도)')

def strip_photos(cardkey, owner, alt, real=None):
    lst = [(k, s) for k, f, s in PHOTOS.get(cardkey, []) if k in HAVE]
    # v19.10: 가게 실제 사진(공식 o_ · 여행자 제공 u_)이 있으면 예시 사진은 섞지 않음
    if any(k.startswith(('u_', 'o_')) for k, _ in lst): lst = [(k, s) for k, s in lst if k.startswith(('u_', 'o_'))]
    if not lst:
        MISSING.append((owner, cardkey)); return ''
    figs = []
    PHOTO_HOME.setdefault(cardkey, tuple(CUR))
    for k, s in lst[:3]:
        USED.setdefault(k, owner)  # v19.5: 같은 사진 재사용 허용, 출처는 처음 한 번만
        tag = f'<span class="shoptag">{E(s) if isinstance(s, str) else "이 가게"}</span>' if s else ''
        figs.append(f'<figure><img src="{IMGSRC(k)}" alt="{E(alt)} 사진" loading="lazy">{tag}</figure>')
    # v19.9: 사진 설명 문구는 빼고 '실제 가게 사진 보기' 링크만 남김 (사용자 요청)
    reallink = (f'<a class="phreal" href="{E(real[0])}" target="_blank" rel="noopener">{E(real[1])} →</a>') if real else '실제 가게 사진은 아래 \'가게 사진\' 버튼'
    return f'<div class="phs">{"".join(figs)}</div><p class="phnote">{reallink}</p>'

def rating(g, gn, t):
    out = []
    if g: out.append(f'<span class="rt"><b>Google</b> ★ {g}<small>({gn})</small></span>')
    if t: out.append(f'<span class="rt tb"><b lang="ja">食べログ</b> {t}</span>')
    return '<div class="rts">' + ''.join(out) + '</div>' if out else ''

def links_for(r):
    q = r.get('q') or r['name']
    out = [a(gsearch(q, r.get('pid')), '구글맵'), a(gnav(q, r.get('pid')), '길안내')]
    if r.get('tb'):
        out += [a('https://tabelog.com' + r['tb'], '타베로그'), a('https://tabelog.com' + r['tb'] + 'dtlphotolst/smp2/', '가게 사진')]
    return '<div class="links">' + ''.join(out) + '</div>'

def status_html(s):
    first = s.split(' · ')[0]
    warn = ('❌' in first) or ('⚠' in first)
    return f'<span class="status{" warn" if warn else ""}">{E(s)}</span>'

def eat_card(key, alt=False, ctx=None):
    r = R[key]
    ph = strip_photos(key, r['name'], r['genre'], _realphoto(r.get('tb'), r.get('q') or r['name'], r.get('pid')))
    cls = 'card eat v' + (' alt' if alt else '')
    award = f'<p class="award">{E(r["award"])}</p>' if r.get('award') else ''
    wtxt = (ctx.get('why', {}).get(key) if ctx else None) or r.get('why')
    why = f'<div class="reason"><b>추천 이유</b><p>{E(wtxt)}</p></div>' if wtxt else ''
    altnote = (ctx['notes'].get(key) if ctx else None) or ALTNOTE.get(key)
    if altnote: altnote = _re.sub(r'^이 가게로 바꾸면[,\s]*', '', altnote)   # 제목 "이 가게로 바꾸면"과 겹치는 앞머리 빼기
    tiptxt = (ctx.get('tip', {}).get(key) if ctx else None) or r['tip']
    note = f'<p class="altnote"><b>이 가게로 바꾸면</b>{E(altnote)}</p>' if alt and altnote else ''
    st = (ctx['status'].get(key) if ctx else None) or r['status']
    return f'''<article class="{cls}">
  {ph}
  <div class="cb">
    <div class="meta">{badge(r.get('orig'))}<span class="genre">{E(r['genre'])}</span>{status_html(st)}</div>
    <h4><span class="jn" lang="ja">{E(r['name'])}</span> <small class="nmline"><span class="nml">한글 이름</span>{E(r['ko'])} · <span class="nml">위치</span>{E(r['area'])}</small></h4>
    {note}
    {rating(r.get('g'), r.get('gn'), r.get('t'))}
    {award}
    {why}
    <dl>
      <div><dt>영업</dt><dd>{E(r['hours'])}</dd></div>
      <div><dt>휴무</dt><dd>{E(r['closed'])}</dd></div>
      <div><dt>가격</dt><dd>{E(r['price'])}</dd></div>
    </dl>
    <p class="tip">{E(tiptxt)}</p>
    {links_for(r)}
  </div>
</article>'''

def alts_html(keys, ctx=None):
    names = ' · '.join(f'<span class="jn" lang="ja">{E(R[k]["name"])}</span><span class="kr">(<span class="nml">한글 이름</span>{E(_clean(R[k]["ko"]))})</span>' for k in keys)
    cards = ''.join(eat_card(k, alt=True, ctx=ctx) for k in keys)
    return f'<details class="alts"><summary><b>대안 맛집 {len(keys)}곳</b><span>{names}</span></summary><p class="althint">카드마다 \'이 가게로 바꾸면\' 줄에 일정 어떻게 달라지는지 적어 놨음.</p><div class="altlist">{cards}</div></details>'

def free_html(key):
    f = FREE.get(key)
    if not f: return ''
    names = ' · '.join(_html_esc_ko(x) for x in f['items'])
    lis = []
    for x in f['items']:
        rows = [('정보', x['info'], ''), ('이날', x['day'], ''), ('추천 이유', x['why'], '')]
        if x.get('change'): rows.append(('일정 조정', x['change'], 'chg'))
        dl = ''.join(f'<div class="{c}"><dt>{E(k)}</dt><dd>{E(v)}</dd></div>' for k, v, c in rows)
        lis.append(f'<li class="fri"><div class="frh"><span class="frcat">{E(x["cat"])}</span><b class="jn" lang="ja">{E(x["name"])}</b>'
                   f'<span class="frko">{E(x["ko"])}</span><span class="frtime">소요 {E(x["time"])}</span></div><dl>{dl}</dl></li>')
    note = f'<p class="frnote">{E(f["note"])}</p>' if f.get('note') else ''
    return (f'<details class="freed"><summary><b>자유시간에 할 만한 것 {len(f["items"])}곳</b><span>{names}</span></summary>'
            f'<p class="frhint">요금·시간은 10/31 공식 사이트·구글 지도 기준. "일정 조정" 있는 곳은 시간 더 걸려서 일정 바꿔야 함.</p>'
            f'<ol class="frlist">{"".join(lis)}</ol>{note}</details>')
def _html_esc_ko(x): return E(x['ko'])

def gallery(cardkey, owner, maxn=6, town=False):
    lst = [(k, c) for k, f, c in PHOTOS.get(cardkey, []) if k in HAVE][:maxn]
    if not lst: return ''
    PHOTO_HOME.setdefault(cardkey, tuple(CUR))
    n = len(lst); figs = []
    for i, (k, c) in enumerate(lst):
        USED.setdefault(k, owner)  # v19.5: 같은 사진 재사용 허용, 출처는 처음 한 번만
        cls = []
        if not town:
            if n == 5 and i == 4: cls.append('wide2')
            if n in (6,) and i == 5: cls.append('mwide')
        else:
            if n % 2 == 1 and i == n - 1 and n > 1: cls.append('mwide')
        cap = c if isinstance(c, str) and c else ''
        figs.append(f'<figure{" class=\"" + " ".join(cls) + "\"" if cls else ""}><img src="{IMGSRC(k)}" alt="{E(cap or owner)}" loading="lazy">'
                    + (f'<figcaption>{E(cap)}</figcaption>' if cap else '') + '</figure>')
    kind = 'tgal' if town else f'g{min(n, 6)}'
    return f'<div class="gal {kind}">{"".join(figs)}</div>'

def place_photos(cardkey, owner):
    g = gallery(cardkey, owner)
    if not g: return ''
    return g + '<p class="phnote">실제 장소 사진 · 찍은 계절 같이 적었음</p>'

def town_html(keys):
    blocks = []
    for k in keys:
        g = gallery('town:' + k, TOWN_NAME[k], 6, town=True)
        if g: blocks.append(f'<div class="town"><p class="town-n">{E(TOWN_NAME[k])}</p>{g}</div>')
    if not blocks: return ''
    return (f'<section class="towns" aria-label="이 날 지나는 동네"><p class="towns-h"><b>이 날 지나는 동네</b>'
            f'<span>거리·동네 분위기 사진 · 찍은 계절 같이 적었음</span></p>{"".join(blocks)}</section>')

def act_card(key, ctx=None):
    x = A[key]
    q = x.get('q') or x['name'].split(' (')[0]
    facts = ''.join(f'<li>{E(f)}</li>' for f in x['facts'])
    ph = place_photos('a:' + key, x['name'])
    return f'''<article class="card act{' v' if ph else ''}">
  {ph}
  <div class="cb">
    <div class="meta">{badge(x.get('orig'), x.get('opt'))}<span class="genre">{E(x['area'])}</span></div>
    <h4><span lang="ja">{E(x['name'])}</span></h4>
    {rating(x.get('g'), x.get('gn'), None)}
    <ul class="flist">{facts}</ul>
    <div class="links">{a(gsearch(q, x.get('pid')), '구글맵')}{a(gnav(q, x.get('pid')), '길안내')}</div>
  </div>
</article>'''

_SCOL = {'sa': 'var(--sa)', 'sb': 'var(--sb)', 'sc': 'var(--muted)', 'sd': 'var(--sd)', 'se': 'var(--se)', 'sf': 'var(--sf)', 'sg': 'var(--sg)'}
def day_scen_html(n):
    hits = [x for x in SCEN if any(int(k) + 1 == n for k in x['change'])]
    if not hits: return ''
    links = ''.join(f'<a class="scenlink" href="#scen-{x["key"]}" style="--sc:{_SCOL[x["color"]]}"><span class="key">{x["key"]}</span><span class="t">{E(x["title"])}</span><span class="go">보기 ↓</span></a>' for x in hits)
    return f'<div class="dayscen"><p><b>이 날을 바꾸고 싶다면</b> 이 날 바꾸는 대안 {len(hits)}개 있음. 누르면 바로 감.</p><div class="scenlinks">{links}</div></div>'

def day_html(d):
    CUR[:] = [f'DAY {d["n"]} 시간표', f'#day{d["n"]}']
    rows = [_tl_rows(d['items'])]
    routes = ''.join(a(groute(o, de, w), f'{E(lbl)} 구글맵', 'btn') for lbl, o, de, w in d['routes'])
    return f'''<section class="day {d['color']}" id="day{d['n']}"><details class="fold dayd">
  <summary class="dh">
    <p class="eyebrow"><span class="shield n{d['n']}">{d['n']}</span>DAY {d['n']} · {d['date']} ({E(d['dow'])})</p>
    <h3>{E(d['title'])}</h3>
    <div class="dstats"><span>{E(d['km'])}</span><span>{E(d['drive'])}</span><span class="foldhint"></span></div>
  </summary>
  <div class="dbody">
    <p class="wx"><b>날씨</b> {E(d['wx'])}</p>
    <p class="why"><b>이렇게 짠 이유</b> {E(d['why'])}</p>
  <figure class="dmap"><a href="map/{d['map']}.jpg" target="_blank" rel="noopener"><img src="map/{d['map']}.jpg" alt="{d['date']} 경로 지도" loading="lazy" width="{MAPDIM[d['map']][0]}" height="{MAPDIM[d['map']][1]}"></a>
    <figcaption>지도 번호 = 아래 시간표 번호. 누르면 크게 열림. © OpenStreetMap contributors</figcaption></figure>
  <div class="routes">{routes}</div>
  {day_scen_html(d['n'])}
  {town_html(DAY_TOWNS.get(d['n'], []))}
  <ol class="tl">{''.join(rows)}</ol>
  </div>
</details></section>'''

def openmark(op):
    m = {'o': ('영업', 'ok'), 'x': ('휴무', 'no'), '?': ('확인', 'q')}
    return ''.join(f'<span class="op {m[v][1]}">{k} {m[v][0]}</span>' for k, v in op.items())

def reg_card(it):
    if it.get('tb'):
        links = [a(gsearch(it['q']), '구글맵'), a('https://tabelog.com' + it['tb'], '타베로그'), a('https://tabelog.com' + it['tb'] + 'dtlphotolst/smp2/', '가게 사진')]
    else:
        links = [a(gsearch(it['q']), '구글맵'), a('https://tabelog.com/hokkaido/rstLst/?sw=' + urllib.parse.quote(it['q']), '타베로그 검색')]
    award = f'<p class="award">{E(it["award"])}</p>' if it.get('award') else ''
    ph = strip_photos('r:' + it['name'], it['name'], it['genre'], _realphoto(it.get('tb'), it.get('q') or it['name']))
    return f'''<article class="card rg v">
  {ph}
  <div class="cb">
    <div class="meta"><span class="genre strong">{E(it['genre'])}</span></div>
    <h4><span class="jn" lang="ja">{E(it['name'])}</span> <small class="nmline"><span class="nml">한글 이름</span>{E(it['ko'])} · <span class="nml">위치</span>{E(it['town'])}</small></h4>
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
    refs = ''
    if rg.get('refs'):
        refs = '<p class="refline"><b>이 지역에서 시간표에 이미 들어간 곳</b> (카드는 위 날짜에): ' + ' · '.join(f'<span lang="ja">{E(n)}</span> ({E(w)})' for n, w in rg['refs']) + '</p>'
    cards = ''.join(reg_card(it) for it in rg['items'])
    tag = '<span class="rtag pass">일정이 지나감</span>' if rg.get('group') == 'pass' else '<span class="rtag off">일정에 없음</span>'
    return f'''<section class="region" id="r-{rg['key']}"><details class="fold regd">
  <summary class="rh">
    <h3>{tag}{E(rg['name'])} <small>{E(rg['sub'])}</small></h3>
    <p class="rmeta"><span>{E(rg['days'])}</span><span>{E(rg['drive'])}</span><span>맛집 {len(rg['items'])}곳</span></p>
    <span class="openbtn" aria-hidden="true"></span>
  </summary>
  <div class="rbody">
  {refs}
  <div class="rgrid">{cards}</div>
  <div class="rbrief"><h4>현지 상황 (2026년 11월 초)</h4><ul>{brief}</ul></div>
  </div>
</details></section>'''

def strip(tiles, changed, label):
    out = [f'<span class="lab">{label}</span>']
    for i, (dt, dw, txt, c) in enumerate(tiles):
        cls = 'chg' if i in changed else ('same' if changed else '')
        out.append(f'<div class="tile t-{c} {cls}"><b>{dt} {E(dw)}</b>{E(txt)}</div>')
    return '<div class="strip">' + ''.join(out) + '</div>'

import re as _re
LODGING_Q = '札幌市東区北17条東2丁目4-32'
def _nav_dest(items, i):
    # v19.17: 이동 칸 → 다음 목적지(다음 식당·장소·숙소·렌터카) 구글맵 길안내
    t0 = items[i][3]
    if '숙소로' in t0: return (LODGING_Q, None)
    for t, kind, ref, title, sub, num, alts in items[i + 1:]:
        if kind == 'move': continue
        rr = ref[0] if isinstance(ref, tuple) else ref
        if kind in ('eat', 'same') and rr in R: return (R[rr].get('q') or R[rr]['name'], R[rr].get('pid'))
        if rr and rr in A: return (A[rr].get('q') or A[rr]['name'], A[rr].get('pid'))
        if '숙소' in title: return (LODGING_Q, None)
        if '렌터카' in title or 'Jnet' in title: return ('Jネットレンタカー 新千歳空港店', None)
        if '주유' in title: return ('ガソリンスタンド 新千歳空港 周辺', None)
        if '공항' in title or '터미널' in title or 'LJ2' in title: return ('新千歳空港 国際線ターミナル', None)
        return (_re.sub(r'\s*\(.*$', '', title), None)
    return (LODGING_Q, None)
def _tl_rows(items, ctx=None):
    rows = []
    for _i, (t, kind, ref, title, sub, num, alts) in enumerate(items):
        mn = f'<span class="mn" title="지도 번호">{E(num)}</span>' if num else ''
        if kind == 'same':
            n = int(str(ref)[3:])
            if title.startswith(t + ' '): title = title[len(t) + 1:]
            body = (f'<p class="it-t">{mn}<span class="samebadge">그대로</span>{E(title)}</p>'
                    + (f'<p class="it-s">{E(sub)}</p>' if sub else '')
                    + f'<p class="samelink"><a href="#day{n}">DAY {n} 시간표에서 보기 ↓</a></p>')
        else:
            if kind == 'move':
                _q, _pid = _nav_dest(items, _i)
                _u = gnav(_q, _pid) + '&dir_action=navigate'
                if '지하철' in title: _u = _u.replace('travelmode=driving', 'travelmode=transit')
                body = (f'<a class="mvgo" href="{E(_u)}" target="_blank" rel="noopener"><p class="it-t">{mn}{E(title)}<span class="navchip">길안내 ▶</span></p></a>'
                        + (f'<p class="it-s">{E(sub)}</p>' if sub else ''))
            else:
                body = f'<p class="it-t">{mn}{E(title)}</p>' + (f'<p class="it-s">{E(sub)}</p>' if sub else '')
            if ref and kind == 'eat':
                for rr in (ref if isinstance(ref, tuple) else (ref,)): body += eat_card(rr, ctx=ctx)
            elif ref and ref in A:
                body += act_card(ref, ctx=ctx) + free_html(ref)
            if alts: body += alts_html(alts, ctx=ctx)
        rows.append(f'<li class="it k-{kind}"><time>{t}</time><span class="dot" aria-hidden="true"></span><div class="it-b">{body}</div></li>')
    return ''.join(rows)

def scen_day_html(s, d, i):
    did = f'scen-{s["key"]}-d{i + 1}'
    CUR[:] = [f'대안 {s["key"]} 상세 일정', f'#{did}']
    ctx = dict(status=s['dstatus'], notes=s['dnotes'], why=s.get('dwhy', {}), tip=s.get('dtip', {}))
    rows = _tl_rows(d['items'], ctx)
    routes = ''.join(a(groute(o, de, w), f'{E(lbl)} 구글맵', 'btn') for lbl, o, de, w in d['routes'])
    mp = ''
    if d['map'] in MAPDIM:
        mp = (f'<figure class="dmap"><a href="map/{d["map"]}.jpg" target="_blank" rel="noopener"><img src="map/{d["map"]}.jpg" alt="대안 {s["key"]} {d["date"]} 경로 지도" loading="lazy" width="{MAPDIM[d["map"]][0]}" height="{MAPDIM[d["map"]][1]}"></a>'
              f'<figcaption>지도 번호 = 아래 시간표 번호. 누르면 크게 열림. © OpenStreetMap contributors</figcaption></figure>')
    return f'''<details class="fold scdet" id="{did}" style="--dc:var(--{d['col']})">
  <summary class="sdh">
    <p class="sdeye">바뀌는 날 상세 일정<span>시간표 · 맛집 카드 · 지도</span></p>
    <h4>{E(d['date'])} ({E(d['dow'])}) · {E(d['title'])}</h4>
    <div class="dstats"><span>{E(d['km'])}</span><span>{E(d['drive'])}</span><span class="foldhint"></span></div>
  </summary>
  <div class="dbody">
    <p class="wx"><b>날씨</b> {E(d['wx'])}</p>
    <p class="why"><b>이렇게 짠 이유</b> {E(d['why'])}</p>
    {mp}
    {town_html(d.get('towns', []))}
    <div class="routes">{routes}</div>
    <ol class="tl">{rows}</ol>
    <p class="scback"><a href="#scen-{s['key']}">대안 {s['key']} 요약으로 ↑</a></p>
  </div>
</details>'''

def scen_html(s):
    after = [s['change'].get(i, BASE[i]) for i in range(5)]
    strips = strip(BASE, set(), '지금 일정') + strip(after, set(s['change']), '바꾸면')
    mini = ''.join(f'<li><time>{E(t)}</time><span>{E(x)}</span></li>' for t, x in s['plan'])
    outl = ''.join(f'<li lang="ja">{E(x)}</li>' for x in s['out'])
    inl = ''.join(f'<li lang="ja">{E(x)}</li>' for x in s['inn'])
    mp = f'<figure class="dmap"><a href="map/{s["map"]}.jpg" target="_blank" rel="noopener"><img src="map/{s["map"]}.jpg" alt="대안 {s["key"]} 경로 지도" loading="lazy" width="{MAPDIM[s["map"]][0]}" height="{MAPDIM[s["map"]][1]}"></a></figure>' if s['map'] else ''
    sc = {'sa': 'var(--sa)', 'sb': 'var(--sb)', 'sc': 'var(--muted)', 'sd': 'var(--sd)', 'se': 'var(--se)', 'sf': 'var(--sf)', 'sg': 'var(--sg)'}[s['color']]
    return f'''<article class="scen" id="scen-{s['key']}" style="--sc:{sc}"><details class="fold scend">
  <summary><h3><span class="key">{s['key']}</span>{E(s['title'])}</h3>
  <p class="when"><b>이럴 때</b> {E(s['when'])}</p><span class="openbtn" aria-hidden="true"></span></summary>
  <div class="scenin">
  <div class="strips">{strips}</div>
  <div class="scen-body">
    <div style="display:grid;gap:10px;min-width:0">
      <h4 style="font-size:13px;color:var(--muted)">바뀌는 날 시간표</h4>
      <ul class="mini">{mini}</ul>
    </div>
    {mp if mp else '<div></div>'}
  </div>
  <div class="inout"><div class="minus"><h4>빠지는 곳</h4><ul>{outl}</ul></div><div class="plus"><h4>새로 들어오는 곳</h4><ul>{inl}</ul></div></div>
  <p class="other"><b>전체 영향</b>{E(s['other'])}</p>
  <p class="cost"><b>부담</b>{E(s['cost'])}</p>
  <div class="scdets">{''.join(scen_day_html(s, d, i) for i, d in enumerate(s.get('detail', [])))}</div>
  </div>
</details></article>'''

from wx19 import WX19 as WX, WX_NOTE   # v19.2: 11/1 날씨 갱신 (wx19.py)
def wx_table():
    rows = []
    for day, cells, pick, plan in WX:
        tds = ''.join(f'<td class="w-{c}{" pick" if i in pick else ""}">{E(t)}</td>' for i, (c, t) in enumerate(cells))
        rows.append(f'<tr><th scope="row">{day}</th>{tds}<td class="plan">{E(plan)}</td></tr>')
    return f'''<div class="tblwrap"><table class="wxt">
<thead><tr><th></th><th>삿포로</th><th>오타루</th><th>남쪽<small>도야·노보리베쓰·도마코마이</small></th><th>북쪽<small>아사히카와·비에이·히가시카와</small></th><th>일정</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div><p class="wxnote">{E(WX_NOTE)}</p>'''

BOOK = [
 ('bk1', 'Jnet 렌터카 · 운전자 등록', '11/2 픽업 12:30쯤', '예약은 12:00 → 12:30에 간다고 미리 연락. 운전은 경일 혼자. 픽업 때 경일 한국 면허증 + 국제운전면허증 + 여권 보여 주고 운전자로 등록 (등록 안 된 사람은 운전 불가)', None),
 ('bk10', '[당일] みなと食堂 재고 확인', '11/2 12:30 차 받을 때', '예약 불가 · 현금만 · 전화 <span class="num">0144-34-1777</span>로 남은 메뉴 확인 후 출발', 'https://tabelog.com/hokkaido/A0108/A010802/1057683/'),
 ('bk3', 'しろくま 札幌本店', '11/2 20:30 · 3명', '타베로그 넷예약 또는 전화 <span class="num">011-552-4690</span> (19:00으로 잡았다면 변경)', 'https://tabelog.com/hokkaido/A0101/A010103/1000800/'),
 ('bk2', '天ぷら 梵 (そよぎ)', '11/3 17:00 · 3명', '전화 <span class="num">0134-24-7220</span> (일본어, 카운터 9석) · 안 잡히면 11/3 저녁 대안 참고', None),
 ('bk8', '焼肉 グルマンズいとう', '11/3 21:00 · 3명 (야식)', '타베로그 넷예약 또는 전화 <span class="num">011-596-9029</span> · 2개월 전부터 받음, 21시 이후가 비교적 여유 · 안 되면 대안 1순위 芯々 (넷예약 21:00 가능, ☎011-206-9009)', 'https://tabelog.com/hokkaido/A0101/A010103/1068431/'),
 ('bk4', 'ログハウスびび', '11/4 18:35 · 3명 (L.O. 19:30)', '전화 예약 (번호는 공식 사이트)', 'https://restaurant-bibi.jp/'),
 ('bk9', '鮨処いちい', '11/5 20:00 · 3명 · おまかせ ¥9,000', '전화 <span class="num">011-232-2321</span> (넷예약에는 3명 자리가 없음) <details class="script"><summary>전화할 때 쓸 일본어 문장 보기</summary><span class="jn" lang="ja">「11月5日（木）20時から3名で、おまかせコース（9,000円）をお願いしたいのですが、空いていますか。できればカウンターでお願いします。」</span> <br>한글 발음: "주이치가쓰 이쓰카(모쿠) 니주지카라 산메이데, 오마카세 코-스(큐-센엔)오 오네가이시타이노데스가, 아이테이마스카. 데키레바 카운타-데 오네가이시마스."<br>뜻: "11월 5일(목) 20시부터 3명, 오마카세 코스(9,000엔)로 부탁드리고 싶은데 자리 있나요? 가능하면 카운터로 부탁드려요."</details>· 안 되면 鮨処 凜 20:00 넷예약', 'https://tabelog.com/hokkaido/A0101/A010102/1002533/'),
 ('bk6', '[당일] 11/5 아침 확인', '아사히다케 운행 · 天金 영업', '天金은 부정기 휴무, 아사히다케는 강풍 운휴', 'https://asahidake.hokkaido.jp/'),
 ('bk7', '예약 안 받는 곳 (줄 서기)', 'みなと食堂 · 木多郎 · 彩未 · 翁 · 天金 · 르타오(공휴일)', '시간표의 도착 시각을 지키면 대기가 가장 짧음 (木多郎는 11/2 17:30 오픈에 맞춰, 현금만)', None),
]
def book_html_v18():
    lis = []
    for i, name, when, how, url in BOOK:
        link = a(url, '사이트') if url else ''
        lis.append(f'<li><input type="checkbox" id="{i}"><label for="{i}"><b>{E(name)}</b><span>{E(when)}</span><span>{how} {link}</span></label></li>')
    return '<ul class="book">' + ''.join(lis) + '</ul>'

# v19.2: 미리 할 것(book19) + 숙소 체크인·가는 길(lodging19) + 대안으로 바꿀 때 예약할 것(altbook19)
import book19 as _bk19, lodging19 as _st19, altbook19 as _ab19
def lodging_html():
    secs = ''.join(f'<details class="staysec" id="{x["id"]}"><summary>{E(x["title"])}</summary><div class="staybody">{x["html"]}</div></details>' for x in _st19.STAY_SECTIONS)
    return (f'<details class="bkdet stayd" id="stay"><summary>{E(_st19.STAY_TITLE)}</summary>'
            f'<div class="stay"><p class="staysum">{_st19.STAY_SUMMARY_HTML}</p>{secs}</div></details>')
def book_html():
    return _bk19.render_book19(E, a, lodging_html()) + _ab19.altbook_html()

def dropped_html():
    lab = {'in': ('일정 유지', 'st-in'), 'alt': ('대안으로', 'st-alt'), 'out': ('빠짐', 'st-out')}
    rows = ''.join(f'<tr><td class="num">#{E(n)}</td><td>{E(nm)}</td><td class="st {lab[st][1]}">{lab[st][0]}</td><td>{E(why)}</td><td>{E(rev)}</td></tr>' for n, nm, why, rev, st in DROPPED)
    return f'<div class="tblwrap"><table class="drop"><thead><tr><th>PDF</th><th>장소</th><th>상태</th><th>내용</th><th>살리려면</th></tr></thead><tbody>{rows}</tbody></table></div>'

def _mvchip(st, text, day, was=False):
    head, _, rest = text.partition(' · ')
    if was and st in ('move', 'alt'): head = '→ ' + head
    chip = f'<a class="mv {st}" href="#{day}">{E(head)}</a>' if day else f'<span class="mv {st}">{E(head)}</span>'
    return chip + (f'<span class="nt">{E(rest)}</span>' if rest else '')
def _pn(n): return f'<span class="pn">#{E(n)}</span>' if n else ''
def changes_html():
    cnt = {'in': 0, 'alt': 0, 'out': 0}
    for n, *_x, st in DROPPED: cnt[st] += len(n.split('·'))
    tot = sum(cnt.values())
    out = [f'<div class="cnt"><span><b>{tot}</b>PDF 장소</span><span class="c-in"><b>{cnt["in"]}</b>메인 그대로</span>'
           f'<span class="c-alt"><b>{cnt["alt"]}</b>대안으로</span><span class="c-out"><b>{cnt["out"]}</b>빠짐</span></div>']
    out.append('<h3 class="chh">한눈에: 옮겨지거나 빠진 곳</h3><ul class="moves">')
    for route, day, what, why, st in MOVES:
        rt = f'<a class="route" href="#{day}">{E(route)}</a>' if day else f'<span class="route">{E(route)}</span>'
        out.append(f'<li class="{st}">{rt}<span class="what">{E(what)}</span><span class="why">{E(why)}</span></li>')
    out.append('</ul>')
    out.append('<details class="chgdays"><summary><span class="sumt">날짜별 변경점 보기</span><span class="sums">원래 PDF와 지금 일정을 날짜마다 나란히 비교 · 눌러서 펼치기 / 접기</span></summary>')
    out.append('<p class="chgnote">여기는 뭐가 어디로 옮겨졌는지만 보는 요약. <b>자세한 시간표는 아래 <a href="#plan">날짜별 시간표</a></b>에 있음.</p>')
    out.append('<div class="mvkey">'
               '<span><span class="mv keep">그대로</span> 원래 자리</span><span><span class="mv move">→ 옮김</span> 다른 시간·날로</span>'
               '<span><span class="mv alt">→ 대안</span> 그 끼니의 대안으로</span><span><span class="mv out">빠짐</span> 일정에서 뺌</span>'
               '<span><span class="mv in">← 옮겨옴</span> 다른 날에서 옴</span><span><span class="mv new">신규</span> 새로 넣은 곳</span></div>')
    for c in CHANGES:
        if c['was']:
            lis = ''.join(f'<li><span class="nm">{E(nm)}</span>{_pn(pn)}{_mvchip(st, dest, day, True)}</li>' for nm, pn, st, dest, day in c['was'])
            was = f'<div class="cmpcol was"><h4>원래 PDF</h4><ol>{lis}</ol></div>'
        else:
            was = '<div class="cmpcol was empty"><h4>원래 PDF</h4><p>PDF에 없던 날<br><small>원래 일정표는 11/4까지</small></p></div>'
        lis = ''.join(f'<li><time>{E(t)}</time><span class="nm">{E(nm)}</span>{_pn(pn)}{_mvchip(st, note, None) if note else ""}</li>' for t, nm, pn, st, note in c['now'])
        now = f'<div class="cmpcol now"><h4>지금 시간표</h4><ol>{lis}</ol></div>'
        out.append(f'<div class="cmpday n{c["n"]}"><h3><span class="shield">{c["n"]}</span>{E(c["date"])} <small>{E(c["dow"])} · {E(c["title"])}</small> <a class="lnk" href="#day{c["n"]}">상세 시간표 ↓</a></h3>'
                   f'<div class="cmp">{was}<div class="arrow" aria-hidden="true">→</div>{now}</div><p class="cmpwhy"><b>왜</b>{E(c["why"])}</p></div>')
    lis = ''.join(f'<li><span class="nm">{E(nm)}</span>{_pn(pn)}{_mvchip(st, dest, day, True)}</li>' for nm, pn, st, dest, day in OTHER_PDF)
    out.append(f'<div class="cmpday other"><h3>그 밖의 PDF 장소</h3><div class="cmpcol was"><ol>{lis}</ol></div></div>')
    out.append(f'<details class="dropdet"><summary>PDF 18곳을 표로 보기 (살리는 방법 포함)</summary>{dropped_html()}</details>')
    out.append('</details>')
    return '\n'.join(out)

def _el_item(key, kind):
    r = R[key]
    sc = []
    if r.get('t'): sc.append(f'<span class="tb">타베로그 {E(r["t"])}</span>')
    if r.get('g'): sc.append(f'<span>구글 {E(r["g"])} <small>({E(r["gn"])})</small></span>')
    tag = '<span class="eltag main">메인</span>' if kind == 'main' else '<span class="eltag alt">대안</span>'
    orig = f'<span class="elorig">PDF #{E(r["orig"])}</span>' if r.get('orig') else ''
    rows = []
    if kind == 'alt' and ALTNOTE.get(key): rows.append(('바꾸면', ALTNOTE[key], 'chg'))
    if r.get('why'): rows.append(('추천 이유', r['why'], ''))
    if r.get('price'): rows.append(('메뉴·가격', r['price'], ''))
    rows.append(('영업', f'{r.get("hours","")} · 휴무 {r.get("closed","")}', ''))
    dl = ''.join(f'<div class="{c}"><dt>{E(k)}</dt><dd>{E(v)}</dd></div>' for k, v, c in rows)
    return (f'<li class="eli {kind}"><div class="elh">{tag}<b class="jn" lang="ja">{E(r["name"])}</b><span class="elko"><span class="nml">한글 이름</span>{E(r["ko"])}</span>{orig}</div>'
            f'<div class="elm"><span class="elg">{E(r["genre"])}</span>{"".join(sc)}<span class="elst{' warn' if any(c in r.get('status','').split(' · ')[0] for c in '⚠❌') else ''}">{E(r.get("status",""))}</span></div>'
            f'<dl>{dl}</dl></li>')

def eatlist_html():
    out = ['<div class="eatlist" id="eatlist"><h3 class="elt">맛집만 모아 보기 <small>사진 없이 · 날짜별 메인과 대안</small></h3>'
           '<p class="elsub">날짜 누르면 펼쳐짐. 끼니마다 메인 맛집 나오고, 대안은 "대안 N곳 보기" 누르면 나옴. 사진·지도·길안내는 아래 상세 일정에 있음.</p>']
    for d in DAYS:
        slots = []; mains = []
        for t, kind, ref, title, sub, num, alts in d['items']:
            if kind != 'eat' or not ref: continue
            refs = ref if isinstance(ref, tuple) else (ref,)
            mains += [_clean(R[x]['ko']) for x in refs]
            items = ''.join(_el_item(x, 'main') for x in refs)
            altblk = ''
            if alts:
                altnames = ' · '.join(_clean(R[x]['ko']) for x in alts)
                altblk = (f'<details class="elalts"><summary><b>대안 {len(alts)}곳 보기</b><span>{E(altnames)}</span><span class="obrow"><span class="openbtn sm" aria-hidden="true"></span></span></summary>'
                          f'<ol>{"".join(_el_item(x, "alt") for x in alts)}</ol></details>')
            slots.append(f'<section class="els"><h4><time>{E(t)}</time>{E(title)}</h4><ol>{items}</ol>{altblk}</section>')
        if not slots: continue
        out.append(f'<details class="eld n{d["n"]}"><summary><span class="shield">{d["n"]}</span><b>{E(d["date"])} ({E(d["dow"])})</b>'
                   f'<span class="elms">{E(" → ".join(mains))}</span><span class="obrow"><span class="openbtn sm" aria-hidden="true"></span></span></summary>{"".join(slots)}'
                   f'<p class="elback"><a href="#day{d["n"]}">이 날 상세 시간표 ↓</a></p></details>')
    out.append('</div>')
    return '\n'.join(out)

def credits():
    out = []; _ushop = set()
    for k in sorted(USED, key=lambda x: USED[x]):
        m = META[k]
        if m.get('license') == 'user_supplied':  # v19.8 여행자 제공 사진: 가게마다 한 줄
            if USED[k] in _ushop: continue
            _ushop.add(USED[k]); _n = sum(1 for x in USED if USED[x] == USED[k] and META[x].get('license') == 'user_supplied')
            out.append(f'<li><span lang="ja">{E(USED[k])}</span> — 사진 {_n}장 · 여행자 제공 (가게·촬영자 사용 허락 받음) · {a(m["page"], "가게 정보", "plain")}</li>')
            continue
        au = (m.get('author') or '').replace('No machine-readable author provided. ', '').replace(' assumed (based on copyright claims).', '')
        au = au.split(' from Seiro')[0][:60] or '작성자는 파일 페이지 참조'
        lic = m.get('license') or ''
        if lic == 'shop_official':
            out.append(f'<li><span lang="ja">{E(USED[k])}</span> — {a(m["page"], "가게 공식 사진 목록", "plain")} · 가게 공식 사진(타베로그 by お店) · 사용 허락은 여행자 확인</li>')
            continue
        if 'zero' in lic: ln = 'CC0'
        elif 'Public_domain' in lic: ln = '퍼블릭 도메인'
        elif '/licenses/' in lic: ln = 'CC ' + lic.rstrip('/').split('/licenses/')[-1].upper().replace('/', ' ')
        else: ln = '라이선스는 파일 페이지'
        out.append(f'<li><span lang="ja">{E(USED[k])}</span> — {a(m["page"], E(m["file"].replace("_", " ")), "plain")} · {E(au)} · {E(ln)}</li>')
    return '<ul class="credits">' + ''.join(out) + '</ul>'

FOLDBAR = lambda scope, lbl: f'<div class="foldbar" data-scope="{scope}"><span>{lbl}</span><button type="button" data-fold="open">모두 펼치기</button><button type="button" data-fold="close">모두 접기</button></div>'
days_html = '<div class="dethead" id="detail"><h2>상세 일정</h2><p>DAY 1–5 날짜별 시간표 · 사진 · 지도 · 길안내</p></div>' + FOLDBAR('dayd', '날짜 누르면 그날 상세 일정 펼쳐짐') + ''.join(day_html(d) for d in DAYS)
_PASS = [r for r in REGIONS if r.get('group') == 'pass']
_OFF = [r for r in REGIONS if r.get('group') != 'pass']
def _rnav(lst): return ''.join(f'<a href="#r-{rg["key"]}">{E(rg["name"])}</a>' for rg in lst)
regions_html = (f'''<div class="rguide">
  <div class="rgcol pass"><h3>① 일정이 지나가는 지역</h3><p>11/4 남쪽, 11/5 북쪽 루프가 지나가는 동네. 동선 조금만 바꾸면 그날 바로 갈 수 있음.</p><nav class="rnav" aria-label="일정이 지나가는 지역">{_rnav(_PASS)}</nav></div>
  <div class="rgcol off"><h3>② 일정에 없는 지역</h3><p>5일 시간표에 없는 외곽. 가려면 하루 통째로 바꿔야 함 (위 "일정 변경 대안" 참고).</p><nav class="rnav" aria-label="일정에 없는 지역">{_rnav(_OFF)}</nav></div>
</div>''' + FOLDBAR('regd', '지역 누르면 맛집 카드 펼쳐짐') + '<h3 class="rgroup">① 일정이 지나가는 지역</h3>' + ''.join(region_html(r) for r in _PASS)
  + '<h3 class="rgroup">② 일정에 없는 지역 (하루를 바꿔야 갈 수 있음)</h3>' + ''.join(region_html(r) for r in _OFF))
scen_all = ''.join(scen_html(s) for s in SCEN)
CSS = open(os.path.join(HERE, 'css2.css'), encoding='utf-8').read()
for _cf in ('book19.css', 'lodging19.css', 'altbook19.css'): CSS += '\n' + open(os.path.join(HERE, _cf), encoding='utf-8').read()
BODY = open(os.path.join(HERE, 'body2.html'), encoding='utf-8').read()
page = ('<title>홋카이도 맛집 투어 계획</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600&family=Noto+Sans+JP:wght@500;700&family=Noto+Sans+KR:wght@400;500;700&family=Noto+Serif+KR:wght@700;900&display=swap">\n'
        '<style>' + CSS + '</style>\n' + BODY)
def sidenav_html():
    def li(href, text, cls='', sub=False):
        return f'<li class="{"sub " if sub else ""}{cls}"><a href="{href}">{text}</a></li>'
    L = [li('#top', '맨 위'), li('#map', '전체 지도'), li('#weather', '날씨'), li('#booking', '미리 할 것'), li('#changes', '원래 일정 비교'),
         li('#plan', '날짜별 시간표'), li('#eatlist', '맛집만 모아 보기', sub=True),
         li('#detail', '<span class="t">상세 일정</span><span class="hd">DAY 1–5</span>', 'snhead')]
    for d in DAYS:
        L.append(li(f'#day{d["n"]}', f'<span class="shield n{d["n"]}">{d["n"]}</span><span class="t">{E(d["date"])} {E(BASE[d["n"]-1][2])}</span>', f'n{d["n"]}', sub=True))
    L.append(li('#swap', '일정 변경 대안'))
    for x in SCEN:
        L.append(li(f'#scen-{x["key"]}', f'<span class="sk">{x["key"]}</span><span class="t">{E(x["title"])}</span>', sub=True))
    L += [li('#regions', '외곽 맛집 모음'), li('#sources', '출처와 메모')]
    ul = f'<ul>{"".join(L)}</ul>'
    FA = '<button type="button" class="foldall" disabled>모두 접기<span class="fac"></span></button>'
    FB = ('<div class="snfoot"><button type="button" class="foldall big" disabled>▴ 펼친 것 모두 접기<span class="fac"></span></button>'
          '<a class="sngo" href="https://claude.ai/artifact/3cV9wQR5GUyk5nVJErzLQm" target="_blank" rel="noopener"><span aria-hidden="true">🚗</span><b>일본 운전 가이드</b><i aria-hidden="true">→</i></a></div>')
    # v19.9: 문서 지도 자체 접기(PC) — 접으면 왼쪽 가장자리에 "문서 지도 ▸" 세로 탭이 보임
    return (f'<nav class="sidenav" id="sidenav" aria-label="문서 지도"><p class="sntitle"><span class="snl">문서 지도</span><span class="snr">{FA}'
            f'<button type="button" class="snclose" aria-label="문서 지도 접기" title="문서 지도 접기">◂ 접기</button></span></p>{ul}{FB}</nav>'
            f'<button type="button" class="snedge" aria-controls="sidenav" title="문서 지도 접기" aria-label="문서 지도 접기"><b>◂</b><span>접기</span></button>'
            f'<button type="button" class="snopen" aria-controls="sidenav" aria-expanded="false" title="문서 지도 펼치기"><span>문서 지도</span><b>▸</b></button>'
            f'<button type="button" class="tocbtn" aria-expanded="false" aria-controls="tocpanel">목차 열기</button>'
            f'<nav class="tocpanel" id="tocpanel" aria-label="목차" hidden><p class="sntitle">목차 <span class="snr">{FA}<button type="button" class="tocx" aria-label="닫기">✕</button></span></p>{ul}{FB}</nav>')
page = (page.replace('{{WX}}', wx_table()).replace('{{SIDENAV}}', sidenav_html()).replace('{{BOOK}}', book_html()).replace('{{BOOKN}}', str(len(_bk19.BOOK19))).replace('{{ALTN}}', str(sum(len(g['items']) for g in _ab19.ALTBOOK))).replace('{{DAYS}}', days_html)
        .replace('{{CHANGES}}', changes_html()).replace('{{EATLIST}}', eatlist_html()).replace('{{SCEN}}', scen_all).replace('{{REGIONS}}', regions_html)
        .replace('{{CREDITS}}', credits()))

import html as _html, re
def _walk_text(page, fn):
    toks = re.split(r'(<[^>]+>)', page); skip = []; out = []
    for t in toks:
        if t.startswith('<'):
            low = t.lower()
            if skip:
                if low.startswith('</' + skip[-1]): skip.pop()
            elif low.startswith(('<style', '<script', '<title')): skip.append(re.match(r'<(\w+)', low).group(1))
            out.append(t)
        else:
            out.append(t if skip or not t.strip() else fn(t))
    return ''.join(out)
_POLISH_PATH = os.path.join(HERE, 'polish.json')
_POLISH = json.load(open(_POLISH_PATH, encoding='utf-8')) if os.path.exists(_POLISH_PATH) else {}
_POLISH_HIT = set()
def _apply_polish(t):
    raw = _html.unescape(t); lead = raw[:len(raw) - len(raw.lstrip())]; trail = raw[len(raw.rstrip()):]
    core = raw.strip()
    new = core
    if core in _POLISH:
        _POLISH_HIT.add(core); new = _POLISH[core]
    if len(new) > 10 and 'Google' in new: new = new.replace('Google 지도', '구글 지도').replace('Google', '구글')
    if new != core: return _html.escape(lead + new + trail, quote=False)
    return t

if os.environ.get('DUMP'):
    _seen = {}
    def _collect(t):
        c = _html.unescape(t).strip()
        if re.search(r'[가-힣]', c) and c not in _seen: _seen[c] = len(_seen)
        return t
    _walk_text(page, _collect)
    json.dump(list(_seen), open(os.path.join(HERE, 'polish_src.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('dumped', len(_seen), sum(len(x) for x in _seen))
page = _walk_text(page, _apply_polish)
if _POLISH: print('polish applied', len(_POLISH_HIT), '/', len(_POLISH))
page = _ko.annotate_html(page, ANN)
json.dump(ANN.log, open(os.path.join(HERE, 'ko_log.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
open(os.path.join(HERE, 'site/hokkaido-trip.html'), 'w', encoding='utf-8').write(page)
os.makedirs(os.path.join(HERE, 'site/img'), exist_ok=True)
for f in os.listdir(os.path.join(HERE, 'site/img')): os.remove(os.path.join(HERE, 'site/img', f))
for k in USED:
    if k in ASSET_URL: continue  # 자산 저장소에 있는 사진은 게시 파일로 넣지 않음
    shutil.copy(os.path.join(HERE, f'img/{k}.jpg'), os.path.join(HERE, f'site/img/{k}.jpg'))
for k, *_ in _st19.STAY_IMAGES: shutil.copy(os.path.join(HERE, f'img/{k}.jpg'), os.path.join(HERE, f'site/img/{k}.jpg'))
# v19.5: 아티팩트 한 판에 담을 수 있는 파일 수(511) 제한 — 넘치면 작은 사진부터 페이지 안에 직접 넣음(data URI)
import base64 as _b64
_MAXF = 508
_imgs = sorted(os.listdir(os.path.join(HERE, 'site/img')), key=lambda f: os.path.getsize(os.path.join(HERE, 'site/img', f)))
_nfiles = len(_imgs) + len([f for f in os.listdir(os.path.join(HERE, 'site/map')) if f.endswith('.jpg')]) + 1
_inl = []
_pg = open(os.path.join(HERE, 'site/hokkaido-trip.html'), encoding='utf-8').read()
for _f in _imgs:
    if _nfiles <= _MAXF: break
    _src = f'img/{_f}'
    _uri = 'data:image/jpeg;base64,' + _b64.b64encode(open(os.path.join(HERE, 'site', _src), 'rb').read()).decode()
    _pg = _pg.replace(f'src="{_src}"', f'src="{_uri}"').replace(f'href="{_src}"', f'href="{_uri}"')
    os.remove(os.path.join(HERE, 'site', _src)); _inl.append(_f); _nfiles -= 1
if _inl:
    open(os.path.join(HERE, 'site/hokkaido-trip.html'), 'w', encoding='utf-8').write(_pg)
json.dump(_inl, open(os.path.join(HERE, 'inlined.json'), 'w'))
print('files', _nfiles, 'inlined', len(_inl))
print('ok', len(page), 'imgs', len(USED))
print('MISSING', MISSING)
