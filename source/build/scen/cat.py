import subprocess, re, json, time, urllib.parse, sys, html, os
UA = 'HokkaidoTripPlanner/1.0 (personal itinerary)'
OUT = 'scen/cats_new.json'
SKIP = ('Uses_of', 'Pages_', 'CC-', 'Files_', 'Hidden', 'Uploaded', 'Media_', 'Self-published', 'License', 'Taken_with', 'Photographs_by', 'Images_from')
db = {}
if os.path.exists(OUT):
    db = json.load(open(OUT))
for c in sys.argv[1:]:
    url = 'https://commons.wikimedia.org/wiki/Category:' + urllib.parse.quote(c.replace(' ', '_'))
    for attempt in range(3):
        r = subprocess.run(['curl', '-s', '-A', UA, '-w', '\n__CODE__%{http_code}', url], capture_output=True, text=True).stdout
        code = r.rsplit('__CODE__', 1)[-1].strip()
        if code != '429':
            break
        print('429, waiting', flush=True)
        time.sleep(15 + 10 * attempt)
    if code == '429':
        continue
    s = r.rsplit('__CODE__', 1)[0]
    files = []
    for box in s.split('class="gallerybox"')[1:]:
        m = re.search(r'href="/wiki/File:([^"]+)"', box)
        if not m:
            continue
        f = html.unescape(urllib.parse.unquote(m.group(1)))
        t = re.search(r'<img[^>]+src="([^"]+)"', box)
        d = re.search(r'([\d,]+) × ([\d,]+)', box)
        w, h = (int(d.group(1).replace(',', '')), int(d.group(2).replace(',', ''))) if d else (0, 0)
        files.append([f, w, h, html.unescape(t.group(1)) if t else ''])
    sub = ''
    i = s.find('id="mw-subcategories"')
    if i >= 0:
        j = s.find('id="mw-pages"', i)
        k = s.find('id="mw-category-media"', i)
        ends = [x for x in (j, k) if x > 0]
        sub = s[i:min(ends) if ends else i + 40000]
    subs = sorted(set(urllib.parse.unquote(x) for x in re.findall(r'href="/wiki/Category:([^"#?]+)"', sub)))
    pi = s.find('id="catlinks"')
    parents = sorted(set(urllib.parse.unquote(x) for x in re.findall(r'href="/wiki/Category:([^"#?]+)"', s[pi:]))) if pi >= 0 else []
    parents = [p for p in parents if not p.startswith(SKIP)]
    db[c] = {'code': code, 'files': files, 'subs': subs, 'parents': parents}
    print(c, code, 'files', len(files), 'subs', subs[:20], flush=True)
    json.dump(db, open(OUT, 'w'), ensure_ascii=False, indent=0)
    time.sleep(3)
