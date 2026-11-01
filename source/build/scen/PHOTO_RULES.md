# 사진 수집 공통 규칙 (v19 작업용)

작업 폴더: `/home/claude/proj/일본여행계획/build` (아래에서 `build/`)

## 목적
한국어 여행 계획 웹페이지 "홋카이도 맛집 투어 계획"(여행일 2026/11/2–6)에 넣을 Wikimedia Commons 사진을 골라 내려받습니다. 동료 3명에게 나눠 줄 페이지라 사진이 그 장소·음식을 분명히 보여 줘야 합니다.

## 라이선스
- 허용: CC BY, CC BY-SA (버전 무관), CC0, Public domain.
- 제외: NC·ND가 들어간 것, GFDL만 있는 것, 작가(author)를 알 수 없는 것.

## 중복 금지 (페이지 빌드가 같은 사진 두 번을 허용하지 않음)
- `build/photos.json`의 모든 항목 `[imgkey, Commons파일명, ...]`의 Commons 파일명, `build/img/meta.json`의 `file` 값에 있는 파일은 쓰지 말 것.
- 다른 사진 담당 작업자도 동시에 일합니다. 끝내기 전에 `build/scen/photo_out_*.json`(내 것 제외)을 읽어 같은 Commons 파일을 고르지 않았는지 확인하고, 겹치면 내 쪽을 다른 사진으로 바꿀 것.
- 내 결과 안에서도 같은 Commons 파일은 한 번만.

## 고치면 안 되는 파일
data2.py, build2.py, photos.json, img/meta.json, scen/picks.json, scen/meta_raw.json, scen/scen_*.py, site/ 아래 전부. 
새로 만드는 것만 허용: `build/img/<내 접두사>*.jpg`, `build/scen/photo_out_<이름>.json`, 작업 폴더 `build/scen/work_<이름>/`.
(예외: picks.json에 이미 정해진 `x_*` 키는 그 이름 그대로 `build/img/x_*.jpg`로 내려받아도 됨.)

## 네트워크
- `commons.wikimedia.org`의 API와 `upload.wikimedia.org`만 사용. 다른 사이트 X. WebFetch 도구 사용 금지.
- User-Agent: `HokkaidoTripPlanner/1.0 (personal itinerary)` (curl `-A`).
- 요청 사이 2–3초 쉬기. 429가 나오면 30–60초 기다렸다 다시. 동시에 여러 요청 보내지 말 것.
- 효율적인 API (한 번에 파일·라이선스·썸네일 URL):
  - 카테고리: `https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=categorymembers&gcmtitle=Category:<이름>&gcmtype=file&gcmlimit=50&prop=imageinfo&iiprop=url|size|extmetadata&iiurlwidth=330`
  - 하위 카테고리: `action=query&list=categorymembers&cmtitle=Category:<이름>&cmtype=subcat&cmlimit=100`
  - 검색: `generator=search&gsrnamespace=6&gsrsearch=<검색어>&gsrlimit=50` (나머지 prop 같음). 일본어·영어 검색어 둘 다 써 볼 것.
  - 카테고리 찾기: `list=search&srnamespace=14&srsearch=<검색어>`
  - extmetadata의 `LicenseUrl`/`LicenseShortName`/`Artist`(HTML 태그 제거)/`DateTimeOriginal`로 라이선스·작가·촬영일 확인.
- 썸네일 너비는 표준값만: 330, 500, 960 (다른 숫자는 차단될 수 있음).

## 눈으로 확인하고 고르기 (필수)
1. 후보 썸네일(330px)을 받아 PIL로 contact sheet를 만듭니다. 한 장에 20–30개, 칸마다 번호와 촬영월을 적고, `build/scen/work_<이름>/sheet_N.jpg`로 저장.
2. **Read 도구로 sheet 이미지를 직접 보고** 고릅니다.
3. 기준: 그 장소·음식이 분명히 보일 것. 흐리거나 기울거나 너무 어두운 사진, 사람 얼굴 클로즈업, 큰 워터마크·글자, 거의 같은 구도 반복은 제외. 늦가을·초겨울(10–12월) 사진을 먼저 고르고, 없으면 다른 계절도 됩니다(캡션에 계절 표기).
4. 너무 작은 원본(긴 쪽 500px 미만)은 피할 것.

## 저장
- 최종 사진은 960px 썸네일(원본이 960보다 작으면 원본 URL)을 받아 PIL로 긴 쪽 560px 이하로 줄이고, RGB JPEG(quality=76, optimize=True, progressive=True)로 `build/img/<imgkey>.jpg`에 저장.
- imgkey: 영문 소문자·숫자·`_`만, 내 접두사로 시작 (예: `y_kofuku5`).

## 캡션 (장소·동네 사진만)
- 한국어로 짧게: 무엇이 보이는지 + 촬영 달을 알면 ` · 11월`처럼. 
- 기존 예: `시코쓰호 호숫가 · 11월`, `야마센 철교 · 11월`, `해 질 녘 조명 켜진 산책로`, `눈 덮인 아사히다케`.
- 음식 예시 사진은 캡션 대신 `0`(같은 종류 음식 예시라는 뜻). 그 가게에서 찍은 사진이 확실하면(파일명·설명에 가게 이름) `"이 가게"`.

## 결과 파일 `build/scen/photo_out_<이름>.json`
```json
{"photos": {"<카드키>": [["<imgkey>", "<Commons 파일명>", "<캡션 또는 0>"], ...]},
 "meta": {"<imgkey>": {"file": "<Commons 파일명>", "page": "https://commons.wikimedia.org/wiki/File:<파일명 URL인코딩>",
                       "license": "<LicenseUrl, 없으면 LicenseShortName>", "author": "<작가 이름 텍스트>",
                       "size": [w, h], "author_ok": true, "date": "<촬영일>"}}}
```
- Commons 파일명은 `File:` 없이, 공백은 `_`로.
- Public domain/CC0는 license 값에 `https://creativecommons.org/publicdomain/zero/1.0/` 또는 `Public_domain` 문자열이 들어가게.
- 카드 안 사진 순서 = 페이지에 보일 순서. 가장 대표적인 사진을 맨 앞에.
- 작업 중간에도 결과 파일을 자주 저장(덮어쓰기)해 둘 것.

## 마지막 점검과 보고
- 결과 JSON을 파이썬으로 다시 읽어: 모든 imgkey 파일이 실제로 있는지, 라이선스가 허용 목록인지, Commons 파일 중복이 없는지(기존 photos.json·meta.json·다른 photo_out 포함) 검사.
- 고른 사진 전체의 최종 contact sheet `build/scen/work_<이름>/final.jpg`(카드키·캡션 표시)를 만들고 Read로 한 번 더 확인.
- 보고(한국어, 짧게): 카드키별 장수 표, 못 채운 카드와 이유, final.jpg 경로.
