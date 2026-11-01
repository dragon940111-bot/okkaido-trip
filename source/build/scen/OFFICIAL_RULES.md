# 가게 공식 사진 받기 규칙 (v19.5)

작업 폴더: `/home/claude/proj/일본여행계획/build`

## 배경
사용자가 이 가게들의 사진 사용 허락을 받았다고 밝혀서, **가게가 타베로그에 직접 올린 공식 사진(お店からの公式写真)만** 받아 맛집 카드에 넣습니다. **손님 리뷰 사진(ユーザー投稿 — "（by お店）" 표시가 없는 사진)은 절대 받지 않습니다.**

## 방법
1. 먼저 Skill 도구로 `anthropic-skills:built-in-browser`를 불러 그 안내를 따르세요 (내장 브라우저 도구 `mcp__remote-devices__Claude_Browser__*`, ToolSearch로 불러오기). 내장 브라우저를 쓸 수 없으면 Chrome 확장(`mcp__claude-in-chrome__*`, 먼저 `anthropic-skills:chrome-browser` 스킬)을 씁니다.
2. **`tabs_create`로 자기 탭을 새로 만들고 모든 호출에 그 tabId를 지정**하세요(`preview_start`는 다른 탭을 재사용할 수 있어 금지). 페이지마다 주소가 내 가게인지 확인하고, 끝나면 탭을 닫습니다. 다른 작업자 여러 명이 같은 브라우저를 동시에 씁니다. 사용자가 열어 둔 탭은 건드리지 않습니다. 로그인·입력·CAPTCHA 풀기 금지.
3. 가게마다 `owner_url`(= 타베로그 가게 주소 + `dtlphotolst/?mode=owner&smp=2`, "お店からの公式写真" 목록)을 엽니다. 가게 사이에 5초 이상 쉽니다. "現在アクセスが集中" 페이지가 나오면 30–60초 기다렸다 다시 열고, 계속이면 그 가게는 건너뜁니다.
4. 페이지에서 사진 목록의 이미지 주소를 javascript_tool로 뽑습니다(예: `[...document.querySelectorAll('img')].map(i=>i.src||i.dataset.original).filter(s=>/tblg\.k-img\.com\/restaurant\/images\//.test(s))`). 공식 사진이 없으면("写真はありません" 등) 그 가게는 "공식 사진 없음"으로 기록하고 넘어갑니다. **판단 기준(정정됨): 타베로그는 가게 공식 사진도 `/Rvw/` 주소를 씁니다. 주소가 아니라 사진마다 "（by お店）" 표시와 `data-analytics-post-type="owner"`가 둘 다 있는지로 가립니다. 둘 다 있는 사진만 받고, "by ヒトサラ" 등 가게가 아닌 곳이 올린 사진과 손님 사진(표시 없음)은 절대 받지 않습니다.**
5. 고르기: 가게당 **최대 3장**. 음식(대표 메뉴) 사진을 먼저, 그다음 가게 외관/내부. 메뉴판·글자만 있는 이미지·가격표·로고만 있는 것은 빼기. 큰 크기 주소는 썸네일 주소의 크기 부분(예: `150x150_square_`)을 `640x640_rect_`로 바꾸면 되는 경우가 많습니다(안 되면 그대로).
6. 내려받기: 컨테이너 셸에서 **평범한 curl**로 이미지 주소만 받습니다(User-Agent 바꾸기 등 차단 우회 금지). 막히면 그 가게는 "받기 실패"로 기록. 받은 이미지는 PIL로 긴 쪽 560px 이하, RGB JPEG(quality=76, optimize, progressive)로 `build/img/o_<가게키>_<번호>.jpg`에 저장.
7. 받은 사진을 contact sheet로 묶어 **Read로 직접 보고** 음식·가게 사진이 맞는지, 손님 사진이 섞이지 않았는지 확인.

## 결과 `build/scen/official_<이름>.json`
```json
{"photos": {"<가게키>": [["o_<가게키>_1", "<원본 이미지 주소>", "가게 공식 사진"], ...]},
 "meta": {"o_<가게키>_1": {"file": "<원본 이미지 주소>", "page": "<owner_url>", "license": "shop_official", "author": "<가게 이름(일본어)> · 타베로그 가게 공식 사진", "source": "tabelog_owner"}},
 "none": ["<공식 사진이 없던 가게키>", ...], "failed": {"<가게키>": "<이유>"}}
```
- 결과 파일을 자주 저장. 다른 작업자 2명도 같은 방식으로 다른 가게를 맡고 있음(파일 이름만 다름).
- 기존 파일(data2.py, build2.py, photos.json, img/meta.json 등)은 고치지 말 것. 게시하지 말 것. WebFetch 금지.

## 보고 (한국어, 짧게)
공식 사진을 넣은 가게 수/장수, 공식 사진이 없던 가게, 실패한 가게와 이유, contact sheet 경로(전체 경로).

## 같은 가게가 카드 여러 개인 경우
목록 항목의 `also`에 다른 카드키가 있으면, 결과 `photos`에는 `key`로만 넣으세요(나중에 합칠 때 `also` 카드에도 같은 사진을 붙입니다). meta author는 "<가게 이름> · 타베로그 가게 공식 사진(by お店)".
