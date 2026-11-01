# AGENTS.md — 홋카이도 맛집 투어 계획 (Codex·다른 AI용 작업 설명서)

이 저장소는 **2026-11-02 ~ 11-06 홋카이도 렌터카 여행**(경일·동재·현준, 숙소 삿포로 북17조) 계획 페이지입니다.
처음엔 Claude가 만들었고, 이제 ChatGPT(Codex)도 같은 방식으로 고치고 다시 올릴 수 있게 원본을 모두 넣어 두었습니다.

- 공개 주소: https://dragon940111-bot.github.io/okkaido-trip/ (GitHub Pages, `main` 브랜치 맨 위 폴더를 그대로 보여 줌)
- 받는 사람들은 휴대폰 홈 화면에 아이콘으로 깔아서 씀(오프라인 동작). 새 판을 올리면 열 때 **"업데이트됨 → 업데이트하기"** 창이 뜸.

---

## 1. 폴더 지도

| 위치 | 무엇 | 손으로 고치나 |
|---|---|---|
| `index.html` `guide.html` `sw.js` `manifest.webmanifest` `icon-*.png` `i/` `p/` `f/` | **배포된 결과물**(공개 사이트). `build_all.sh`가 만듦 | ❌ 직접 고치지 말 것 |
| `source/build/` | 투어 계획 원본 | ✅ 여기 고침 |
| `source/build/data2.py` | **일정·식당·대안·지역 데이터 전부** | ✅ 가장 자주 고침 |
| `source/build/body2.html` | 페이지 뼈대·고정 설명문(맨 위 소개, 표시 읽는 법, 각 구역 안내) | ✅ |
| `source/build/build2.py` | 페이지 생성기(카드·시간표 HTML, 일부 설명 문구) | 조심해서 |
| `source/build/css2.css` | 디자인 | 조심해서 |
| `source/build/book19.py` `lodging19.py` `altbook19.py` (+ `.css`) | 미리 할 것·예약 목록, 숙소 안내, 대안 예약 목록 | ✅ |
| `source/build/wx19.py` | 날씨 표(11/1 기준) | ✅ |
| `source/build/scen/scen_*.py` | 일정 변경 대안 A–G 상세 | ✅ |
| `source/build/photos.json` / `img/meta.json` | 카드별 사진 목록 / 사진 출처 | 조심해서 |
| `source/build/img/` | 사진 원본(`o_*` 가게 공식, `u_*` 여행자 제공, 나머지 자유 라이선스) | |
| `source/build/site/map/` | 날짜별 경로 지도 그림(원본) | |
| `source/build/polish.json` | 빌드 마지막에 **문장 통째 바꾸기**(원문 → 바뀐 문장). 원본을 고쳤는데 안 바뀌면 여기 확인 | ✅ |
| `source/build/kodict.json` | 일본어 지명·가게명 옆 한국어 읽기 | |
| `source/운전가이드/` | 운전 가이드북 원본(`build_guide.py`, `tpl.html`, `figs.py`, `assets/`, `site/img/`) | ✅ |
| `source/오프라인/build_offline.py` | 공개판(PWA: 사진 묶음·글꼴·서비스워커·다운로드/업데이트 화면) + 한 파일 오프라인판 생성 | 조심해서 |
| `source/tools/build_all.sh` | **한 번에 전부 빌드 + 맨 위로 복사** | |
| `source/package.json` / `requirements.txt` | 글꼴(npm) / 파이썬 패키지 | |

`source/build/data2.py` 는 **위에서 정의하고, 아래쪽에 "패치 블록"을 계속 덧붙이는 구조**입니다(같은 항목을 아래에서 다시 바꿈). 무엇이 최종인지 헷갈리면 파일 **맨 아래부터** 그 키를 검색하세요.

---

## 2. 자주 하는 수정

### 2-1. 식당 정보 바꾸기 (영업시간·휴무·가격·팁·상태)
식당은 `r('키', name=..., ko=..., genre=..., area=..., hours=..., closed=..., price=..., status=..., tip=..., why=..., tb=..., pid=..., q=...)` 로 정의됨.
- 가장 안전한 방법: `data2.py` **맨 아래**에 한 줄 추가
  ```python
  R['gop'].update(hours='11:30–21:30 (수·목 휴무)', status='11/2 ✅ (재확인 11/1)')
  ```
- 필드 뜻: `name` 일본어 가게명, `ko` 한글 이름, `area` 위치 설명, `hours` 영업, `closed` 휴무, `price` 가격, `status` 그날 영업 여부 표시, `tip` 팁, `why` 추천 이유, `g`/`gn` 구글 평점/리뷰 수, `t` 타베로그 점수, `tb` 타베로그 경로(`/hokkaido/…/`), `pid` 구글 place_id, `q` 구글 검색어.

### 2-2. 시간표 줄·메인 식당·대안 바꾸기
날짜별 시간표는 `DAYS[n-1]['items']` 의 튜플: `(시각, 종류, 참조키, 제목, 부제, 지도번호, 대안키목록)`
- 종류: `'eat'`(식사) `'stay'`(장소) `'move'`(이동) `'note'`(메모) `'free'` 등
- 이미 있는 줄의 대안·제목만 바꿀 때는 맨 아래에 헬퍼 사용:
  ```python
  _setalts(3, '11:30', ['okina', 'bocca', 'wasabi'], title='점심: 소바', sub='줄 서면 11:00 도착')
  ```
  (`_setalts(날짜번호, '시각', [대안키…], ref=메인키, title=…, sub=…, num=지도번호)`)
- 메인을 대안 중 하나로 맞바꿀 때: `ref`(메인 키)와 대안 목록을 함께 바꾸고, 시간·이동 시간이 맞는지 앞뒤 줄도 확인.
- 새 식당이 필요하면 먼저 `r('새키', …)` 로 정의(사진 없으면 카드에 사진 칸만 빠짐).

### 2-3. 설명 문구 고치기
- 고정 설명문: `source/build/body2.html` (맨 위 소개 `<ul class="leadlist">`, "이 페이지의 표시 읽는 법", 각 `<section>`의 `<p class="sub">`)
- 카드·시간표 쪽 짧은 문구: `build2.py` 문자열, 예약 쪽은 `book19.py`·`lodging19.py`·`altbook19.py`
- **말투 규칙**: 사용자 말투로 짧게 — "~했음 / ~함 / ~임 / ~됨 / ~하면 됨". 확인 안 된 것은 "(확인 못 함)".
- 고쳤는데 결과에 반영 안 되면 `polish.json`에 원문 키가 있는지 확인(있으면 그 값을 고치거나 키 삭제).

### 2-4. 공지 넣기 (예: "11/4 점심 바뀜")
`body2.html` 맨 위 소개(`<ul class="leadlist">…</ul>`) 바로 아래에:
```html
<p class="notice" style="margin:10px 0;padding:10px 12px;border-radius:10px;background:#fff3e6;border:1px solid #f0b37e;font-weight:700">📢 11/4 점심 바뀜: ○○ → △△ (이유 한 줄)</p>
```

### 2-5. 사진
- 카드 사진은 `photos.json` 의 `"카드키": [["사진키", "출처파일", "이름표"], …]` 앞쪽 3장이 보임. 파일은 `img/사진키.jpg`, 출처는 `img/meta.json`.
- 가게 실제 사진(`o_*`, `u_*`)이 있으면 예시 사진은 자동으로 안 섞임.
- **손님 리뷰 사진 등 허락 없는 사진은 넣지 말 것.**

### 2-6. 운전 가이드북
`source/운전가이드/build_guide.py`(장 내용) · `tpl.html`(틀) · `assets/hwy|park/*.json`(실제 사진 목록).

---

## 3. 빌드 & 배포

```bash
# 처음 한 번
cd source && npm ci && pip install -r requirements.txt && cd ..
# (Pillow는 AVIF 저장이 되는 버전이어야 함: python3 -c "import PIL.features as f; print(f.check('avif'))" → True)

# 고친 뒤 매번
bash source/tools/build_all.sh      # 약 3–5분 (AVIF 변환이 오래 걸림)
git add -A
git commit -m "무엇을 바꿨는지 한국어로"
git push                            # 1–2분 뒤 공개 주소 반영
```
- `build_all.sh` 순서: `build2.py`(투어) → `build_guide.py`(가이드) → `build_offline.py`(공개판 + 한 파일 오프라인판) → 공개판을 저장소 맨 위로 복사(`i/ p/ f/` 교체).
- `sw.js` 첫 줄 `// 버전 xxxx` 가 바뀌면 사용자 폰에 "업데이트됨" 창이 뜸. 내용이 바뀌면 자동으로 바뀜(손댈 필요 없음).
- 판 날짜 표시는 빌드한 날짜. 고정하려면 `TRIP_STAMP=2026-11-01 bash source/tools/build_all.sh`.
- 한 파일 오프라인판은 `source/오프라인/out/홋카이도_여행_오프라인.html` 에 생김(약 21MB, git에는 안 올림). 카톡으로 파일 보낼 때만 씀.
- PR로 올릴 때: PR을 만들고 사용자가 GitHub 앱에서 **Merge** 를 누르면 반영됨. (`main`에 합쳐져야 공개 주소가 바뀜)

### 올리기 전 확인 (가능하면 Playwright, 아니면 최소한 아래)
1. `build2.py` 마지막 줄 `MISSING []` (빠진 사진 키 없음)
2. 결과 크기: `index.html` 약 1.5–2MB, `guide.html` 수백 KB, `p/` 약 22MB, `f/` 약 1.5MB
3. 휴대폰 폭(390px)에서 가로로 넘치는 곳 없음, 스크립트 오류 없음
4. 바꾼 부분이 `index.html` 에 실제로 들어갔는지 검색(`grep`)

---

## 4. 규칙

- 페이지 글은 **한국어**(가게 일본어 이름·주소는 그대로 + 한글 읽기).
- **예약 확정·결제·가게에 메시지 보내기 절대 하지 않음.** 예약 안내만 씀.
- 로그인·카드 정보·개인정보 입력 하지 않음.
- 사진은 가게 공식 / 여행자 제공(허락 받음) / 자유 라이선스(Wikimedia Commons)만.
- 확인 못 한 사실은 지어내지 말고 "(확인 못 함)".
- 사용자(경일)에게 보고할 때: 한국어, 질문엔 먼저 답하고 작업, 파일 경로는 전체 경로, 확인 못 한 건 "직접 보지 못함".

## 5. 손대지 말 것

- 저장소 맨 위 결과물(`index.html`, `guide.html`, `sw.js`, `i/`, `p/`, `f/`)을 **손으로** 고치기 → 다음 빌드 때 덮어써짐. 항상 `source/` 고치고 빌드.
- `sw.js` 의 캐시·다운로드 로직, `build_offline.py` 의 다운로드/업데이트 화면 로직(오프라인 동작이 깨질 수 있음). 고칠 땐 오프라인·업데이트 흐름을 꼭 시험.
- `source/build/scen/userphotos/asset_urls.json` (Claude 쪽 사진 주소 ↔ 원본 파일 연결표, 빌드에 필요).
- Claude 쪽 페이지(claude.ai/artifact/…)는 이 저장소에서 바꿀 수 없음. **공유용 정본은 이 GitHub Pages 주소.**
