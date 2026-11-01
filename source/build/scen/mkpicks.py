# builds scen/picks.json from (card, imgkey, sheet, index, caption) tuples
import json, os
SEL = [
    ('a:a_kofuku', 'x_kofuku1', 's1', 5, '고후쿠역 나무 역사'),
    ('a:a_kofuku', 'x_kofuku2', 's1', 17, '역사 안을 덮은 소원 쪽지 · 10월'),
    ('a:a_kofuku', 'x_kofuku4', 's1', 13, '고후쿠역 플랫폼과 역사 · 8월'),
    ('a:a_manabe', 'x_manabe1', 's1', 25, '일본 정원 연못 · 5월'),
    ('a:a_manabe', 'x_manabe2', 's1', 37, '침엽수 정원 산책로 · 5월'),
    ('a:a_manabe', 'x_manabe3', 's1', 30, '푸른 가문비나무 정원 · 5월'),
    ('a:b_kurodake', 'x_kuro1', 's2', 42, '구로다케 로프웨이 산기슭역과 단풍'),
    ('a:b_kurodake', 'x_kuro2', 's2', 12, '가을 소운쿄 절벽'),
    ('a:b_kurodake', 'x_kuro3', 's2', 9, '소운쿄 온천 입구의 단풍'),
    ('a:b_falls', 'x_falls1', 's2', 30, '긴가 폭포'),
    ('a:b_falls', 'x_falls2', 's2', 31, '류세이 폭포 · 늦가을'),
    ('a:b_falls', 'x_falls3', 's2', 33, '눈 덮인 류세이 폭포'),
    ('a:d_fukidashi', 'x_fuki1', 's3', 10, '후키다시 공원 용천수 · 11월'),
    ('a:d_fukidashi', 'x_fuki2', 's3', 3, '후키다시 공원 연못 · 11월'),
    ('a:d_fukidashi', 'x_fuki3', 's3', 85, '국도 276호에서 본 요테이산'),
    ('a:e_nikka', 'x_nikka1', 's5', 0, '석조 정문 · 8월'),
    ('a:e_nikka', 'x_nikka2', 's5', 44, '빨간 지붕의 킬른탑(건조탑)'),
    ('a:e_nikka', 'x_nikka3', 's5', 65, '석탄 직화 단식 증류기'),
    ('a:f_hokudai', 'x_hokudai1', 's6', 8, '은행나무 가로수길 · 11월'),
    ('a:f_hokudai', 'x_hokudai2', 's6', 3, '노랗게 물든 은행나무 길'),
    ('a:f_hokudai', 'x_hokudai3', 's6', 30, '가을 캠퍼스 은행나무'),
    ('pool:butadon', 'x_butadon1', 'f1', 2, '숯불 향 오비히로식 부타동'),
    ('pool:butadon', 'x_butadon2', 'f1', 19, '오비히로 부타동'),
    ('pool:butadon', 'x_butadon3', 'f1', 50, '달콤 짭짤한 소스의 부타동'),
    ('pool:jingisukan', 'x_jingi1', 'f1', 62, '숙주를 깐 징기스칸 철판'),
    ('pool:jingisukan', 'x_jingi2', 'f1', 66, '양고기와 채소 징기스칸'),
    ('pool:jingisukan', 'x_jingi3', 'f1', 60, '굽기 전 양고기와 채소'),
]
extra = json.load(open('scen/sel_extra.json')) if os.path.exists('scen/sel_extra.json') else []
out = []
seenk = set()
for card, k, sh, i, cap in SEL + [tuple(x) for x in extra]:
    assert k.startswith('x_') and k not in seenk, k
    seenk.add(k)
    f = json.load(open(f'scen/th/{sh}.json'))[i][0]
    out.append([card, k, f, cap])
json.dump(out, open('scen/picks.json', 'w'), ensure_ascii=False, indent=0)
print(len(out))
