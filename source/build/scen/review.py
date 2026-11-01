import json, os, sys
from PIL import Image, ImageDraw
picks = json.load(open('scen/picks.json'))
pref = sys.argv[1] if len(sys.argv) > 1 else ''
ks = [k for c, k, f, cap in picks if os.path.exists(f'img/{k}.jpg') and c.startswith(pref)]
C, T = 5, 240
rows = (len(ks) + C - 1) // C
S = Image.new('RGB', (C * T, rows * (T + 4)), (255, 255, 255))
d = ImageDraw.Draw(S)
for i, k in enumerate(ks):
    im = Image.open(f'img/{k}.jpg')
    im.thumbnail((T - 4, T - 18))
    x, y = (i % C) * T, (i // C) * (T + 4)
    S.paste(im, (x + 2, y + 16))
    d.text((x + 3, y + 2), k + ' ' + str(Image.open(f'img/{k}.jpg').size), fill=(0, 0, 0))
S.save('scen/th/review.jpg', quality=82)
print(len(ks))
