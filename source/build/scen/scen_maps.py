# 대안 A–G 경로 지도 (v19). 실행: build/ 에서  python3 scen/scen_maps.py [지도이름 ...]
# daymaps.py의 그리기 방식(OSM 타일 + OSRM 경로 + 번호 핀 + 라벨)을 그대로 따르되,
#  - 대안 데이터(scen/scen_*.py의 SCN[...]['map'] / map2)에서 좌표·라벨·순서를 읽고
#  - 핀이 겹치면 옆으로 비켜 그리고 지시선으로 실제 위치를 잇고
#  - 구간마다 이동 수단(차·택시·도보·지하철)을 다르게 그림.
import math, os, subprocess, json, time, sys, runpy
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(HERE)
UA_T = 'HokkaidoTripPlanner/1.0 (personal one-off map)'
FB = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def font(sz): return ImageFont.truetype(FB, sz, index=1)
SYM = lambda sz: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', sz)
COL = {2: (28, 126, 214), 3: (47, 158, 68), 'A': (200, 120, 0), 'B': (0, 128, 140), 'D': (162, 62, 98),
       'E': (94, 122, 30), 'F': (61, 111, 176), 'G': (156, 74, 26)}
SUBWAY = (201, 42, 42)

def px(lat, lon, z):
    n = 256 * 2 ** z; x = (lon + 180) / 360 * n
    y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n
    return x, y

def tile(z, x, y):
    os.makedirs('tiles', exist_ok=True)
    p = f'tiles/{z}_{x}_{y}.png'
    if not os.path.exists(p) or os.path.getsize(p) < 100:
        for att in range(3):
            code = subprocess.run(['curl', '-s', '-A', UA_T, '-o', p, '-w', '%{http_code}',
                                   f'https://tile.openstreetmap.org/{z}/{x}/{y}.png'], capture_output=True, text=True).stdout
            if code == '200': break
            time.sleep(2)
        else:
            raise SystemExit(f'tile failed {z}/{x}/{y} code {code}')
        time.sleep(0.12)
    return Image.open(p).convert('RGB')

def osrm(pts):
    coords = ';'.join(f'{lon},{lat}' for lat, lon in pts)
    for att in range(3):
        out = subprocess.run(['curl', '-s', f'https://router.project-osrm.org/route/v1/driving/{coords}?overview=full&geometries=geojson'],
                             capture_output=True, text=True).stdout
        try:
            r = json.loads(out)
            if r.get('code') == 'Ok': break
        except Exception:
            pass
        time.sleep(3)
    else:
        raise SystemExit('OSRM failed: ' + out[:200])
    rt = r['routes'][0]; time.sleep(1)
    return rt['geometry']['coordinates'], rt['distance'] / 1000, [l['duration'] / 60 for l in rt['legs']]

def hav(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))

def dashed(dr, pts, fill, width, on=14, off=10):
    """pts 폴리라인을 점선으로."""
    carry = 0.0; draw = True
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        L = math.hypot(x2 - x1, y2 - y1)
        if L == 0: continue
        pos = 0.0
        while pos < L:
            seg = (on if draw else off) - carry
            end = min(L, pos + seg)
            if draw:
                dr.line((x1 + (x2 - x1) * pos / L, y1 + (y2 - y1) * pos / L, x1 + (x2 - x1) * end / L, y1 + (y2 - y1) * end / L), fill=fill, width=width)
            if end - pos < seg:
                carry += end - pos
            else:
                carry = 0.0; draw = not draw
            pos = end

def render_inset(inset, lines, P, stops, col, size):
    """확대도: inset['keys']의 지점을 높은 줌으로 다시 그린 작은 지도 (번호 핀만)."""
    iw, ih = size
    keys = inset['keys']
    pts = [P[k] for k in keys]
    lats = [p[0] for p in pts]; lons = [p[1] for p in pts]
    la0, la1, lo0, lo1 = min(lats), max(lats), min(lons), max(lons)
    for z in range(inset.get('zmax', 16), 8, -1):
        x0, y0 = px(la1, lo0, z); x1, y1 = px(la0, lo1, z)
        if (x1 - x0) + 110 <= iw and (y1 - y0) + 130 <= ih: break
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 10
    X0, Y0 = cx - iw / 2, cy - ih / 2
    tx0, ty0, tx1, ty1 = int(X0 // 256), int(Y0 // 256), int((X0 + iw) // 256), int((Y0 + ih) // 256)
    im = Image.new('RGB', ((tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256))
    for tx in range(tx0, tx1 + 1):
        for ty in range(ty0, ty1 + 1): im.paste(tile(z, tx, ty), ((tx - tx0) * 256, (ty - ty0) * 256))
    ox, oy = X0 - tx0 * 256, Y0 - ty0 * 256
    im = im.crop((int(ox), int(oy), int(ox + iw), int(oy + ih)))
    im = ImageEnhance.Color(im).enhance(0.5); im = Image.blend(im, Image.new('RGB', im.size, (255, 255, 255)), 0.25)
    f = lambda lat, lon: (px(lat, lon, z)[0] - X0, px(lat, lon, z)[1] - Y0)
    dr = ImageDraw.Draw(im, 'RGBA')
    for mode, lp in lines:
        xy = [f(*p) for p in lp]
        if mode == 'car': dr.line(xy, fill=(255, 255, 255), width=10, joint='curve'); dr.line(xy, fill=col, width=6, joint='curve')
        elif mode == 'taxi': dr.line(xy, fill=(255, 255, 255), width=8, joint='curve'); dr.line(xy, fill=col, width=4, joint='curve')
        elif mode == 'walk': dashed(dr, xy, (255, 255, 255), 9, 14, 8); dashed(dr, xy, col, 4, 10, 10)
        else: dashed(dr, xy, (255, 255, 255), 8, 16, 6); dashed(dr, xy, SUBWAY, 4, 12, 10)
    placed = []
    numof = {k: n for k, n, _ in stops}
    r = 16
    for k in keys:
        x, y = f(*P[k]); qx, qy = x, y
        if any(math.hypot(x - a, y - b) < 36 for a, b in placed):
            for rad in (44, 64, 84):
                ok = False
                for da in range(0, 360, 30):
                    qx = x + rad * math.cos(math.radians(da - 90)); qy = y + rad * math.sin(math.radians(da - 90))
                    if 24 < qx < iw - 24 and 50 < qy < ih - 24 and not any(math.hypot(qx - a, qy - b) < 38 for a, b in placed):
                        ok = True; break
                if ok: break
            dr.line((x, y, qx, qy), fill=(255, 255, 255), width=5); dr.line((x, y, qx, qy), fill=col, width=2)
            dr.ellipse((x - 5, y - 5, x + 5, y + 5), fill=col, outline=(255, 255, 255), width=2)
        placed.append((qx, qy))
        dr.ellipse((qx - r - 3, qy - r - 3, qx + r + 3, qy + r + 3), fill=(255, 255, 255)); dr.ellipse((qx - r, qy - r, qx + r, qy + r), fill=col)
        dr.text((qx, qy + 1), numof[k], font=font(19), fill=(255, 255, 255), anchor='mm')
    t = inset['title']; TF = font(19)
    dr.rounded_rectangle((8, 8, 8 + TF.getlength(t) + 20, 38), radius=6, fill=(255, 255, 255, 235))
    dr.text((18, 23), t, font=TF, fill=col, anchor='lm')
    fr = Image.new('RGB', (iw, ih), (255, 255, 255))
    fr.paste(im.crop((3, 3, iw - 3, ih - 3)), (3, 3))
    ImageDraw.Draw(fr).rectangle((0, 0, iw - 1, ih - 1), outline=col, width=3)
    return fr

def render(name, col, P, legs, stops, title, zmax=13, legend=False, note=None, inset=None):
    """P: {키:(위도,경도)}; legs: [(출발키, 도착키, 수단, [경유 (위도,경도)...])] 수단 = car|taxi|walk|subway
       stops: [(키, 번호, 라벨)] (숙소 제외)"""
    # 1) 구간별 선 모양 계산 (같은 수단의 연속 차 구간은 OSRM 한 번에)
    lines = []; info = {'km': 0.0, 'legs': [], 'modes': []}
    i = 0
    while i < len(legs):
        a, b, mode, via = legs[i]
        if mode in ('car', 'taxi'):
            j = i; pts = [P[a]]; legidx = []
            while j < len(legs) and legs[j][2] == mode and (j == i or legs[j][0] == legs[j - 1][1]):
                for v in legs[j][3]: pts.append(v)
                pts.append(P[legs[j][1]]); legidx.append(len(pts) - 1); j += 1
            geom, km, lmins = osrm(pts)
            lines.append((mode, [(la, lo) for lo, la in geom]))
            info['km'] += km
            # 경유점이 있으면 OSRM leg가 더 많음 → 정거장 단위로 합치기
            stopsum = []; acc = 0.0; k = 0
            for pi in range(1, len(pts)):
                acc += lmins[pi - 1]
                if pi in legidx: stopsum.append(round(acc)); acc = 0.0
            info['legs'] += stopsum; info['modes'] += [mode] * len(stopsum)
            i = j
        else:
            pts = [P[a]] + list(via) + [P[b]]
            lines.append((mode, pts))
            d = sum(hav(p, q) for p, q in zip(pts, pts[1:]))
            if mode == 'walk':
                info['km'] += d * 1.3; info['legs'].append(round(d * 1.3 / 4.5 * 60))
            else:
                info['km'] += d; info['legs'].append(round(d / 30 * 60 + 4))
            info['modes'].append(mode)
            i += 1
    # 2) 범위·줌
    allp = [p for _, pts in lines for p in pts] + [P[k] for k, _, _ in stops]
    lats = [p[0] for p in allp]; lons = [p[1] for p in allp]
    la0, la1, lo0, lo1 = min(lats), max(lats), min(lons), max(lons)
    for z in range(zmax, 6, -1):
        x0, y0 = px(la1, lo0, z); x1, y1 = px(la0, lo1, z)
        if (x1 - x0) * 1.22 <= 1500 and (y1 - y0) * 1.3 <= 1050: break
    padx = max((x1 - x0) * 0.12, 60); pady = max((y1 - y0) * 0.15, 70)
    W = max(x1 - x0 + 2 * padx, 1150); H = max(y1 - y0 + 2 * pady, 720)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; X0, Y0 = cx - W / 2, cy - H / 2
    tx0, ty0, tx1, ty1 = int(X0 // 256), int(Y0 // 256), int((X0 + W) // 256), int((Y0 + H) // 256)
    im = Image.new('RGB', ((tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256))
    for tx in range(tx0, tx1 + 1):
        for ty in range(ty0, ty1 + 1): im.paste(tile(z, tx, ty), ((tx - tx0) * 256, (ty - ty0) * 256))
    ox, oy = X0 - tx0 * 256, Y0 - ty0 * 256
    im = im.crop((int(ox), int(oy), int(ox + W), int(oy + H)))
    im = ImageEnhance.Color(im).enhance(0.5); im = Image.blend(im, Image.new('RGB', im.size, (255, 255, 255)), 0.25)
    f = lambda lat, lon: (px(lat, lon, z)[0] - X0, px(lat, lon, z)[1] - Y0)
    dr = ImageDraw.Draw(im, 'RGBA')
    Wi, Hi = im.size
    # 3) 선
    for mode, pts in lines:
        xy = [f(*p) for p in pts]
        if mode == 'car':
            dr.line(xy, fill=(255, 255, 255), width=12, joint='curve'); dr.line(xy, fill=col, width=7, joint='curve')
        elif mode == 'taxi':
            dr.line(xy, fill=(255, 255, 255), width=10, joint='curve'); dr.line(xy, fill=col, width=5, joint='curve')
        elif mode == 'walk':
            dashed(dr, xy, (255, 255, 255), 10, 16, 8); dashed(dr, xy, col, 5, 12, 12)
        elif mode == 'subway':
            dashed(dr, xy, (255, 255, 255), 9, 18, 6); dashed(dr, xy, SUBWAY, 5, 14, 10)
    # 4) 숙소 별
    boxes = [(10, 10, Wi - 10, 70)]  # 제목 띠
    placed = []
    lx, ly = f(*P['lodging']); r = 19
    dr.ellipse((lx - r - 4, ly - r - 4, lx + r + 4, ly + r + 4), fill=(255, 255, 255)); dr.ellipse((lx - r, ly - r, lx + r, ly + r), fill=(201, 42, 42))
    dr.text((lx, ly + 1), '★', font=SYM(26), fill=(255, 255, 255), anchor='mm')
    LT = font(26); tw = LT.getlength('숙소')
    if lx - 30 - tw > 6:
        dr.text((lx - 30, ly - 24), '숙소', font=LT, fill=(201, 42, 42), stroke_width=4, stroke_fill=(255, 255, 255), anchor='rm')
        boxes.append((lx - 30 - tw, ly - 40, lx - 30, ly - 8))
    else:
        dr.text((lx + 30, ly - 24), '숙소', font=LT, fill=(201, 42, 42), stroke_width=4, stroke_fill=(255, 255, 255), anchor='lm')
        boxes.append((lx + 30, ly - 40, lx + 30 + tw, ly - 8))
    placed.append((lx, ly)); boxes.append((lx - 26, ly - 26, lx + 26, ly + 26))
    # 5) 번호 핀 위치 (겹치면 비켜 놓기)
    pins = []
    def near(x, y, d=46): return any(math.hypot(x - a, y - b) < d for a, b in placed)
    for k, num, t in stops:
        x, y = f(*P[k]); px_, py_ = x, y
        if near(x, y):
            cand = []
            # 무리 중심의 반대쪽부터
            cxm = sum(a for a, _ in placed) / len(placed); cym = sum(b for _, b in placed) / len(placed)
            base = math.atan2(y - cym, x - cxm)
            for rad in (58, 82, 108, 136):
                for da in (0, 30, -30, 60, -60, 90, -90, 120, -120, 150, -150, 180):
                    ang = base + math.radians(da)
                    cand.append((x + rad * math.cos(ang), y + rad * math.sin(ang)))
            for qx, qy in cand:
                if 30 < qx < Wi - 30 and 90 < qy < Hi - 40 and not near(qx, qy, 48):
                    px_, py_ = qx, qy; break
        placed.append((px_, py_)); pins.append((k, num, t, x, y, px_, py_))
        boxes.append((px_ - 22, py_ - 22, px_ + 22, py_ + 22))
    def hit(b): return any(not (b[2] < o[0] or b[0] > o[2] or b[3] < o[1] or b[1] > o[3]) for o in boxes)
    # 범례·메모 상자 크기
    LF = font(20); rowh = 30
    lused = [m for m in ('car', 'taxi', 'walk', 'subway') if any(mm == m for mm, _ in lines)] if legend else []
    lnames = {'car': '차', 'taxi': '택시', 'walk': '걸어서', 'subway': '지하철 南北線'}
    iboxes = []
    for ins in ([inset] if isinstance(inset, dict) else (inset or [])):
        iw, ih = ins.get('size', (420, 320)); ibox = None
        cands = [(14, Hi - 34 - ih), (Wi - 14 - iw, Hi - 34 - ih), (Wi - 14 - iw, 84), (14, 84), (14, (Hi - ih) / 2), (Wi - 14 - iw, (Hi - ih) / 2)]
        for bx0, by0 in cands:
            b = (bx0, by0, bx0 + iw, by0 + ih)
            if not hit(b): ibox = b; break
        if not ibox: raise SystemExit(f'{name}: no room for inset {ins["title"]}')
        boxes.append(ibox); iboxes.append((ins, ibox))
    lbox = None
    if lused or note:
        wbox = (70 + max(LF.getlength(lnames[m]) for m in lused) + 20) if lused else 0
        if note: wbox = max(wbox, LF.getlength(note) + 30)
        hb = rowh * len(lused) + 16 + (rowh if note else 0)
        for bx0, by0 in ((14, Hi - 34 - hb), (Wi - 14 - wbox, Hi - 40 - hb), (Wi - 14 - wbox, 84), (14, 84)):
            b = (bx0, by0, bx0 + wbox, by0 + hb)
            if not hit(b): lbox = b; break
        if not lbox: raise SystemExit(f'{name}: no room for legend')
        boxes.append(lbox)
    # 확대도 자리
    for k, num, t, x, y, qx, qy in pins:
        if (qx, qy) != (x, y):
            dr.line((x, y, qx, qy), fill=(255, 255, 255), width=6); dr.line((x, y, qx, qy), fill=col, width=3)
            dr.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(255, 255, 255)); dr.ellipse((x - 4, y - 4, x + 4, y + 4), fill=col)
    for k, num, t, x, y, qx, qy in pins:
        r = 19
        dr.ellipse((qx - r - 3, qy - r - 3, qx + r + 3, qy + r + 3), fill=(255, 255, 255)); dr.ellipse((qx - r, qy - r, qx + r, qy + r), fill=col)
        dr.text((qx, qy + 1), num, font=font(22), fill=(255, 255, 255), anchor='mm')
    # 6) 라벨
    FT = font(26)
    for k, num, t, x, y, qx, qy in pins:
        tw = FT.getlength(t); th = 30
        cands = [(qx + 28, qy, 'lm'), (qx - 28, qy, 'rm'), (qx + 22, qy - 34, 'lm'), (qx + 22, qy + 34, 'lm'), (qx - 22, qy - 34, 'rm'), (qx - 22, qy + 34, 'rm'),
                 (qx + 30, qy - 62, 'lm'), (qx + 30, qy + 62, 'lm'), (qx - 30, qy - 62, 'rm'), (qx - 30, qy + 62, 'rm'),
                 (qx + 40, qy - 92, 'lm'), (qx + 40, qy + 92, 'lm'), (qx - 40, qy - 92, 'rm'), (qx - 40, qy + 92, 'rm')]
        best = None
        for cx_, cy_, an in cands:
            b = (cx_, cy_ - th / 2, cx_ + tw, cy_ + th / 2) if an == 'lm' else (cx_ - tw, cy_ - th / 2, cx_, cy_ + th / 2)
            if b[0] < 4 or b[2] > Wi - 4 or b[1] < 74 or b[3] > Hi - 24: continue
            if not hit(b): best = (cx_, cy_, an, b); break
        if not best:
            raise SystemExit(f'{name}: no room for label {t}')
        cx_, cy_, an, b = best; boxes.append(b)
        if abs(cy_ - qy) > 40: dr.line((qx, qy, cx_, cy_), fill=col, width=2)
        dr.text((cx_, cy_), t, font=FT, fill=(20, 20, 20), stroke_width=5, stroke_fill=(255, 255, 255), anchor=an)
    # 7) 제목·범례·출처
    tw = font(30).getlength(title)
    dr.rounded_rectangle((14, 14, 14 + tw + 36, 66), radius=10, fill=(255, 255, 255, 235))
    dr.text((32, 40), title, font=font(30), fill=col, anchor='lm')
    if lbox:
        bx0, by0, bx1, by1 = lbox
        dr.rounded_rectangle(lbox, radius=8, fill=(255, 255, 255, 235), outline=(200, 200, 200))
        yy = by0 + 8 + rowh / 2
        for m in lused:
            seg = [(bx0 + 14, yy), (bx0 + 60, yy)]
            if m == 'car': dr.line(seg, fill=col, width=7)
            elif m == 'taxi': dr.line(seg, fill=col, width=5)
            elif m == 'walk': dashed(dr, seg, col, 5, 12, 12)
            else: dashed(dr, seg, SUBWAY, 5, 14, 10)
            dr.text((bx0 + 70, yy), lnames[m], font=LF, fill=(40, 40, 40), anchor='lm'); yy += rowh
        if note: dr.text((bx0 + 14, yy), note, font=LF, fill=(90, 90, 90), anchor='lm')
    for ins, ibox in iboxes:
        sub = render_inset(ins, lines, P, stops, col, (int(ibox[2] - ibox[0]), int(ibox[3] - ibox[1])))
        im.paste(sub, (int(ibox[0]), int(ibox[1])))
        dr = ImageDraw.Draw(im, 'RGBA')
    dr.text((Wi - 12, Hi - 10), '© OpenStreetMap contributors', font=font(14), fill=(80, 80, 80), anchor='rd', stroke_width=2, stroke_fill=(255, 255, 255))
    os.makedirs('site/map', exist_ok=True)
    im.save(f'site/map/{name}.jpg', quality=80, optimize=True, progressive=True)
    out = {'size': list(im.size), 'km': round(info['km']), 'legs': info['legs'], 'modes': info['modes'], 'zoom': z}
    print(name, out, os.path.getsize(f'site/map/{name}.jpg'), flush=True)
    return out

# ── 데이터 읽기 ──
SCN = {}
for fn in ('scen_A', 'scen_B', 'scen_C', 'scen_D', 'scen_EF', 'scen_G'):
    SCN.update(runpy.run_path(f'scen/{fn}.py')['SCN'])

LABEL = {'okina': '다테 오키나 (소바)', 'lakehill': '레이크힐 팜 (젤라토)', 'usuzan': '쇼와신잔 · 우스잔',
         'jigokudani': '노보리베쓰 지옥계곡', 'bibi': '로그하우스 비비 (와규)',
         'saimi': '멘야 사이미 (미소라멘)', 'daibutsu': '두대불', 'pathos': '르타오 파토스',
         'canal': '오타루 운하 · 사카이마치', 'uomasa': '우오마사 (스시·해산물)',
         'd_ageimo': '나카야마 고개 (아게이모)'}
def from_map(m, label=None):
    label = {**LABEL, **(label or {})}
    P = {}; stops = []; n = 0
    for k, la, lo, lab in m:
        if k == 'lodging':
            P['lodging'] = (la, lo); continue
        n += 1; P[k] = (la, lo); stops.append((k, str(n), label.get(k, lab)))
    return P, stops

def check_nums(key, day, stops, alias=None):
    """시간표의 지도번호와 지도 핀 번호가 같은지 검사."""
    alias = alias or {}
    nums = {}
    for it in day['items']:
        if it[5]:
            ref = it[2]
            refs = ref if isinstance(ref, tuple) else (ref,)
            nums.setdefault(it[5], []).extend(refs)
    want = sorted(nums, key=int)
    got = [s[1] for s in stops]
    assert want == got, f'{key}: 시간표 번호 {want} != 지도 번호 {got}'
    for k, num, lab in stops:
        refs = [alias.get(r, r) for r in nums[num] if r]
        ok = k in refs or any(k in str(r) or str(r) in k for r in refs) or any(r.startswith('day') for r in refs)
        print(f'  {key} #{num} 지도:{k:<14} 시간표:{nums[num]}  {"OK" if ok else "확인 필요"}')
    return True

res = {}
ONLY = sys.argv[1:]
def go(name, *a, **k):
    if ONLY and name not in ONLY: return
    res[name] = render(name, *a, **k)

# A 오비히로
s = SCN['A']; P, st = from_map(s['map']); check_nums('A', s['days'][0], st)
L = [('lodging', 'a_shirakaba', 'car', []), ('a_shirakaba', 'a_kofuku', 'car', []), ('a_kofuku', 'a_manabe', 'car', []),
     ('a_manabe', 'a_rokkatei', 'car', []), ('a_rokkatei', 'a_tonta', 'car', []), ('a_tonta', 'lodging', 'car', [])]
go('sa', COL['A'], P, L, st, '대안 A · 11/3 오비히로·도카치 당일치기',
   inset=dict(keys=['a_shirakaba', 'a_kofuku', 'a_manabe', 'a_rokkatei', 'a_tonta'], title='오비히로 부근 확대', size=(390, 330)))

# B 소운쿄
s = SCN['B']; P, st = from_map(s['map']); check_nums('B', s['days'][0], st)
L = [('lodging', 'b_asahi', 'car', []), ('b_asahi', 'b_kurodake', 'car', []), ('b_kurodake', 'b_ginga', 'car', []),
     ('b_ginga', 'b_daikokuya', 'car', []), ('b_daikokuya', 'lodging', 'car', [])]
go('sb', COL['B'], P, L, st, '대안 B · 11/5 소운쿄·구로다케 + 아사히카와')

# C 맞바꾸기 (두 날)
s = SCN['C']
P, st = from_map(s['map']); check_nums('C-11/3', s['days'][0], st)
VIA_TMK = (42.6420, 141.5600)  # 원래 11/4 지도와 같은 道央道 경유점
L = [('lodging', 'okina', 'car', [VIA_TMK]), ('okina', 'lakehill', 'car', []), ('lakehill', 'usuzan', 'car', []),
     ('usuzan', 'jigokudani', 'car', []), ('jigokudani', 'bibi', 'car', []), ('bibi', 'lodging', 'car', [])]
go('sc1', COL[3], P, L, st, '대안 C · 11/3 남쪽 루프 (11/4와 맞바꾼 날)')
P, st = from_map(s['map2'], {'canal': '오타루 운하'}); check_nums('C-11/4', s['days'][1], st)
L = [('lodging', 'saimi', 'car', []), ('saimi', 'daibutsu', 'car', []), ('daibutsu', 'pathos', 'car', []),
     ('pathos', 'canal', 'walk', []), ('canal', 'uomasa', 'walk', []), ('uomasa', 'lodging', 'car', [])]
go('sc2', COL[2], P, L, st, '대안 C · 11/4 삿포로 남쪽 → 오타루', zmax=13, legend=True,
   inset=dict(keys=['pathos', 'canal', 'uomasa'], title='오타루 확대', size=(360, 300)))

# D 니세코
s = SCN['D']; P, st = from_map(s['map']); check_nums('D', s['days'][0], st)
VIA_NIKI = (43.1556, 140.7672)  # 귀갓길: 굿찬 → 국도 5 → 仁木 → 後志道
L = [('lodging', 'd_ageimo', 'car', []), ('d_ageimo', 'd_fukidashi', 'car', []), ('d_fukidashi', 'd_jin', 'car', []),
     ('d_jin', 'd_makkarina', 'car', []), ('d_makkarina', 'd_takahashi', 'car', []), ('d_takahashi', 'lodging', 'car', [VIA_NIKI])]
go('sd', COL['D'], P, L, st, '대안 D · 11/5 니세코·요테이산')

# E 요이치
s = SCN['E']; P, st = from_map(s['map'], {'pathos': '르타오 파토스 · 운하'}); check_nums('E', s['days'][0], st)
L = [('lodging', 'saimi', 'car', []), ('saimi', 'e_nikka', 'car', []), ('e_nikka', 'e_kakizaki', 'walk', []),
     ('e_kakizaki', 'pathos', 'car', []), ('pathos', 'soyogi', 'walk', []), ('soyogi', 'lodging', 'car', [])]
go('se', COL['E'], P, L, st, '대안 E · 11/3 두대불 대신 요이치 닛카 증류소', legend=True,
   inset=[dict(keys=['e_nikka', 'e_kakizaki'], title='요이치역 앞 확대', size=(300, 260)),
          dict(keys=['pathos', 'soyogi'], title='오타루 확대', size=(300, 260))])

# F 11/2 오후 삿포로 시내 (숙소에 차를 두고 걷기)
SEIMON = (43.0706, 141.3485)  # 홋카이도대학 정문 (西5丁目通)
s = SCN['F']; P, st = from_map(s['map']); check_nums('F', s['days'][0], st, {'f_hokudai': 'f_hokudai'})
L = [('lodging', 'f_hokudai', 'walk', []), ('f_hokudai', 'f_akarenga', 'walk', [SEIMON]), ('f_akarenga', 'f_tokeidai', 'walk', []),
     ('f_tokeidai', 'ranban', 'walk', []), ('ranban', 'suage', 'walk', []), ('suage', 'f_odori', 'walk', []),
     ('f_odori', 'shirokuma', 'walk', []), ('shirokuma', 'lodging', 'subway', [])]
go('sf', COL['F'], P, L, st, '대안 F · 11/2 오후 삿포로 시내 (차는 숙소에)', zmax=14, legend=True,
   note='공항 → 도마코마이 점심 → 숙소는 차 (DAY 1과 같음)')

# G 11/5 삿포로 하루 (차 없이)
s = SCN['G']; P, st = from_map(s['map'])
check_nums('G', s['days'][0], st, {'f_hokudai': 'hokudai', 'f_akarenga': 'akarenga', 'f_clock': 'clocktower',
                                    'f_tvtower': 'tvtower', 'g_beermuseum': 'beermuseum'})
P['seimon'] = SEIMON
L = [('lodging', 'hokudai', 'walk', []), ('hokudai', 'seimon', 'walk', []), ('seimon', 'meshiya', 'taxi', []), ('meshiya', 'beermuseum', 'taxi', []),
     ('beermuseum', 'akarenga', 'taxi', []), ('akarenga', 'clocktower', 'walk', []), ('clocktower', 'tvtower', 'walk', []),
     ('tvtower', 'saera', 'walk', []), ('saera', 'lodging', 'subway', [])]
go('sg', COL['G'], P, L, st, '대안 G · 11/5 삿포로 시내 하루 (차 없이)', zmax=15, legend=True)

if res:
    path = 'scen/scen_maps.json'
    old = json.load(open(path)) if os.path.exists(path) else {}
    old.update(res)
    json.dump(old, open(path, 'w'), ensure_ascii=False, indent=1)
    print('saved', path, sorted(old))
