# usage: python3 -I scen/thumbs.py <sheetname> <category>[:min_w] ...   -> scen/th/<sheet>.jpg contact sheet + scen/th/<sheet>.json index
import json, subprocess, time, os, sys, hashlib
from PIL import Image, ImageDraw
UA = 'HokkaidoTripPlanner/1.0 (personal itinerary)'
db = json.load(open('scen/cats_new.json'))
used = set()
P = json.load(open('photos.json'))
for v in P.values():
    for x in v:
        used.add(x[1])
for v in json.load(open('img/meta.json')).values():
    used.add(v['file'])
sheet = sys.argv[1]
items = []
seen = set()
for arg in sys.argv[2:]:
    c, _, mw = arg.partition(':')
    mw = int(mw or 500)
    for f, w, h, t in db[c]['files']:
        if f in seen or f in used or not t:
            continue
        if w and w < mw:
            continue
        if not f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            continue
        seen.add(f)
        items.append([f, w, h, t, c])
items = items[:int(os.environ.get('MAXN', '400'))]
os.makedirs('scen/th', exist_ok=True)
tiles = []
for i, (f, w, h, t, c) in enumerate(items):
    fn = 'scen/th/t_' + hashlib.md5(f.encode()).hexdigest()[:12] + '.jpg'
    if not os.path.exists(fn):
        for att in range(3):
            code = subprocess.run(['curl', '-s', '-A', UA, '-o', fn, '-w', '%{http_code}', t], capture_output=True, text=True).stdout
            if code == '200':
                break
            if os.path.exists(fn):
                os.remove(fn)
            time.sleep(6)
        time.sleep(1.2)
    try:
        im = Image.open(fn).convert('RGB')
    except Exception:
        im = Image.new('RGB', (120, 90), (80, 0, 0))
    tiles.append(im)
    print(i, w, h, f[:80], flush=True)
json.dump(items, open(f'scen/th/{sheet}.json', 'w'), ensure_ascii=False, indent=0)
C = 8
T = 150
rows = (len(tiles) + C - 1) // C
S = Image.new('RGB', (C * T, rows * (T + 4)), (255, 255, 255))
d = ImageDraw.Draw(S)
for i, im in enumerate(tiles):
    im.thumbnail((T - 4, T - 18))
    x, y = (i % C) * T, (i // C) * (T + 4)
    S.paste(im, (x + 2, y + 16))
    d.rectangle([x, y, x + 34, y + 14], fill=(0, 0, 0))
    d.text((x + 3, y + 2), str(i), fill=(255, 255, 0))
S.save(f'scen/th/{sheet}.jpg', quality=80)
print('sheet', sheet, len(tiles))
