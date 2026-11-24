# Step 41 — focus-trap-lightbox

- 목적: lightbox trap 연결, 기존 Tab 리스너 제거, focus-visible(기존 토큰만).
- 예상 17분 / 선행 0~40 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §8.2(step 41), §16.4(`:focus-visible` outline 예외); `trapFocus`, `ensureLightbox`, 기존 lightbox Tab 리스너, `:focus-visible`
- tracked 허용(exact): `js/main.js`(lightbox trap 연결과 기존 Tab 리스너 제거만), `css/style.css`(`:focus-visible`만, BASE 정의 토큰만), `tests/specs/focus-lightbox.spec.js`(신규)
- runtime: R0
- 금지: §15.7, `index.html`, `js/data.js`, `css/themes.css`, 새 색, trapFocus 시그니처·모달 연결, focus-modal.spec

## 작업 (TDD)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step41`
2. spec(desktop-dark/light) 먼저 실패 확인: lightbox 안 순환; Esc 1회 lightbox 닫힘·`.shot-zoom` 복귀·모달 순환; Esc 2회 모달 닫힘·트리거 복귀; 3회 반복 후 Tab 한 칸; 키보드 도달한 `.featured-card`, `.project-card`, 모달 닫기, `.shot-zoom`의 outline-style ≠ none.
3. main.js·style.css.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- focus-lightbox.spec.js focus-modal.spec.js design-guard.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step41.json --allow js/main.js,css/style.css,tests/specs/focus-lightbox.spec.js` → exit 0
