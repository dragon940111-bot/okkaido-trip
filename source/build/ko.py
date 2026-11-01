# Japanese -> Korean reading annotation: "日本語(한국어)"
import re, unicodedata
import pykakasi
_kks = pykakasi.kakasi()

V = {'a': 0, 'ya': 2, 'eo': 4, 'e': 5, 'yeo': 6, 'o': 8, 'yo': 12, 'u': 13, 'yu': 17, 'eu': 18, 'i': 20, 'wa': 9, 'wi': 16, 'we': 15, 'wo': 14, 'ye': 7}
C = {'g': 0, 'kk': 1, 'n': 2, 'd': 3, 'r': 5, 'm': 6, 'b': 7, 's': 9, 'ss': 10, '': 11, 'j': 12, 'ch': 14, 'k': 15, 't': 16, 'p': 17, 'h': 18}
def syl(c, v): return chr(0xAC00 + (C[c] * 21 + V[v]) * 28)

# kana -> (initial-consonant, medial-consonant, vowel)
K = {}
def add(kana, ci, cm, v): K[kana] = (ci, cm, v)
for k, v in zip('あいうえお', ['a', 'i', 'u', 'e', 'o']): add(k, '', '', v)
for row, ci, cm in [('かきくけこ', 'g', 'k'), ('がぎぐげご', 'g', 'g'), ('さしすせそ', 's', 's'), ('ざじずぜぞ', 'j', 'j'),
                    ('たちつてと', 'd', 't'), ('だぢづでど', 'd', 'd'), ('なにぬねの', 'n', 'n'), ('はひふへほ', 'h', 'h'),
                    ('ばびぶべぼ', 'b', 'b'), ('ぱぴぷぺぽ', 'p', 'p'), ('まみむめも', 'm', 'm'), ('らりるれろ', 'r', 'r')]:
    for k, v in zip(row, ['a', 'i', 'u', 'e', 'o']): add(k, ci, cm, v)
add('す', 's', 's', 'eu'); add('ず', 'j', 'j', 'eu'); add('づ', 'j', 'j', 'eu')
add('ち', 'j', 'ch', 'i'); add('ぢ', 'j', 'j', 'i'); add('つ', 'ss', 'ss', 'eu')
for k, v in zip('やゆよ', ['ya', 'yu', 'yo']): add(k, '', '', v)
add('わ', '', '', 'wa'); add('を', '', '', 'o')
YO = {'ゃ': 'ya', 'ゅ': 'yu', 'ょ': 'yo'}
PAL = {'き': ('g', 'k'), 'ぎ': ('g', 'g'), 'に': ('n', 'n'), 'ひ': ('h', 'h'), 'び': ('b', 'b'), 'ぴ': ('p', 'p'), 'み': ('m', 'm'), 'り': ('r', 'r'),
       'し': ('s', 's'), 'じ': ('j', 'j'), 'ち': ('j', 'ch'), 'ぢ': ('j', 'j')}
SMALLV = {'ぁ': 'a', 'ぃ': 'i', 'ぅ': 'u', 'ぇ': 'e', 'ぉ': 'o'}

def kata2hira(s): return ''.join(chr(ord(c) - 0x60) if 'ァ' <= c <= 'ヶ' else c for c in s)

def kana2hangul(h):
    h = kata2hira(h).replace('ゔ', 'ぶ')
    out = []; i = 0; first = True; prev_v = None
    while i < len(h):
        c = h[i]; nx = h[i + 1] if i + 1 < len(h) else ''
        if c in 'ーｰ': i += 1; continue
        if c == 'っ':
            if out and (ord(out[-1]) - 0xAC00) % 28 == 0 and 0xAC00 <= ord(out[-1]) <= 0xD7A3: out[-1] = chr(ord(out[-1]) + 19)
            i += 1; continue
        if c == 'ん':
            if out and (ord(out[-1]) - 0xAC00) % 28 == 0 and 0xAC00 <= ord(out[-1]) <= 0xD7A3: out[-1] = chr(ord(out[-1]) + 4)
            else: out.append('응')
            i += 1; continue
        if c == 'う' and prev_v in ('o', 'u', 'yo', 'yu'):  # long vowel
            i += 1; prev_v = None; continue
        if c in PAL and nx in YO:
            ci, cm = PAL[c]; v = YO[nx]
            cons = ci if first else cm
            if cons in ('s', 'j', 'ch'): v = {'ya': 'a', 'yu': 'u', 'yo': 'o'}[v] if cons != 's' else {'ya': 'ya', 'yu': 'yu', 'yo': 'yo'}[v]
            out.append(syl(cons, v)); prev_v = YO[nx]; i += 2; first = False; continue
        if c in ('ふ', 'て', 'で', 'う', 'し', 'じ', 'ち') and nx in SMALLV:
            sv = SMALLV[nx]
            m = {'ふ': ('p', sv), 'て': ('t', sv), 'で': ('d', sv), 'う': ('', {'i': 'wi', 'e': 'we', 'o': 'wo', 'a': 'wa'}.get(sv, sv)),
                 'し': ('s', 'ye' if sv == 'e' else sv), 'じ': ('j', sv), 'ち': ('ch', sv)}[c]
            out.append(syl(m[0], m[1])); prev_v = sv; i += 2; first = False; continue
        if c in K:
            ci, cm, v = K[c]
            out.append(syl(ci if first else cm, v)); prev_v = v; i += 1; first = False; continue
        if c in SMALLV: out.append(syl('', SMALLV[c])); i += 1; continue
        if c in YO: out.append(syl('', YO[c])); i += 1; continue
        out.append(c); i += 1
        if c == ' ': first = True
    return ''.join(out)

def reading(jp):
    parts = []
    for x in _kks.convert(jp):
        o = x['orig']; hira = x['hira']
        if re.search(r'[぀-ヿ㐀-鿿]', o): parts.append(kana2hangul(hira.replace('々', '')))
        else: parts.append(o)
    return ''.join(parts)

JPC = r'぀-ヿ㐀-鿿豈-﫿々〆ー'
RUN = rf'[{JPC}]+(?:[0-9０-９A-Za-z]+[{JPC}]+)*'
PHRASE = rf'{RUN}(?: {RUN})*'
HANGUL = re.compile(r'[가-힣]')

SINGLE_BAD = set('寿雲月花港鹿熊松竹梅華翁梵')
SUFFIX = set(['店','駅','湖','岬','山','川','丼','線','条','町','本店','支店','市場','食堂','温泉','空港'])
class Annotator:
    def __init__(self, d):
        self.d = dict(d)
        keys = sorted(self.d, key=len, reverse=True)
        self.seg = [k for k in keys if (len(k) >= 2 or k not in SINGLE_BAD) and re.fullmatch(rf'[{JPC}0-9A-Za-z・]+', k)]
        self.rx = re.compile('((?<![' + JPC + '])(?:' + '|'.join(re.escape(k) for k in keys) + ')(?![' + JPC + '])|' + PHRASE + ')')
        self.log = {}
    def segment(self, part):
        out = []; buf = ''; i = 0
        def flush():
            nonlocal buf
            if buf: out.append(('r', reading(buf))); buf = ''
        while i < len(part):
            k = next((k for k in self.seg if part.startswith(k, i)), None)
            if k:
                flush(); out.append(('s' if k in SUFFIX else 'd', self.d[k])); i += len(k)
            else:
                buf += part[i]; i += 1
        flush()
        res = ''
        for kind, txt in out:
            res += txt if (not res or kind == 's') else ' ' + txt
        return res
    def read(self, m):
        if m in self.d: return self.d[m]
        return ' '.join(self.d.get(p) or self.segment(p) for p in m.split(' '))
    def __call__(self, text):
        out = []; last = 0
        for mt in self.rx.finditer(text):
            s, e = mt.span(); m = mt.group(0)
            out.append(text[last:e]); last = e
            if not re.search(rf'[{JPC}]', m): continue
            r = self.read(m)
            if not r or r == m: continue
            tail = text[e:e + 40]
            pm = re.match(r'\s?\(([^()]*)\)', tail)
            if pm and HANGUL.search(pm.group(1)):
                a = re.sub(r'\s', '', pm.group(1)); b = re.sub(r'\s', '', r)
                if a.startswith(b) or b.startswith(a) or a.split('·')[0] == b: continue
            if s > 0 and text[s - 1] == '(' and text[e:e + 1] == ')' and HANGUL.search(text[max(0, s - 14):s]): continue
            self.log[m] = r
            out.append(f'({r})')
        out.append(text[last:])
        return ''.join(out)

def annotate_html(page, ann):
    toks = re.split(r'(<[^>]+>)', page)
    skip = []  # stack of closing tags we wait for
    out = []
    for t in toks:
        if t.startswith('<'):
            low = t.lower()
            if skip:
                if low.startswith('<' + skip[-1]): skip.append(skip[-1])
                elif low.startswith('</' + skip[-1]): skip.pop()
            else:
                if low.startswith('<style') or low.startswith('<script') or low.startswith('<title'): skip.append(re.match(r'<(\w+)', low).group(1))
                elif 'class="jn"' in low or 'class="plain"' in low or 'class="credits"' in low: skip.append(re.match(r'<(\w+)', low).group(1))
            out.append(t)
        else:
            out.append(t if skip or not re.search(rf'[{JPC}]', t) else ann(t))
    return ''.join(out)
