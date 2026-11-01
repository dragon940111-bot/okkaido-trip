# reads scen/picks.json + scen/meta_raw.json; downloads img/<imgkey>.jpg (<=560px) for picks with a free license + author
import json, subprocess, time, urllib.parse, os, hashlib, re
from PIL import Image
UA = 'HokkaidoTripPlanner/1.0 (personal itinerary)'
picks = json.load(open('scen/picks.json'))
raw = json.load(open('scen/meta_raw.json'))
DIM = {}
for c in json.load(open('scen/cats_new.json')).values():
    for f, w, h, t in c['files']:
        DIM[f] = w
FREE = re.compile(r'creativecommons\.org/(licenses/(by|by-sa)/|publicdomain/)|Public_domain|wikipedia/commons/.*PD', re.I)


def ok(m):
    if not m or not m.get('license') or not m.get('author'):
        return False
    if re.search(r'-nc|-nd|/nc|/nd', m['license'], re.I):
        return False
    return bool(FREE.search(m['license']))


todo = [(k, f) for c, k, f, cap in picks if ok(raw.get(f))]
os.makedirs('scen/dl', exist_ok=True)
for rnd in range(10):
    left = [(k, f) for k, f in todo if not os.path.exists(f'img/{k}.jpg')]
    print('round', rnd, 'left', len(left), flush=True)
    if not left:
        break
    for k, f in left:
        fu = f.replace(' ', '_')
        h = hashlib.md5(fu.encode()).hexdigest()
        q = urllib.parse.quote(fu)
        w0 = DIM.get(f, 0)
        urls = []
        for w in ([960, 500, 330][rnd % 3:] + [960, 500, 330][:rnd % 3]):
            if w0 == 0 or w < w0:
                urls.append(f'https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{q}/{w}px-{q}' + ('.jpg' if q.lower().endswith(('.png', '.webp', '.tif', '.tiff')) else ''))
        if w0 and w0 <= 1000:
            urls.append(f'https://upload.wikimedia.org/wikipedia/commons/{h[0]}/{h[:2]}/{q}')
        u = urls[0]
        tmp = f'scen/dl/{k}.raw'
        r = subprocess.run(['curl', '-s', '-A', UA, '-o', tmp, '-w', '%{http_code}', u], capture_output=True, text=True).stdout
        if r == '200':
            try:
                im = Image.open(tmp).convert('RGB')
                im.thumbnail((560, 560))
                im.save(f'img/{k}.jpg', quality=76, optimize=True, progressive=True)
                print('OK', k, im.size, flush=True)
            except Exception as e:
                print('bad', k, e, flush=True)
        else:
            print(r, k, u[-60:], flush=True)
        if os.path.exists(tmp):
            os.remove(tmp)
        time.sleep(3)
    time.sleep(20)
print('DONE')
