# 오프라인용 단일 HTML 만들기: 투어 계획 + 운전 가이드북을 한 파일로 합침
#   python3 build_offline.py  →  홋카이도_여행_오프라인.html
# - 사진·지도: WebP로 다시 압축해 파일 안에 넣음(같은 사진은 한 번만 저장, JS로 연결)
# - 글꼴: 문서에 실제로 쓰인 글자만 잘라서 파일 안에 넣음(오프라인에서도 같은 글꼴)
# - 운전 가이드북: 같은 파일 안 전체 화면 창(iframe)으로 열림, 서로 오가는 버튼 연결
import os, re, json, glob, base64, io, html, datetime
from PIL import Image
from fontTools import subset as ftsub
from fontTools.ttLib import TTFont

# 경로: 이 파일 위치 기준(…/오프라인/build_offline.py → 상위 폴더가 ROOT). 환경변수로 바꿀 수 있음
_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get('TRIP_ROOT') or os.path.dirname(_HERE)
TOUR = f'{ROOT}/build/site/hokkaido-trip.html'
GUIDE = f'{ROOT}/운전가이드/site/guide.html'
def _fontdir():
    if os.environ.get('FONTDIR'): return os.environ['FONTDIR']
    for c in (f'{ROOT}/node_modules/@fontsource', f'{_HERE}/node_modules/@fontsource',
              '/tmp/claude-0/-home-claude/c1281e8f-d222-5b04-bc07-5bc379422285/scratchpad/fonts/node_modules/@fontsource'):
        if os.path.isdir(c): return c
    raise SystemExit('글꼴 폴더(@fontsource)를 못 찾음: source 폴더에서 npm ci 먼저 실행하거나 FONTDIR 환경변수 지정')
FONTDIR = _fontdir()
OUT = os.environ.get('OFFLINE_OUT') or f'{ROOT}/오프라인/홋카이도_여행_오프라인.html'
TOUR_URL = 'https://claude.ai/artifact/B8zUF6GHy5b6pZs9e7kakN'
GUIDE_URL = 'https://claude.ai/artifact/3cV9wQR5GUyk5nVJErzLQm'
STAMP = os.environ.get('TRIP_STAMP') or datetime.date.today().isoformat()

tour = open(TOUR, encoding='utf-8').read()
guide = open(GUIDE, encoding='utf-8').read()
assets = json.load(open(f'{ROOT}/build/scen/userphotos/asset_urls.json'))
blob2key = {v: k for k, v in assets.items()}

# ---------- 사진 ----------
IMG = {}          # id -> data URI
def enc(path, q):
    im = Image.open(path); im = im.convert('RGB') if im.mode not in ('RGB',) else im
    if q < 75: im.thumbnail((440, 440), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'WEBP', quality=q, method=6)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
def img_id(path, q):
    k = 'i%d' % len(IMG) if path not in _PATHID else _PATHID[path]
    if path not in _PATHID:
        _PATHID[path] = k; IMG[k] = enc(path, q); SRC[k] = (path, q)
    return k
SRC = {}
_PATHID = {}

def localize(doc, base):
    def rep(m):
        attr, url = m.group(1), m.group(2)
        if url.startswith('/_blob/'):
            p = f'{ROOT}/build/img/{blob2key[url]}.jpg'
        else:
            p = os.path.join(base, url)
        if not os.path.exists(p): return m.group(0)
        q = 80 if "/map/" in p or os.path.basename(os.path.dirname(p)) == "map" else 62
        k = img_id(p, q)
        if attr == 'src': return f'src="" data-oi="{k}"'
        return f'href="#" data-oh="{k}"'
    return re.sub(r'(src|href)="((?:img|map)/[^"]+\.(?:jpg|jpeg|png|webp)|/_blob/[0-9a-f]+)"', rep, doc)

tour = localize(tour, f'{ROOT}/build/site')
guide = localize(guide, f'{ROOT}/운전가이드/site')

# ---------- 서로 오가는 버튼 ----------
tour = re.sub(r'href="' + re.escape(GUIDE_URL) + r'"(\s+target="_blank")?(\s+rel="noopener")?', 'href="#guide"', tour)
guide = re.sub(r'href="' + re.escape(TOUR_URL) + r'"(\s+target="_blank")?(\s+rel="noopener")?', 'href="#back"', guide)

# ---------- 글꼴 ----------
GF = re.compile(r'<link rel="preconnect"[^>]*>\s*|<link rel="stylesheet" href="https://fonts\.googleapis\.com[^"]*">\s*')
tour = GF.sub('', tour); guide = GF.sub('', guide)
used = set(html.unescape(re.sub(r'data:[^"\']+', '', tour + guide))) | set(' 0123456789')
used = {ord(c) for c in used if ord(c) >= 32}
FAM = [('IBM Plex Mono', 'ibm-plex-mono', [500, 600]), ('Noto Sans JP', 'noto-sans-jp', [500, 700]),
       ('Noto Sans KR', 'noto-sans-kr', [400, 500, 700, 900]), ('Noto Serif KR', 'noto-serif-kr', [700, 900]),
       ('Black Han Sans', 'black-han-sans', [400])]
def urange(cps):
    cps = sorted(cps); out = []; s = p = cps[0]
    for c in cps[1:]:
        if c == p + 1: p = c; continue
        out.append((s, p)); s = p = c
    out.append((s, p))
    return ','.join(f'U+{a:X}' if a == b else f'U+{a:X}-{b:X}' for a, b in out)
faces = []; fbytes = 0
# v19.14: 굵기마다 조각 여러 개 → 1개 파일로 합침(요청 수 629 → 11)
from fontTools import merge as ftmerge
import tempfile
_TMP = tempfile.mkdtemp()
for fam, pkg, ws in FAM:
    for w in ws:
        files = sorted(glob.glob(f'{FONTDIR}/{pkg}/files/{pkg}-*-{w}-normal.woff2'))
        done = set(); parts = []
        for f in files:
            cm = set(TTFont(f).getBestCmap().keys())
            want = (cm & used) - done
            if not want: continue
            done |= want
            opts = ftsub.Options(); opts.layout_features = ['*']; opts.notdef_outline = True
            ft = TTFont(f); sb = ftsub.Subsetter(opts); sb.populate(unicodes=want); sb.subset(ft)
            ft.flavor = None; tp = f'{_TMP}/{pkg}-{w}-{len(parts)}.ttf'; ft.save(tp); parts.append(tp)
        if not parts: continue
        try:
            mf = ftmerge.Merger().merge(parts) if len(parts) > 1 else TTFont(parts[0])
        except Exception as e:
            print('merge fail', fam, w, e); mf = TTFont(parts[0])
        # 빌드할 때마다 같은 파일이 나오게(시간 기록 고정) → 글꼴이 안 바뀌면 사용자가 다시 안 받음
        mf.recalcTimestamp = False; mf['head'].created = mf['head'].modified = 3786825600
        b = io.BytesIO(); mf.flavor = 'woff2'; mf.save(b); data = b.getvalue(); fbytes += len(data)
        faces.append(f"@font-face{{font-family:'{fam}';font-style:normal;font-weight:{w};font-display:swap;"
                     f"src:url(data:font/woff2;base64,{base64.b64encode(data).decode()}) format('woff2');unicode-range:{urange(done)}}}")
FONTCSS = '\n'.join(faces)

# ---------- 가이드북: 같은 파일 안 창으로 ----------
GUIDE_BOOT = ('<script>try{var s=parent.document.getElementById("ofonts");if(s)document.write("<style>"+s.textContent+"</style>");}catch(e){}'
              'document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest(\'a[href="#back"]\');'
              'if(a){e.preventDefault();parent.postMessage("hk-back","*");}});'
              # 가이드 안 목차·장 이동 링크는 주소(기록)를 바꾸지 않고 스크롤만 → 뒤로가기 때 빈 화면 방지
              'document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest(\'a[href^="#"]\');if(!a)return;'
              'var h=a.getAttribute("href");if(h==="#back"||h.length<2)return;var el=document.getElementById(decodeURIComponent(h.slice(1)));if(!el)return;'
              'e.preventDefault();setTimeout(function(){el.scrollIntoView({block:"start"});},0);},true);'
              'try{var _ps=history.pushState;history.pushState=function(a,b,u){try{history.replaceState(a,b,u)}catch(e){}};}catch(e){}</script>')
IMG_JS = ('<script>(function(){var M=window.parent&&window.parent!==window&&(function(){try{return parent.__IMG}catch(e){}})()||window.__IMG;'
          'if(!M)return;function fill(r){[].forEach.call(r.querySelectorAll("[data-oi]"),function(i){i.src=M[i.getAttribute("data-oi")];});'
          '[].forEach.call(r.querySelectorAll("[data-oh]"),function(a){a.href=M[a.getAttribute("data-oh")];a.removeAttribute("target");});}'
          'if(document.readyState!=="loading")fill(document);else document.addEventListener("DOMContentLoaded",function(){fill(document);});})();</script>')
HEAD = ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<style>*,*::before,*::after{box-sizing:border-box}html,body{margin:0}</style>')
guide_doc = HEAD + GUIDE_BOOT + '</head><body>' + guide + IMG_JS + '</body></html>'
guide_txt = guide_doc.replace('</script', '<\\/script')

VIEWER = '''
<div id="gview" hidden>
  <div class="gv-bar"><button type="button" id="gvback">← 맛집 투어 계획으로</button><span>일본 렌터카 운전 가이드북</span></div>
  <iframe id="gvframe" title="일본 렌터카 운전 가이드북"></iframe>
</div>
<style>
#gview{position:fixed;inset:0;z-index:1000;background:#fff}
#gview[hidden]{display:none}
.gv-bar{display:flex;align-items:center;gap:12px;padding:8px max(12px,env(safe-area-inset-left)) 8px;background:#1d2733;color:#fff;font:700 14px/1.2 'Noto Sans KR',system-ui,sans-serif}
.gv-bar span{opacity:.8;font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
#gvback{flex:none;font:900 14px/1 'Noto Sans KR',system-ui,sans-serif;color:#1d2733;background:#fff;border:0;border-radius:999px;padding:9px 14px;cursor:pointer}
#gvframe{position:absolute;left:0;right:0;bottom:0;top:52px;width:100%;height:calc(100% - 52px);border:0;display:block}
.gv-bar{height:52px;box-sizing:border-box}
.offnote{margin:0 0 10px;display:inline-block;font:700 12px/1.5 'Noto Sans KR',system-ui,sans-serif;color:#6b5b00;background:#fff6c7;border:1px solid #e9d670;border-radius:8px;padding:4px 10px}
</style>
<script type="text/plain" id="guidesrc">''' + guide_txt + '''</script>
<script>
(function(){
  var v=document.getElementById('gview'), f=document.getElementById('gvframe'), y=0;
  if(f) f.remove(); f=null;
  // 열 때마다 새 창(iframe)을 만들고 닫을 때 없앰 → 아이폰에서 다시 열면 빈 화면 되던 문제 방지
  function open(){ if(!v.hidden&&f) return; y=window.scrollY;
    f=document.createElement('iframe'); f.id='gvframe'; f.title='일본 렌터카 운전 가이드북';
    v.appendChild(f); f.srcdoc=document.getElementById('guidesrc').textContent.replace(/<\\\\\\/script/g,'</script');
    v.hidden=false; document.documentElement.style.overflow='hidden'; }
  function close(){ v.hidden=true; if(f){ f.remove(); f=null; } document.documentElement.style.overflow=''; window.scrollTo(0,y); }
  function sync(){ if(location.hash==='#guide') open(); else if(!v.hidden) close(); }
  window.addEventListener('hashchange',sync);
  function goBack(){ if(location.hash==='#guide'){ history.back(); setTimeout(function(){ if(!v.hidden){ try{history.replaceState(null,'',location.pathname+location.search);}catch(e){} close(); } },400); } else close(); }
  document.getElementById('gvback').addEventListener('click',goBack);
  window.addEventListener('popstate',sync);
  window.addEventListener('pageshow',function(){ sync(); if(v.hidden) document.documentElement.style.overflow=''; });
  window.addEventListener('message',function(e){ if(e.data==='hk-back') goBack(); });
  if(location.hash==='#guide') open();
})();
</script>'''

tour = re.sub(r'(<h1[^>]*>)', '<p class="offnote">오프라인용 파일 · ' + STAMP + ' 기준 · 구글맵·타베로그 링크는 인터넷 될 때만 열림</p>\\1', tour, count=1)
page = (HEAD + f'<style id="ofonts">{FONTCSS}</style>' + '<script>window.__IMG=' + json.dumps(IMG) + ';</script></head><body>'
        + tour + VIEWER + IMG_JS + '</body></html>')
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'w', encoding='utf-8').write(page)
print('images', len(IMG), 'fonts', len(faces), round(fbytes / 1e6, 2), 'MB', 'total', round(os.path.getsize(OUT) / 1e6, 1), 'MB')

# ---------- 공개 주소용(PWA): 홈 화면에 추가하면 오프라인 + 온라인일 때 자동 최신판 ----------
import shutil, hashlib
PWA = os.environ.get('PWA_OUT') or f'{ROOT}/오프라인/pwa'
os.makedirs(PWA, exist_ok=True)
VER = hashlib.sha1(page.encode()).hexdigest()[:10]
pwa_head = ('<link rel="manifest" href="manifest.webmanifest"><meta name="theme-color" content="#0f5e63">'
            '<meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-title" content="홋카이도 여행">'
            '<link rel="apple-touch-icon" href="icon-192.png"><link rel="icon" href="icon-192.png">'
            '<title>홋카이도 맛집 투어 계획</title>')
pwa_note = ('<div class="pwanote"><b>인터넷 없이 보려면 (한 번만 하면 됨)</b>'
            '<ol><li><b>아이폰:</b> 카톡에서 열었으면 오른쪽 아래 <b>공유 버튼</b> → <b>다른 브라우저로 열기</b>(사파리). '
            '사파리에서 <b>공유 버튼</b>(네모에 ↑) → <b>더 보기(⌄)</b> → <b>홈 화면에 추가</b>. 안 보이면 그 목록을 아래로 내려서 찾으면 됨.</li>'
            '<li><b>안드로이드:</b> 카톡에서 열었으면 메뉴(⋮) → <b>다른 브라우저로 열기</b>(크롬) → 크롬 메뉴(⋮) → <b>홈 화면에 추가</b>.</li></ol>'
            '그다음부터 홈 화면 아이콘으로 열면 인터넷 없어도 다 보임. 인터넷 될 때 열면 최신판으로 자동으로 바뀜.'
            '<span class="pwaver">판 ' + STAMP + '</span></div>')
pwa_css = ('<style>.pwanote{margin:0 0 12px;font:500 13px/1.6 "Noto Sans KR",system-ui,sans-serif;color:#0b3e42;background:#e3f4f2;border:1px solid #9fd3cd;border-radius:10px;padding:10px 12px}'
           '.pwanote b{font-weight:700}.pwanote ol{margin:6px 0 6px;padding-left:18px;display:grid;gap:4px}.pwaver{display:block;margin-top:4px;font-size:11.5px;opacity:.7}'
           '.updbar{position:fixed;left:50%;top:10px;transform:translateX(-50%);z-index:2000;background:#0f5e63;color:#fff;font:700 13px/1.4 "Noto Sans KR",system-ui,sans-serif;padding:9px 14px;border-radius:999px;box-shadow:0 4px 14px rgba(0,0,0,.25)}'
           'html.standalone .pwanote{display:none}</style>')
pwa_js = ('<script>(function(){if(matchMedia("(display-mode: standalone)").matches||navigator.standalone)document.documentElement.classList.add("standalone");'
          'if(!("serviceWorker" in navigator)||!/^https?:/.test(location.protocol))return;'
          'var had=!!navigator.serviceWorker.controller;'
          'navigator.serviceWorker.register("sw.js").catch(function(){});'
          'navigator.serviceWorker.addEventListener("message",function(e){if(e.data&&e.data.type==="updated"&&had){'
          'var d=document.createElement("div");d.className="updbar";d.textContent="새 버전 있음 · 눌러서 최신판 보기";d.onclick=function(){location.reload();};document.body.appendChild(d);}});'
          '})();</script>')
# v19.13 가볍게 + 다운로드/업데이트 화면
# - 사진·글꼴은 따로 떼어 냄(첫 화면은 글만). 처음 열면 화면 가운데 "다운받는 중 N%"로 사진을 전부 받아 휴대폰에 저장(16개씩 동시)
# - 그다음부터는 저장된 판을 바로 보여 줌(온라인이어도 다시 안 받음). 새 판이 올라오면 화면 가운데 "업데이트됨 · 업데이트하기"
for d in ('i', 'f'):
    if os.path.isdir(f'{PWA}/{d}'): shutil.rmtree(f'{PWA}/{d}')
    os.makedirs(f'{PWA}/{d}')
IMGPATH = {}
for k, uri in IMG.items():
    data = base64.b64decode(uri.split(',', 1)[1]); h = hashlib.sha1(data).hexdigest()[:12]
    IMGPATH[k] = f'i/{h}.webp'; open(f'{PWA}/{IMGPATH[k]}', 'wb').write(data)
FONTFILES = []
def _font(m):
    data = base64.b64decode(m.group(1)); h = hashlib.sha1(data).hexdigest()[:12]
    p = f'f/{h}.woff2'; open(f'{PWA}/{p}', 'wb').write(data); FONTFILES.append(p)
    return f'url({p})'
FONTCSS_L = re.sub(r'url\(data:font/woff2;base64,([A-Za-z0-9+/=]+)\)', _font, FONTCSS)
def light(doc):
    doc = re.sub(r'src="" data-oi="(i\d+)"', lambda m: f'src="{IMGPATH[m.group(1)]}"', doc)
    doc = re.sub(r'href="#" data-oh="(i\d+)"', lambda m: f'href="{IMGPATH[m.group(1)]}"', doc)
    doc = re.sub(r'<img (?![^>]*loading=)', '<img loading="lazy" ', doc)
    return doc
guide_doc_l = HEAD + GUIDE_BOOT + '</head><body>' + light(guide) + '</body></html>'
VIEWER_L = VIEWER.replace(guide_txt, guide_doc_l.replace('</script', '<\\/script'))
tour_l = re.sub(r'<p class="offnote">.*?</p>', pwa_note, light(tour), count=1).replace('href="#guide"', 'href="guide.html"')
ASSETS = sorted(set(IMGPATH.values()))
# v19.14 위쪽(1일차)부터 받는 순서 · AVIF(더 작음) · 묶음 8개로 합쳐 요청 수 줄이기
ORDER = list(dict.fromkeys(re.findall(r'i/[0-9a-f]{12}\.webp', tour_l + guide_doc_l)))
ORDER += [a for a in ASSETS if a not in ORDER]
WEBP = {a: open(f'{PWA}/{a}', 'rb').read() for a in ORDER}
AVIF = {}
for k, (path, q) in SRC.items():
    a = IMGPATH[k]
    if a in AVIF: continue
    im = Image.open(path); im = im.convert('RGB') if im.mode != 'RGB' else im
    if q < 75: im.thumbnail((440, 440), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'AVIF', quality=(60 if q >= 75 else 50), speed=6); AVIF[a] = b.getvalue()
if os.path.isdir(f'{PWA}/p'): shutil.rmtree(f'{PWA}/p')
os.makedirs(f'{PWA}/p')
def make_packs(src, tag, n=8):
    tot = sum(len(src[a]) for a in ORDER); per = tot / n; packs = []; cur = []; size = 0
    for a in ORDER:
        cur.append(a); size += len(src[a])
        if size >= per and len(packs) < n - 1: packs.append(cur); cur = []; size = 0
    if cur: packs.append(cur)
    out = []
    for grp in packs:
        blob = b''.join(src[a] for a in grp); h = hashlib.sha1(blob).hexdigest()[:12]
        u = f'p/{tag}{h}.bin'; open(f'{PWA}/{u}', 'wb').write(blob)
        it = []; off = 0
        for a in grp: it.append([a, off, len(src[a])]); off += len(src[a])
        out.append({'u': u, 'n': len(blob), 'it': it})
    return out
PACKS = {'webp': make_packs(WEBP, 'w'), 'avif': make_packs(AVIF, 'a')}
_t = Image.new('RGB', (2, 2), 'white'); _b = io.BytesIO(); _t.save(_b, 'AVIF', quality=30)
AVIF_TEST = 'data:image/avif;base64,' + base64.b64encode(_b.getvalue()).decode()
print('packs webp', round(sum(p['n'] for p in PACKS['webp'])/1e6,1), 'MB / avif', round(sum(p['n'] for p in PACKS['avif'])/1e6,1), 'MB')
VER = hashlib.sha1((tour_l + guide_doc_l + FONTCSS_L + json.dumps(PACKS)).encode()).hexdigest()[:10]
DL = """
<div id="dlv" hidden><div class="dlc">
  <p class="dlt" id="dlt">다운받는 중</p><p class="dlp" id="dlp">0%</p>
  <div class="dlb"><i id="dlbar"></i></div>
  <p class="dls" id="dls">처음 한 번만 · 인터넷 없어도 보이게 사진을 휴대폰에 저장하는 중</p>
  <div class="dlbtns" id="dlbtns" hidden></div>
</div></div>
<style>
#dlv{position:fixed;inset:0;z-index:3000;display:grid;place-items:center;background:rgba(10,16,22,.55);-webkit-backdrop-filter:blur(5px);backdrop-filter:blur(5px);padding:24px}
#dlv[hidden]{display:none}
.dlc{width:min(320px,100%);background:#fff;color:#16202a;border-radius:18px;padding:22px 22px 18px;text-align:center;box-shadow:0 18px 50px rgba(0,0,0,.35);font-family:"Noto Sans KR",system-ui,sans-serif}
.dlt{margin:0;font-weight:900;font-size:18px}
.dlp{margin:6px 0 10px;font:900 40px/1 "IBM Plex Mono",ui-monospace,monospace;color:#0f5e63}
.dlb{height:10px;border-radius:999px;background:#e3ecea;overflow:hidden}
.dlb i{display:block;height:100%;width:0;background:linear-gradient(90deg,#0f5e63,#2aa198);border-radius:999px;transition:width .25s ease}
.dls{margin:10px 0 0;font-size:12.5px;line-height:1.5;color:#5b6670}
.dlbtns{display:flex;gap:8px;justify-content:center;margin-top:14px}
.dlbtns button{font:800 15px/1 "Noto Sans KR",system-ui,sans-serif;border:0;border-radius:999px;padding:12px 20px;cursor:pointer}
.dlbtns .go{background:#e8590c;color:#fff}.dlbtns .later{background:#eef1f3;color:#4a5560}
html.dlopen,html.dlopen body{overflow:hidden}
#netmode{position:fixed;right:max(14px,env(safe-area-inset-right,0px));bottom:calc(max(6px,env(safe-area-inset-bottom,0px)));z-index:31;font:800 11.5px/1 "Noto Sans KR",system-ui,sans-serif;letter-spacing:.02em;padding:3px 8px;border-radius:999px;background:rgba(255,255,255,.85);color:#1f7a4d;box-shadow:0 1px 4px rgba(0,0,0,.15);pointer-events:none}
#netmode.off{color:#b4400a}
#netmode::before{content:"● ";font-size:9px;vertical-align:1px}
@media (prefers-color-scheme:dark){#netmode{background:rgba(20,26,32,.85);color:#5fd39a}#netmode.off{color:#ff9a5c}}
.tocbtn{bottom:calc(max(16px,env(safe-area-inset-bottom,0px)) + 18px)!important}
.tocpanel{bottom:calc(max(16px,env(safe-area-inset-bottom,0px)) + 80px)!important}
</style>
<div id="netmode" aria-live="polite"></div>
<script>(function(){
var NM=document.getElementById("netmode");function nm(){var on=navigator.onLine;NM.textContent=on?"온라인 모드":"오프라인 모드";NM.classList.toggle("off",!on);}
nm();window.addEventListener("online",nm);window.addEventListener("offline",nm);
if(!("serviceWorker" in navigator)||!/^https?:/.test(location.protocol))return;
if(matchMedia("(display-mode: standalone)").matches||navigator.standalone)document.documentElement.classList.add("standalone");
var V=document.getElementById("dlv"),T=document.getElementById("dlt"),P=document.getElementById("dlp"),B=document.getElementById("dlbar"),S=document.getElementById("dls"),BT=document.getElementById("dlbtns");
var mode=null,stall=null,FMT=null;function fmt(cb){if(FMT)return cb(FMT);var t=new Image();t.onload=function(){FMT=(t.width>0)?"avif":"webp";cb(FMT);};t.onerror=function(){FMT="webp";cb(FMT);};t.src=__AVIF_TEST__;}
function open(){V.hidden=false;document.documentElement.classList.add("dlopen");}
function close(){V.hidden=true;document.documentElement.classList.remove("dlopen");}
function prog(t,sub){mode="dl";BT.hidden=true;T.textContent=t;S.textContent=sub;open();}
function pct(d,t){var p=t?Math.floor(d*100/t):0;P.textContent=p+"%";B.style.width=p+"%";clearTimeout(stall);
  stall=setTimeout(function(){if(mode==="dl"){S.textContent="인터넷이 느리거나 끊긴 것 같음 · 연결되면 이어서 받음";btns([["나중에 받기","later",close]]);}},20000);}
function btns(list){BT.innerHTML="";list.forEach(function(x){var b=document.createElement("button");b.type="button";b.textContent=x[0];b.className=x[1];b.onclick=x[2];BT.appendChild(b);});BT.hidden=false;}
function finish(msg,reload){clearTimeout(stall);P.textContent="100%";B.style.width="100%";T.textContent=msg;S.textContent=reload?"새 판으로 바뀌는 중":"이제 인터넷 없어도 다 보임";BT.hidden=true;
  setTimeout(function(){if(reload)location.reload();else close();mode=null;},reload?600:1200);}
var updating=false;
navigator.serviceWorker.addEventListener("message",function(e){var d=e.data||{};
  if(d.type==="progress"){ if(d.total&&d.done<d.total&&navigator.onLine){ if(mode!=="dl")prog(updating?"업데이트 중":"다운받는 중",updating?"새 내용 받는 중 · 잠깐만 기다리면 됨":"처음 한 번만 · 인터넷 없어도 보이게 사진을 휴대폰에 저장하는 중"); pct(d.done,d.total);} }
  if(d.type==="ready"){ if(mode==="dl"||updating)finish(updating?"업데이트 완료 ✓":"준비 완료 ✓",updating); }
});
function askUpdate(w){mode="ask";T.textContent="업데이트됨";P.textContent="NEW";B.style.width="100%";S.textContent="새 내용이 올라왔음 · 눌러서 받으면 됨";
  btns([["업데이트하기","go",function(){updating=true;prog("업데이트 중","새 내용 받는 중 · 잠깐만 기다리면 됨");pct(0,1);w.postMessage("skip");}],["나중에","later",function(){close();mode=null;}]]);open();}
navigator.serviceWorker.register("sw.js").then(function(r){
  function watch(w){w.addEventListener("statechange",function(){if(w.state==="installed"&&navigator.serviceWorker.controller)askUpdate(w);});}
  if(r.waiting&&navigator.serviceWorker.controller)askUpdate(r.waiting);
  r.addEventListener("updatefound",function(){if(r.installing)watch(r.installing);});
  navigator.serviceWorker.ready.then(function(rr){var w=navigator.serviceWorker.controller||rr.active;if(w)fmt(function(f){w.postMessage({cmd:"status",fmt:f});});});
  if(navigator.onLine)setTimeout(function(){r.update().catch(function(){});},1500);
}).catch(function(){});
navigator.serviceWorker.addEventListener("controllerchange",function(){var c=navigator.serviceWorker.controller;if(c)fmt(function(f){c.postMessage({cmd:"status",fmt:f});});});
})();</script>"""
DL = DL.replace('__AVIF_TEST__', json.dumps(AVIF_TEST))
pp = (HEAD + f'<style id="ofonts">{FONTCSS_L}</style>' + pwa_head + pwa_css + '</head><body>' + tour_l + DL + '</body></html>')
# v19.15 운전 가이드북은 별도 페이지(guide.html) — 돌아가기는 브라우저 뒤로(보던 자리 그대로), 처음 연 경우엔 투어 첫 화면으로
GBACK = """<script>document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest('a[href^="#"]');if(!a)return;var h=a.getAttribute("href");if(h==="#back"||h.length<2)return;var el=document.getElementById(decodeURIComponent(h.slice(1)));if(!el)return;e.preventDefault();setTimeout(function(){el.scrollIntoView({block:"start"});},0);},true);
document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest('a[href="#back"]');if(!a)return;e.preventDefault();
try{if(document.referrer&&new URL(document.referrer).origin===location.origin&&history.length>1){history.back();return;}}catch(_){}location.href="./";});</script>"""
NETMODE = DL[DL.index('#netmode{'):DL.index('.tocbtn{bottom')] 
gp = (HEAD + f'<style id="ofonts">{FONTCSS_L}</style>' + pwa_head.replace('<title>홋카이도 맛집 투어 계획</title>', '<title>일본 렌터카 운전 가이드북</title>')
      + '<style>' + NETMODE + '.tocbtn{bottom:calc(34px + env(safe-area-inset-bottom,0px))!important}.tocpop{bottom:calc(82px + env(safe-area-inset-bottom,0px))!important}</style></head><body>' + light(guide) + GBACK
      + '<div id="netmode"></div><script>(function(){var N=document.getElementById("netmode");function f(){var on=navigator.onLine;N.textContent=on?"온라인 모드":"오프라인 모드";N.classList.toggle("off",!on);}f();addEventListener("online",f);addEventListener("offline",f);'
      + 'if("serviceWorker" in navigator&&/^https?:/.test(location.protocol))navigator.serviceWorker.register("sw.js").catch(function(){});})();</script></body></html>')
open(f'{PWA}/guide.html', 'w', encoding='utf-8').write(gp)
open(f'{PWA}/index.html', 'w', encoding='utf-8').write(pp)
CORE = ['./', 'index.html', 'guide.html', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png'] + FONTFILES
open(f'{PWA}/sw.js', 'w', encoding='utf-8').write("""// 버전 """ + VER + """
const C='hk-""" + VER + """';
const CORE=""" + json.dumps(CORE) + """;
const PACKS=""" + json.dumps(PACKS) + """;
const ALL=PACKS.webp.flatMap(p=>p.it.map(x=>x[0]));
// 설치: 글·글꼴만(작음). 이미 쓰던 판이 있으면 "업데이트하기"를 눌러야 바뀜
self.addEventListener('install',e=>{e.waitUntil((async()=>{const c=await caches.open(C);
  await Promise.all(CORE.map(async a=>{const old=a.startsWith('f/')?await caches.match(a):null;if(old){await c.put(a,old);return;}const r=await fetch(a,{cache:'no-store'});if(!r.ok)throw new Error(a);await c.put(a,r);}));
  if(!self.registration.active)self.skipWaiting();})());});
self.addEventListener('message',e=>{const d=e.data;if(d==='skip')self.skipWaiting();if(d==='status')ensureAll('webp');if(d&&d.cmd==='status')ensureAll(d.fmt);});
self.addEventListener('activate',e=>{e.waitUntil(self.clients.claim());});
let running=null;
async function tell(m){(await self.clients.matchAll({includeUncontrolled:true})).forEach(cl=>cl.postMessage(m));}
const key=u=>new URL(u,self.location).pathname.split('/').slice(-2).join('/');
// 사진 묶음(8개)을 동시에 받아서 휴대폰 안에서 사진 한 장씩 나눠 저장 · 진행률은 받은 용량 기준
function ensureAll(fmt){if(running)return running;running=(async()=>{const c=await caches.open(C);
  const have=new Set((await c.keys()).map(r=>key(r.url)));
  const P=PACKS[fmt]||PACKS.webp;const ty=(fmt==='avif'&&PACKS.avif)?'image/avif':'image/webp';
  const todo=P.filter(p=>p.it.some(x=>!have.has(x[0])));
  const total=P.reduce((s,p)=>s+p.n,0);let got=total-todo.reduce((s,p)=>s+p.n,0);let last=0;
  if(todo.length)await tell({type:'progress',done:got,total});
  await Promise.all(todo.map(async p=>{let mine=0;
    try{const r=await fetch(p.u);if(!r.ok)throw 0;let buf;
      if(r.body&&r.body.getReader){const rd=r.body.getReader();const ch=[];
        for(;;){const {done,value}=await rd.read();if(done)break;ch.push(value);mine+=value.length;got+=value.length;const now=Date.now();if(now-last>150){last=now;tell({type:'progress',done:Math.min(got,total-1),total});}}
        buf=new Blob(ch);}
      else{buf=await r.blob();got+=buf.size;mine=buf.size;}
      await Promise.all(p.it.filter(x=>!have.has(x[0])).map(x=>c.put(x[0],new Response(buf.slice(x[1],x[1]+x[2],ty),{headers:{'content-type':ty}}))));
    }catch(e){got-=mine;
      for(const x of p.it){if(have.has(x[0]))continue;try{const r=await fetch(x[0]);if(r.ok)await c.put(x[0],r);}catch(_){}}
      got+=p.n;tell({type:'progress',done:Math.min(got,total-1),total});}
  }));
  const have2=new Set((await c.keys()).map(r=>key(r.url)));const left=ALL.filter(a=>!have2.has(a)).length;
  if(left===0){for(const k of await caches.keys())if(k!==C)await caches.delete(k);await tell({type:'ready'});}
  else await tell({type:'progress',done:total-1,total});
  running=null;})();return running;}
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(u.origin!==location.origin)return;
  if(e.request.mode==='navigate'||u.pathname.endsWith('/index.html')||u.pathname.endsWith('/guide.html')){
    const pg=u.pathname.endsWith('/guide.html')?'guide.html':'index.html';e.respondWith(caches.open(C).then(c=>c.match(pg)).then(r=>r||fetch(e.request)));return;}
  e.respondWith(caches.match(e.request,{ignoreSearch:true}).then(r=>r||fetch(e.request)));
});
""")
json.dump({'name': '홋카이도 맛집 투어 계획 + 운전 가이드', 'short_name': '홋카이도 여행', 'start_url': './', 'scope': './', 'display': 'standalone',
           'background_color': '#f2f4f3', 'theme_color': '#0f5e63', 'lang': 'ko',
           'icons': [{'src': 'icon-192.png', 'sizes': '192x192', 'type': 'image/png'}, {'src': 'icon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any maskable'}]},
          open(f'{PWA}/manifest.webmanifest', 'w', encoding='utf-8'), ensure_ascii=False)
# 아이콘
from PIL import ImageDraw, ImageFont
kr = sorted(glob.glob(f'{FONTDIR}/noto-sans-kr/files/noto-sans-kr-*-900-normal.woff2'))
ttf = None
for f in kr:
    t = TTFont(f)
    if ord('홋') in t.getBestCmap(): t.flavor = None; ttf = os.path.join(_TMP, '_icon.ttf'); t.save(ttf); break
for n in (192, 512):
    im = Image.new('RGB', (n, n), '#0f5e63'); d = ImageDraw.Draw(im)
    fnt = ImageFont.truetype(ttf, int(n * .52)) if ttf else ImageFont.load_default()
    d.text((n / 2, n * .47), '홋', font=fnt, fill='white', anchor='mm')
    d.rounded_rectangle((n * .2, n * .78, n * .8, n * .84), radius=n * .03, fill='#f5c542')
    im.save(f'{PWA}/icon-{n}.png')
open(f'{PWA}/.nojekyll', 'w').write('')
print('pwa', VER, len(FONTFILES),'fontfiles', round(os.path.getsize(f'{PWA}/index.html') / 1e6, 2), 'MB html', len(ASSETS), 'imgs', len(FONTFILES), 'fonts', round(sum(os.path.getsize(f'{PWA}/'+x) for x in ASSETS)/1e6,1), 'MB imgs', round(sum(os.path.getsize(f'{PWA}/'+x) for x in FONTFILES)/1e6,1),'MB fonts')
