# reads scen/picks.json [[card, imgkey, file, caption], ...]; writes scen/meta_raw.json (all) with license/author/date
import json, re, html, subprocess, time, urllib.parse, os
UA = 'HokkaidoTripPlanner/1.0 (personal itinerary)'
picks = json.load(open('scen/picks.json'))
RAW = 'scen/meta_raw.json'
raw = json.load(open(RAW)) if os.path.exists(RAW) else {}


def cell(s, key):
    x = re.search(r'fileinfotpl(?:_|&#95;)' + key + r'".*?</td>\s*<td[^>]*>(.*?)</td>', s, re.S)
    if not x:
        return None
    t = re.sub(r'<style.*?</style>', '', x.group(1), flags=re.S)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t))).strip()


for card, k, f, cap in picks:
    if f in raw and raw[f].get('license'):
        continue
    page = 'https://commons.wikimedia.org/wiki/File:' + urllib.parse.quote(f.replace(' ', '_'))
    for att in range(4):
        r = subprocess.run(['curl', '-s', '-A', UA, '-w', '\n__CODE__%{http_code}', page], capture_output=True, text=True).stdout
        s, code = r.rsplit('__CODE__', 1)
        code = code.strip()
        if code != '429':
            break
        print('429 wait', flush=True)
        time.sleep(20 + 15 * att)
    if code != '200':
        print('ERR', code, k, f, flush=True)
        raw[f] = {'code': code}
        json.dump(raw, open(RAW, 'w'), ensure_ascii=False, indent=1)
        time.sleep(3)
        continue
    lic = re.search(r'"license":"([^"]+)"', s)
    lic = lic.group(1).replace('\\/', '/') if lic else None
    lic_names = sorted(set(re.findall(r'class="licensetpl_short"[^>]*>([^<]+)<', s)))
    au = cell(s, 'aut')
    date = cell(s, 'date')
    desc = cell(s, 'desc')
    dims = re.search(r'([\d,]+) × ([\d,]+) pixels', s)
    raw[f] = {'code': code, 'page': page, 'license': lic, 'licnames': lic_names,
              'author': au, 'date': (date or '')[:60], 'desc': (desc or '')[:200],
              'dims': [int(dims.group(1).replace(',', '')), int(dims.group(2).replace(',', ''))] if dims else None}
    json.dump(raw, open(RAW, 'w'), ensure_ascii=False, indent=1)
    print(k, lic, lic_names, (au or '')[:50], (date or '')[:25], flush=True)
    time.sleep(2.5)
print('DONE')
