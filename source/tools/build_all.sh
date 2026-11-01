#!/usr/bin/env bash
# 홋카이도 여행 페이지 전체 빌드 + 공개판(저장소 맨 위)에 반영
#   사용: bash source/tools/build_all.sh   (저장소 어디서 실행해도 됨)
#   준비: cd source && npm ci && pip install -r requirements.txt
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"     # .../source
REPO="$(cd "$SRC/.." && pwd)"                                # 저장소 맨 위 = 공개 사이트
export TRIP_ROOT="$SRC"
export FONTDIR="${FONTDIR:-$SRC/node_modules/@fontsource}"
export PWA_OUT="$SRC/오프라인/pwa"
export OFFLINE_OUT="$SRC/오프라인/out/홋카이도_여행_오프라인.html"
[ -d "$FONTDIR" ] || { echo "글꼴 없음: cd source && npm ci 먼저 실행"; exit 1; }
mkdir -p "$SRC/오프라인/out"
echo "== 1/3 투어 계획 (build2.py)"; ( cd "$SRC/build" && python3 build2.py | tail -3 )
echo "== 2/3 운전 가이드북 (build_guide.py)"; ( cd "$SRC/운전가이드" && python3 build_guide.py | tail -2 )
echo "== 3/3 오프라인판·공개판 (build_offline.py, 약 3–4분: AVIF 변환)"; ( cd "$SRC/오프라인" && python3 build_offline.py | tail -3 )
echo "== 공개판을 저장소 맨 위로 복사"
rm -rf "$REPO/i" "$REPO/p" "$REPO/f"
cp -r "$PWA_OUT/." "$REPO/"
echo "== 결과"
du -sh "$REPO/index.html" "$REPO/guide.html" "$REPO/i" "$REPO/p" "$REPO/f" 2>/dev/null
head -1 "$REPO/sw.js"
echo "한 파일 오프라인판: $OFFLINE_OUT (git에는 안 올라감)"
echo "다음: git add -A && git commit && git push  → 1–2분 뒤 https://dragon940111-bot.github.io/okkaido-trip/ 에 반영"
