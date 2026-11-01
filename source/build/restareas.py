# 이동 행 옆 "휴게소 1·2…" 칩 데이터 (v19.20)
# 키: (구역 id, 시각) — 구역 id는 day1..day5 또는 scen-A-d1 같은 대안 상세 일정 id, 시각은 이동 행 시각.
# 값: 주행 순서대로 (휴게소 코드, 방향). 방향: 道央道 上り=函館(남)방면·下り=旭川(북)방면, 道東道 上り=千歳恵庭방면·下り=帯広방면, 札樽道는 방향 없이(None).
# 경로 근거: 위키 IC/SA/PA 순서표 + 계획 문구의 진입·출구 IC + 구글맵 경로(일부). 2026-11-01 Claude.

SPOTS = {  # 코드: (일본어 정식명, 한국어 읽기)
    'wattsu':   ('輪厚パーキングエリア', '와쓰 PA'),
    'misawa':   ('美沢パーキングエリア', '미사와 PA'),
    'tarumae':  ('樽前サービスエリア', '다루마에 SA'),
    'hagino':   ('萩野パーキングエリア', '하기노 PA'),
    'tomiura':  ('富浦パーキングエリア', '도미우라 PA'),
    'usuzan':   ('有珠山サービスエリア', '우스잔 SA'),
    'nopporo':  ('野幌パーキングエリア', '놋포로 PA'),
    'iwamizawa':('岩見沢サービスエリア', '이와미자와 SA'),
    'chashinai':('茶志内パーキングエリア', '차시나이 PA'),
    'sunagawa': ('砂川サービスエリア', '스나가와 SA'),
    'otoe':     ('音江パーキングエリア', '오토에 PA'),
    'pippu':    ('比布大雪パーキングエリア', '핏푸 다이세쓰 PA'),
    'kiusu':    ('キウスパーキングエリア', '기우스 PA'),
    'yuni':     ('由仁パーキングエリア', '유니 PA'),
    'shimukappu':('占冠パーキングエリア', '시무캇푸 PA'),
    'tokachi':  ('十勝平原サービスエリア', '도카치 헤이겐 SA'),
    'kanayama': ('金山パーキングエリア 札樽自動車道', '가나야마 PA'),
}
U, D = '上り', '下り'
_D3_AM  = [('wattsu', U), ('misawa', U), ('tarumae', U), ('hagino', U), ('tomiura', U), ('usuzan', U)]  # 札幌北IC → 伊達IC
_D3_PM1 = [('usuzan', D), ('tomiura', D)]          # 伊達IC → 登別東IC (구글맵 경로 확인)
_D3_PM2 = [('hagino', D), ('tarumae', D)]          # 登別東IC → 苫小牧 방면 (美沢PA는 출구 IC 따라 달라 뺌)
_D3_HOME = [('wattsu', D)]                          # 苫小牧/新千歳 → 札幌
_NORTH  = [('nopporo', D), ('iwamizawa', D), ('chashinai', D), ('sunagawa', D), ('otoe', D)]  # 札幌 → 旭川
_SOUTH_FROM_TAKIKAWA = [('sunagawa', U), ('chashinai', U), ('iwamizawa', U), ('nopporo', U)]  # 滝川IC → 札幌
_KANAYAMA = [('kanayama', None)]

REST = {
    ('day2', '13:10'): _KANAYAMA,
    ('day2', '18:30'): _KANAYAMA,
    ('day3', '09:00'): _D3_AM,
    ('day3', '15:05'): _D3_PM1,
    ('day3', '17:45'): _D3_PM2,
    ('day3', '19:40'): _D3_HOME,
    ('day4', '09:00'): _NORTH,
    ('day4', '16:35'): _SOUTH_FROM_TAKIKAWA,
    ('day5', '08:15'): [('wattsu', U)],
    ('scen-A-d1', '09:00'): [('wattsu', U), ('kiusu', D), ('yuni', D)],
    ('scen-A-d1', '10:55'): [('tokachi', D)],
    ('scen-A-d1', '17:10'): [('tokachi', U), ('shimukappu', U), ('yuni', U), ('kiusu', U), ('wattsu', D)],
    ('scen-B-d1', '09:00'): _NORTH + [('pippu', D)],
    ('scen-B-d1', '17:15'): [('otoe', U)] + _SOUTH_FROM_TAKIKAWA,
    ('scen-C-d1', '08:40'): _D3_AM,
    ('scen-C-d1', '15:00'): _D3_PM1,
    ('scen-C-d1', '17:45'): _D3_PM2,
    ('scen-C-d1', '19:40'): _D3_HOME,
    ('scen-C-d2', '13:10'): _KANAYAMA,
    ('scen-C-d2', '18:30'): _KANAYAMA,
    ('scen-D-d1', '14:45'): _KANAYAMA,
    ('scen-E-d1', '11:40'): _KANAYAMA,
    ('scen-F-d1', '14:10'): [('misawa', D), ('wattsu', D)],
}
