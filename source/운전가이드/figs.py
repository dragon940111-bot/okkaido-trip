# -*- coding: utf-8 -*-
# 상황별 예시 그림 (인라인 SVG). 일본 좌측통행 기준, 위에서 내려다본 도식.
# 좌표: 위 = 북쪽. 북쪽으로 가는 차는 도로의 서쪽 절반(왼쪽)을 달린다.
import math

def _ang(dx, dy):
    """진행 방향 벡터(화면 좌표) → rotate 각도 (0 = 위쪽)."""
    return math.degrees(math.atan2(dx, -dy))

def car(x, y, a, cls='me', label=None, lx=0, ly=0, anchor='middle'):
    g = (f'<g transform="translate({x:.1f} {y:.1f}) rotate({a:.1f})">'
         f'<rect class="car {cls}" x="-9" y="-16" width="18" height="32" rx="5"/>'
         f'<rect class="glass" x="-6" y="-11" width="12" height="7" rx="2"/></g>')
    if label:
        g += f'<text class="lb {cls}t" x="{x+lx:.1f}" y="{y+ly:.1f}" text-anchor="{anchor}">{label}</text>'
    return g

def ped(x, y):
    return (f'<g class="ped" transform="translate({x} {y})"><circle cx="0" cy="-7" r="3.2"/>'
            f'<path d="M0 -3 L0 5 M-5 0 L5 0 M0 5 L-4 12 M0 5 L4 12"/></g>')

def bike(x, y):
    return (f'<g class="bike" transform="translate({x} {y})"><circle cx="0" cy="-8" r="4"/><circle cx="0" cy="8" r="4"/>'
            f'<path d="M0 -8 L0 8 M-4 -3 L4 -3"/></g>')

def label(x, y, t, cls='lb', anchor='start'):
    return f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}">{t}</text>'

def num(x, y, n):
    return f'<g class="num"><circle cx="{x}" cy="{y}" r="9"/><text x="{x}" y="{y+4}" text-anchor="middle">{n}</text></g>'

DEFS = ('<defs>'
        '<marker id="ar-me" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path class="mk-me" d="M0 0 L10 5 L0 10 z"/></marker>'
        '<marker id="ar-go" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path class="mk-go" d="M0 0 L10 5 L0 10 z"/></marker>'
        '<marker id="ar-ot" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path class="mk-ot" d="M0 0 L10 5 L0 10 z"/></marker>'
        '</defs>')

def route(d, cls='me'):
    return f'<path class="rt {cls}r" d="{d}" marker-end="url(#ar-{cls})"/>'

def svg(body, w=360, h=300, title=''):
    return (f'<svg class="fig" viewBox="0 0 {w} {h}" role="img" aria-label="{title}">{DEFS}'
            f'<rect class="ground" x="0" y="0" width="{w}" height="{h}"/>{body}</svg>')

# ── 공통: 십자 교차로 (세로 140–220, 가로 110–190) ──
def cross(stop_n=True, crosswalks=True):
    s = ('<rect class="road" x="140" y="0" width="80" height="300"/>'
         '<rect class="road" x="0" y="110" width="360" height="80"/>'
         '<path class="cl" d="M180 0 V110 M180 190 V300 M0 150 H140 M220 150 H360"/>')
    if crosswalks:
        for x0, y0, w, h in ((140, 195, 80, 10), (140, 95, 80, 10), (125, 110, 10, 80), (225, 110, 10, 80)):
            if w > h:
                s += ''.join(f'<rect class="zebra" x="{x0+i*10+2}" y="{y0}" width="6" height="{h}"/>' for i in range(w // 10))
            else:
                s += ''.join(f'<rect class="zebra" x="{x0}" y="{y0+i*10+2}" width="{w}" height="6"/>' for i in range(h // 10))
    if stop_n:
        s += '<path class="stop" d="M140 212 H180"/>'
    return s

def fig_right():
    b = cross()
    b += route('M160 248 L160 178 C160 156 168 140 192 132 L340 130')
    b += '<circle class="wait" cx="168" cy="148" r="11"/>'
    b += car(160, 262, 0, 'me', '내 차', 20, 4, 'start')
    b += car(200, 52, 180, 'go', '맞은편 직진', 14, -2, 'start')
    b += route('M200 70 L200 286', 'go')
    b += ped(229, 126)
    b += num(124, 152, 1) + num(206, 98, 2) + num(250, 112, 3)
    return svg(b, title='우회전')

def fig_left():
    b = cross()
    b += route('M160 248 L160 214 C160 186 150 172 126 170 L14 170')
    b += car(160, 262, 0, 'me', '내 차', 20, 4, 'start')
    b += bike(147, 236)
    b += label(100, 236, '자전거', 'lb ot', 'end')
    b += ped(118, 180)
    b += num(124, 210, 1) + num(60, 150, 2)
    return svg(b, title='좌회전')

def fig_uturn():
    b = cross(crosswalks=False)
    b += route('M160 248 L160 165 C160 118 200 118 200 165 L200 286')
    b += car(160, 262, 0, 'me', '내 차', -16, 4, 'end')
    b += car(200, 40, 180, 'ot', '맞은편 차', 16, 0, 'start')
    # 転回禁止 표지 (이게 있으면 금지)
    b += ('<g transform="translate(300 245)"><circle class="sg-blue" r="22"/>'
          '<path class="sg-w" d="M-6 10 V-4 A7 7 0 0 1 8 -4 V4" fill="none"/><path class="sg-wf" d="M3 2 L8 10 L13 2 z"/>'
          '<path class="sg-redl" d="M-16 -16 L16 16"/><circle class="sg-ring" r="22"/></g>')
    b += label(300, 285, '転回禁止 → 유턴 금지', 'lb ng', 'middle')
    b += num(124, 140, 1) + num(226, 210, 2)
    return svg(b, title='유턴')

def fig_stop():
    b = ('<rect class="road" x="0" y="110" width="360" height="80"/>'
         '<rect class="road" x="140" y="190" width="60" height="110"/>'
         '<path class="cl" d="M0 150 H360"/>'
         '<path class="stop" d="M140 204 H170"/>')
    b += ('<g transform="translate(120 222)"><path class="sg-red" d="M-17 -12 L17 -12 L0 18 z"/>'
          '<text class="sg-txt" x="0" y="-2" text-anchor="middle">止まれ</text></g>')
    b += car(155, 228, 0, 'me', '내 차', -14, 6, 'end')
    b += car(300, 170, -90, 'go', '우선도로 차', 0, -16, 'middle')
    b += route('M282 170 L40 170', 'go')
    b += car(60, 130, 90, 'go')
    b += route('M78 130 L330 130', 'go')
    b += num(184, 210, 1) + num(184, 250, 2)
    return svg(b, title='일시정지')

def fig_rail():
    b = '<rect class="road" x="140" y="0" width="80" height="300"/><path class="cl" d="M180 0 V300"/>'
    b += '<rect class="rail-bed" x="0" y="120" width="360" height="44"/>'
    b += '<path class="rail" d="M0 132 H360 M0 152 H360"/>'
    b += ''.join(f'<rect class="sleeper" x="{x}" y="126" width="5" height="32"/>' for x in range(4, 360, 14))
    b += '<path class="stop" d="M140 190 H180"/>'
    # 차단기 + 경보기
    b += ('<g class="gate"><rect x="122" y="168" width="10" height="10" rx="2"/><path d="M132 173 H180"/>'
          '<circle class="lamp" cx="118" cy="160" r="5"/><circle class="lamp" cx="118" cy="174" r="5"/></g>')
    b += car(160, 222, 0, 'me', '내 차', -22, 6, 'end')
    b += route('M160 205 L160 40')
    b += label(300, 112, '← 열차 →', 'lb ng', 'middle')
    b += num(196, 200, 1) + num(196, 142, 2) + num(196, 70, 3)
    return svg(b, title='철길 건널목')

def _sig(x, y, lit, arrows=None, flash=False):
    """일본 가로형 신호: 왼쪽부터 초록·노랑·빨강."""
    cols = ['g', 'y', 'r']
    s = f'<g transform="translate({x} {y})"><rect class="sig-box" x="-42" y="-14" width="84" height="28" rx="6"/>'
    for i, c in enumerate(cols):
        cls = f'l-{c}' if c == lit else 'l-off'
        s += f'<circle class="{cls}" cx="{-26+i*26}" cy="0" r="10"/>'
        if c == lit and flash:
            s += f'<circle class="rays {c}" cx="{-26+i*26}" cy="0" r="15"/>'
    if arrows:
        s += f'<rect class="sig-box" x="-42" y="16" width="84" height="26" rx="6"/>'
        pos = {'L': -26, 'S': 0, 'R': 26}
        for k in ('L', 'S', 'R'):
            on = k in arrows
            cx = pos[k]
            s += f'<circle class="{"l-g" if on else "l-off"}" cx="{cx}" cy="29" r="9"/>'
            if on:
                d = {'L': f'M{cx+5} 29 H{cx-5} M{cx-1} 25 L{cx-5} 29 L{cx-1} 33',
                     'S': f'M{cx} 35 V23 M{cx-4} 27 L{cx} 23 L{cx+4} 27',
                     'R': f'M{cx-5} 29 H{cx+5} M{cx+1} 25 L{cx+5} 29 L{cx+1} 33'}[k]
                s += f'<path class="arw" d="{d}"/>'
    return s + '</g>'

def fig_signal():
    b = ''
    b += _sig(62, 70, 'r', arrows='LS')
    b += label(62, 140, '빨강 + 초록 화살표', 'lb', 'middle')
    b += label(62, 160, '화살표 방향만 진행', 'lb sm', 'middle')
    b += label(62, 178, '(여기선 좌회전·직진)', 'lb sm', 'middle')
    b += _sig(180, 70, 'y', flash=True)
    b += label(180, 140, '노랑 깜빡임', 'lb', 'middle')
    b += label(180, 160, '주위를 보며', 'lb sm', 'middle')
    b += label(180, 178, '천천히 진행 가능', 'lb sm', 'middle')
    b += _sig(298, 70, 'r', flash=True)
    b += label(298, 140, '빨강 깜빡임', 'lb ng', 'middle')
    b += label(298, 160, '정지선에서 멈춘 뒤', 'lb sm', 'middle')
    b += label(298, 178, '확인하고 진행', 'lb sm', 'middle')
    b += label(180, 232, '일본 신호등은 가로형이 많고 왼쪽부터 초록·노랑·빨강.', 'lb sm', 'middle')
    b += label(180, 252, '홋카이도는 눈 때문에 세로형도 많음 (위가 빨강).', 'lb sm', 'middle')
    return svg(b, h=270, title='신호')

def _clock(cx, cy, r, th):
    t = math.radians(th)
    return cx + r * math.sin(t), cy - r * math.cos(t)

def fig_round():
    cx, cy = 180, 150
    b = ('<rect class="road" x="140" y="0" width="80" height="300"/>'
         '<rect class="road" x="0" y="110" width="360" height="80"/>'
         f'<circle class="road" cx="{cx}" cy="{cy}" r="88"/>'
         f'<circle class="island" cx="{cx}" cy="{cy}" r="44"/>'
         f'<circle class="cl ring" cx="{cx}" cy="{cy}" r="66"/>')
    p1 = _clock(cx, cy, 66, 205); p2 = _clock(cx, cy, 66, 80)
    b += route(f'M160 286 L160 248 C160 230 {p1[0]-4:.1f} {p1[1]+12:.1f} {p1[0]:.1f} {p1[1]:.1f} '
               f'A66 66 0 1 1 {p2[0]:.1f} {p2[1]:.1f} C{p2[0]+10:.1f} {p2[1]-6:.1f} 262 130 280 130 L344 130')
    b += car(160, 272, 0, 'me', '내 차', -16, 6, 'end')
    q = _clock(cx, cy, 66, 140)
    t = math.radians(140)
    b += car(q[0], q[1], _ang(math.cos(t), math.sin(t)), 'go', '먼저 (링 안 차)', 18, 18, 'start')
    # 시계방향 표시
    for th in (20, 110, 290):
        a1 = _clock(cx, cy, 66, th); a2 = _clock(cx, cy, 66, th + 18)
        b += f'<path class="rt otr" d="M{a1[0]:.1f} {a1[1]:.1f} A66 66 0 0 1 {a2[0]:.1f} {a2[1]:.1f}" marker-end="url(#ar-ot)"/>'
    b += label(cx, cy + 5, '시계방향', 'lb sm', 'middle')
    b += num(128, 240, 1) + num(96, 120, 2) + num(300, 112, 3)
    return svg(b, title='로터리')

def fig_narrow():
    b = ('<rect class="road" x="160" y="0" width="54" height="300"/>'
         '<path class="road" d="M214 112 L244 122 L244 186 L214 196 z"/>'
         '<rect class="slope" x="0" y="0" width="150" height="300"/>')
    b += label(75, 40, '↑ 오르막 (위쪽이 높음)', 'lb', 'middle')
    b += car(229, 154, 180, 'ot', '내리막 차', 18, 4, 'start')
    b += label(300, 196, '대피 공간에서', 'lb sm', 'middle') + label(300, 212, '기다림', 'lb sm', 'middle')
    b += car(187, 236, 0, 'me', '내 차 (오르막)', -14, 6, 'end')
    b += route('M187 220 L187 30')
    b += num(212, 236, 1) + num(256, 140, 2)
    return svg(b, title='좁은 길 교행')

def fig_merge():
    b = ('<rect class="road" x="170" y="0" width="84" height="300"/>'
         '<path class="road" d="M30 300 C60 230 120 220 128 180 L170 40 L170 300 z"/>'
         '<path class="cl" d="M212 0 V300"/>'
         '<path class="edge" d="M170 300 V150"/>')
    b += label(191, 18, '走行', 'lb sm', 'middle') + label(233, 18, '追越', 'lb sm', 'middle')
    b += label(191, 34, '주행', 'lb sm', 'middle') + label(233, 34, '추월', 'lb sm', 'middle')
    b += car(150, 236, 12, 'me', '내 차', -16, 4, 'end')
    b += route('M152 220 L158 150 C160 128 172 112 190 104 L190 52')
    b += car(191, 262, 0, 'go', '본선 차', 16, 4, 'start')
    b += route('M191 246 L191 150', 'go')
    b += num(122, 200, 1) + num(136, 120, 2) + num(214, 80, 3)
    return svg(b, title='고속도로 합류')

def fig_etc():
    b = '<rect class="road" x="20" y="0" width="320" height="300"/>'
    lanes = [('ETC専用', 'etc', 60), ('ETC/一般', 'etc2', 140), ('一般', 'gen', 220), ('一般', 'gen', 300)]
    for t, c, x in lanes:
        b += f'<rect class="booth" x="{x-12}" y="118" width="24" height="44" rx="3"/>' if x != 60 else ''
        b += f'<rect class="lane-sign {c}" x="{x-34}" y="66" width="68" height="26" rx="4"/>'
        b += f'<text class="lane-t" x="{x}" y="84" text-anchor="middle">{t}</text>'
    b += '<path class="bar" d="M40 150 H96"/><circle class="bar-p" cx="40" cy="150" r="4"/>'
    b += ''.join(f'<path class="cl" d="M{x} 100 V300"/>' for x in (100, 180, 260))
    b += car(60, 250, 0, 'me', '20km/h 이하', 26, 6, 'start')
    b += route('M60 234 L60 40')
    b += num(26, 220, 1) + num(26, 150, 2) + num(26, 112, 3)
    return svg(b, title='ETC 차로')

FIGS = {
 'right': (fig_right, '우회전 (한국의 비보호 좌회전에 해당)', [
     '교차로 <b>중앙 바로 앞</b>까지 나가서 기다립니다(점선 원). 정지선 뒤에서 기다리지 않습니다.',
     '<b>맞은편 직진·좌회전 차가 먼저</b>. 다 지나간 뒤 돕니다. 신호가 노랑·빨강으로 바뀌는 중이면 남은 차가 빠질 때 조용히 마무리.',
     '돌아나간 길의 <b>왼쪽 차로</b>로 들어갑니다. 건너는 사람이 있으면 횡단보도 앞에서 멈춤.']),
 'left': (fig_left, '좌회전 (한국의 우회전처럼 작게)', [
     '미리 <b>왼쪽 끝 차로</b>에 붙고, 교차로 모서리를 따라 <b>작게</b> 돕니다.',
     '왼쪽 뒤 <b>자전거·오토바이</b>가 같이 들어오지 않는지 거울과 고개로 확인(말려들기 사고). 횡단보도 사람은 무조건 먼저.']),
 'uturn': (fig_uturn, '유턴 (転回)', [
     '<b>転回禁止 표지가 없는 곳</b>에서만. 교차로라면 우회전처럼 중앙까지 나가서 맞은편 차를 다 보낸 뒤 돕니다. 우회전 초록 화살표 때도 표지가 없으면 유턴할 수 있습니다(JAF).',
     '횡단보도·건널목 위, 언덕 꼭대기·급커브 근처, 고속도로에서는 금지. 애매하면 <b>블록을 한 바퀴</b> 도는 게 안전합니다.']),
 'stop': (fig_stop, '止まれ — 일시정지', [
     '빨간 역삼각형 止まれ가 보이면 <b>정지선에서 바퀴가 완전히 멈추게</b>. 2–3초 멈춤. 단속이 가장 많은 위반입니다.',
     '그다음 조금씩 앞으로 나가며 좌우를 봅니다. <b>오른쪽에서 오는 차가 내 앞 차로</b>(좌측통행)라 먼저 오른쪽, 그다음 왼쪽.']),
 'rail': (fig_rail, '철길 건널목 (踏切)', [
     '신호가 없어도 <b>정지선에서 반드시 멈춤</b>. 경보음이 울리거나 차단기가 내려오는 중이면 들어가지 않습니다.',
     '창문을 조금 열고 좌우를 <b>보고 듣기</b>.',
     '건너편에 내 차가 들어갈 <b>빈자리가 있을 때만</b> 출발, 건널목 안에서는 멈추지 않고 한 번에.']),
 'signal': (fig_signal, '신호 읽기', []),
 'round': (fig_round, '로터리 (ラウンドアバウト)', [
     '들어가기 전 속도를 줄이고 <b>링 안 차(오른쪽에서 옴)가 먼저</b>. 들어갈 때는 깜빡이 없이 왼쪽으로.',
     '링 안은 <b>시계방향</b>으로 돕니다.',
     '나가기 바로 전 출구에서 <b>왼쪽 깜빡이</b>를 켜고 빠집니다.']),
 'narrow': (fig_narrow, '좁은 길·산길에서 마주쳤을 때', [
     '<b>오르막 차가 우선</b>입니다(내리막에서 출발이 더 쉬워서). 단, 가까이에 대피 공간이 있는 쪽이 들어가 기다리는 게 보통입니다.',
     '내리막 차는 대피 공간(待避所, 다이히조)에 들어가 기다립니다. 서로 눈인사 후 천천히.']),
 'merge': (fig_merge, '고속도로 합류', [
     '가속 차로를 <b>끝까지 쓰며</b> 본선 속도(80–100km/h)까지 올립니다. 가속 차로 중간에서 멈추지 않기.',
     '<b>오른쪽 깜빡이</b> + 오른쪽 뒤를 고개로 확인.',
     '본선 <b>왼쪽 차로(走行車線)</b>로 들어갑니다. 오른쪽 차로(追越車線)는 추월할 때만 쓰고 끝나면 돌아옵니다.']),
 'etc': (fig_etc, 'ETC 차로 지나가기', [
     '요금소 앞 표지에서 <b>보라색 ETC専用</b> 또는 <b>ETC/一般</b> 차로를 고릅니다. 초록 一般은 ETC 카드 없는 차용.',
     '<b>20km/h 이하</b>로 들어갑니다. 차단기는 일부러 늦게 열리게 해 둔 곳이 많습니다.',
     '차단기가 안 열리면 <b>그 자리에서 멈추고 후진하지 않기</b>. 비상등 켜고 인터폰·직원을 기다립니다.']),
}
