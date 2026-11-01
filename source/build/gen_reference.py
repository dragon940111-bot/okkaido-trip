# -*- coding: utf-8 -*-
"""data2.py + build2.py(BOOK/WX) + scen/*.py 를 사람이 읽을 수 있는 참고 문서로 펼침."""
import os, re, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from data2 import R, A, DAYS, DROPPED, REGIONS, BASE, SCEN, MOVES, CHANGES, OTHER_PDF, ALTNOTE, FREE

src = open(os.path.join(HERE, 'build2.py'), encoding='utf-8').read()
ns = {'E': lambda s: s}
for name in ('WX', 'BOOK'):
    m = re.search(r'^' + name + r' = \[.*?^\]', src, re.S | re.M)
    exec(m.group(0), ns)
WX, BOOK = ns['WX'], ns['BOOK']

def strip_tags(s): return re.sub(r'<[^>]+>', '', s or '')
out = []
w = out.append

def rline(k, r, note=None, status=None):
    rr = R.get(k) or r
    w(f"- **{rr['name']}** ({rr['ko']}) · {rr['genre']} · {rr['area']}  `키:{k}`")
    w(f"  - 평점: 타베로그 {rr.get('t')} · 구글 {rr.get('g')} ({rr.get('gn')}건)" + (f" · {rr['award']}" if rr.get('award') else ''))
    w(f"  - 영업: {rr['hours']} · 휴무: {rr['closed']} · 상태: {status or rr.get('status','')}")
    w(f"  - 가격: {rr['price']}")
    if rr.get('why'): w(f"  - 추천 이유: {rr['why']}")
    if rr.get('tip'): w(f"  - 팁: {rr['tip']}")
    if note: w(f"  - 이 가게로 바꾸면: {note}")
    if rr.get('tb'): w(f"  - 타베로그: https://tabelog.com{rr['tb']}")
    if rr.get('orig'): w(f"  - 원래 PDF 장소 #{rr['orig']}")

def aline(k, x):
    w(f"- **{x['name']}** · {x.get('area','')}  `키:{k}`" + (f" · 구글 {x.get('g')} ({x.get('gn')})" if x.get('g') else ''))
    for f in x.get('facts', []): w(f"  - {f}")

w('# 홋카이도 맛집 투어 — 전체 자료 (데이터에서 자동 생성)')
w('생성 기준: build/data2.py (v18 게시본과 같은 데이터) + build/scen/*.py (대안 상세 조사, 아직 페이지 미반영). 날짜 2026/10/31.')
w('')
w('## 1. 예약·준비 체크리스트 (페이지의 "예약·확인할 것")')
for bid, t, when, how, url in BOOK:
    w(f"- **{strip_tags(t)}** — {strip_tags(when)} — {strip_tags(how)}" + (f" ({url})" if url else ''))
w('')
w('## 2. 날씨 (10/31 기준 예보, 지역별)')
w('| 날짜 | 삿포로 | 오타루 | 남쪽 | 북쪽 | 일정 |')
w('|---|---|---|---|---|---|')
for day, cells, pick, plan in WX:
    w(f"| {day} | " + ' | '.join(('**' + t + '**') if i in pick else t for i, (c, t) in enumerate(cells)) + f" | {plan} |")
w('')
w('## 3. 원래 PDF 일정 대비 바뀐 점')
w('### 날짜별 비교 (CHANGES)')
for c in CHANGES:
    w(f"- **{c['date']} ({c['dow']}) {c['title']}** — {c.get('why','')}")
    w('  - 원래: ' + ' / '.join(f"{a} [{b or '-'}] → {d}" for a, b, s, d, *_ in (c.get('was') or [])))
    w('  - 지금: ' + ' / '.join(f"{t} {a} [{b or '-'}] ({d})" for t, a, b, s, d in (c.get('now') or [])))
w('### 옮겨진 것 (MOVES)')
for m in MOVES: w('- ' + ' · '.join(str(x) for x in m if x))
w('### PDF 장소 중 대안·빠진 것 (OTHER_PDF / DROPPED)')
for o in OTHER_PDF: w('- ' + ' · '.join(str(x) for x in o if x))
for d in DROPPED: w('- #' + ' · '.join(str(x) for x in d if x))
w('')
w('## 4. 상세 일정 (게시된 v18)')
for d in DAYS:
    w(f"### DAY {d['n']} · {d['date']} ({d['dow']}) — {d['title']}")
    w(f"- 거리·운전: {d['km']} · {d['drive']} · 날씨: {d['wx']}")
    w(f"- 이렇게 짠 이유: {d['why']}")
    for t, kind, ref, title, sub, num, alts in d['items']:
        w(f"#### {t} [{kind}] {title}" + (f" (지도 {num})" if num else ''))
        if sub: w(f"- {sub}")
        if kind == 'eat' and ref:
            for rr in (ref if isinstance(ref, tuple) else (ref,)): rline(rr, R[rr])
        elif ref and ref in A:
            aline(ref, A[ref])
            f = FREE.get(ref)
            if f:
                w('- 자유시간 추천:')
                for x in f['items']:
                    w(f"  - {x['name']} ({x['ko']}, {x['cat']}, 소요 {x['time']}): {x['info']} · {x['day']} · 이유: {x['why']}" + (f" · 일정 조정: {x['change']}" if x.get('change') else ''))
                if f.get('note'): w(f"  - {f['note']}")
        if alts:
            w('- **대안 맛집:**')
            for k in alts: rline(k, R[k], ALTNOTE.get(k))
    w('')

w('## 5. 일정 변경 대안 A–G — 지금 페이지의 요약 (v18)')
for s in SCEN:
    w(f"### {s['key']}. {s['title']}")
    w(f"- 이럴 때: {s['when']}")
    w('- 바뀌는 날: ' + ', '.join(f"{v[0]} {v[1]} → {v[2]}" for v in s['change'].values()))
    for t, x in s['plan']: w(f"  - {t} {x}")
    w(f"- 빠지는 곳: {', '.join(s['out'])} / 새로 들어오는 곳: {', '.join(s['inn'])}")
    w(f"- 전체 영향: {s['other']}"); w(f"- 부담: {s['cost']}")
w('')

w('## 6. 일정 변경 대안 — 새로 조사한 상세 일정 (scen/*.py, 아직 페이지 미반영)')
NR, NA = {}, {}
for fn in ('scen_A', 'scen_B', 'scen_C', 'scen_D', 'scen_EF', 'scen_G'):
    spec = importlib.util.spec_from_file_location(fn, os.path.join(HERE, 'scen', fn + '.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    NR.update(getattr(m, 'NEW_R', {})); NA.update(getattr(m, 'NEW_A', {}))
    for L, S in m.SCN.items():
        w(f"### 대안 {L} (파일 scen/{fn}.py)")
        for k in ('title', 'when'):
            if S.get(k): w(f"- {k}: {S[k]}")
        for d in S['days']:
            w(f"#### {d['date']} ({d['dow']}) {d['title']} — {d['km']} · {d['drive']}")
            w(f"- 날씨: {d['wx']}"); w(f"- 이유: {d['why']}")
            for t, kind, ref, title, sub, num, alts in d['items']:
                w(f"- **{t}** [{kind}] {title}" + (f" — {sub}" if sub else '') + (f" (지도 {num})" if num else ''))
                if kind == 'eat' and ref:
                    for rr in (ref if isinstance(ref, tuple) else (ref,)):
                        r = NR.get(rr) or R.get(rr)
                        w(f"  - 메인: {r['name']} ({r['ko']}) · 타베로그 {r.get('t')} · 구글 {r.get('g')}({r.get('gn')}) · {S['status'].get(rr,'')}")
                if alts:
                    for k in alts:
                        r = NR.get(k) or R.get(k)
                        w(f"  - 대안: {r['name']} ({r['ko']}) · 타베로그 {r.get('t')} · 구글 {r.get('g')}({r.get('gn')}) · {S['status'].get(k,'')} · 바꾸면: {S['notes'].get(k,'')}")
        if S.get('summary_plan'):
            w('- 요약 시간표: ' + ' / '.join(f"{a} {b}" for a, b in S['summary_plan']))
        w(f"- 빠지는 곳: {', '.join(S.get('out', []))} / 새로 들어오는 곳: {', '.join(S.get('inn', []))}")
        w(f"- 전체 영향: {S.get('other','')}"); w(f"- 부담: {S.get('cost','')}")
        w('')
w('### 대안용 새 맛집 상세 (NEW_R)')
for k, r in NR.items(): rline(k, r)
w('### 대안용 새 볼거리 (NEW_A)')
for k, x in NA.items(): aline(k, x)
w('')

w('## 7. 일정에 없는 지역·지나가는 지역 맛집 (REGIONS)')
for rg in REGIONS:
    w(f"### {rg['name']} ({rg['sub']}) — {rg['days']} · {rg['drive']}")
    for b in rg['brief']: w(f"- {b}")
    if rg.get('refs'): w('- 시간표에 이미 있는 곳: ' + ', '.join(f"{n} ({x})" for n, x in rg['refs']))
    for it in rg['items']:
        w(f"- **{it['name']}** ({it['ko']}) · {it['genre']} · {it['town']} · 타베로그 {it['t']} · 구글 {it['g']}({it['gn']})")
        w(f"  - 영업 {it['hours']} · 휴무 {it['closed']} · 날짜별 {it['open']} · 가격 {it['price']}")
        w(f"  - {it['dish']} — {it['why']} · 팁: {it['tip']}")
w('')
w('## 8. 맛집 키 전체 목록')
for k, r in R.items():
    w(f"- `{k}` {r['name']} ({r['ko']}) · {r['genre']} · {r['area']} · 타베로그 {r.get('t')} · 구글 {r.get('g')}({r.get('gn')}) · 휴무 {r['closed']}")
open(os.path.join(HERE, '여행계획_전체자료.md'), 'w', encoding='utf-8').write('\n'.join(out))
print('ok', len('\n'.join(out)))
