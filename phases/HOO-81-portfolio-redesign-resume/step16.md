# Resume Step 16 — focus-trap-lightbox (원 step 52)

- 목적: 원 §6.1 lightbox trap, 기존 Tab 리스너 제거, focus-visible(BASE token만).
- 17분 / 선행 0~15 / 공통 원 §9 + §R1·§R2 no-op / gate `RGATE 16`
- 허용(exact): `js/main.js`(lightbox trap·리스너 제거만), `css/style.css`(`:focus-visible` outline·outline-offset만), `tests/specs/focus-lightbox.spec.js`(신규)
- runtime: R0
- 추가 금지: `index.html`, `js/data.js`, 새 색·named·`currentColor`, 색 규칙 순서, trapFocus 시그니처·모달 연결, focus-modal.spec

## 작업
1. `RSNAP 16`
2. RED spec(desktop-dark/light): 모달 → `.shot-zoom` lightbox Tab/Shift+Tab 내부 순환; Esc 1회 lightbox 닫힘·`.shot-zoom` 복귀·모달 순환; Esc 2회 모달 닫힘·트리거 복귀; 3회 반복 후 Tab 한 칸; 키보드 도달 `.featured-card`·`.project-card`·모달 닫기·`.shot-zoom` outline-style ≠ none.
3. 구현.

## AC
- `T focus-lightbox.spec.js focus-modal.spec.js GS && FULL && VS && RGATE 16 js/main.js,css/style.css,tests/specs/focus-lightbox.spec.js`
