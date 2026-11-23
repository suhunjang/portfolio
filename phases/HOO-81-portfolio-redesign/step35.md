# Step 35 — focus-trap-lightbox

- 목적: lightbox trap 연결, 기존 Tab 리스너 제거, focus-visible.
- 예상 17분 / 선행 0~34 / 공통 절차 설계 §15
- read-first: 설계 §8.2(step 35); step 34 `trapFocus`, `ensureLightbox`, 기존 lightbox Tab 리스너, `.shot-zoom`, `:focus-visible`
- tracked 허용(exact): `js/main.js`(lightbox 열기·닫기 trap 연결과 기존 Tab 리스너 제거만), `css/style.css`(`:focus-visible`만), `tests/specs/focus-lightbox.spec.js`(신규)
- runtime: R0
- 금지: §15.7, `index.html`, `js/data.js`, `css/themes.css`, trapFocus 시그니처와 모달 연결, focus-modal.spec

## 작업 (TDD)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step35`
2. spec(desktop-dark/light) 먼저 실패 확인: grid 카드 모달 → `.shot-zoom` lightbox에서 Tab/Shift+Tab이 lightbox 안에서만 순환; Esc 1회 lightbox 닫힘·`.shot-zoom` 복귀·이후 모달 경계 순환; Esc 2회 모달 닫힘·트리거 복귀; lightbox 3회 열고 닫은 뒤에도 Tab 한 칸; 키보드로 도달한 `.featured-card`, `.project-card`, 모달 닫기 버튼, `.shot-zoom`의 outline-style ≠ none.
3. main.js: 열 때 push(`.shot-zoom`)·닫을 때 release, 기존 리스너 제거. style.css: outline 유지·보강(토큰만).

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- focus-lightbox.spec.js focus-modal.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step35.json --allow js/main.js,css/style.css,tests/specs/focus-lightbox.spec.js` → exit 0
