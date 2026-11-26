# Resume Step 29 — focus-trap-lightbox (원 step 52)

- 목적: 원 §6.1 lightbox trap, 기존 Tab 리스너 제거, focus-visible(BASE token만).
- 17분 / 선행 0~28 / 공통 원 §9 + §R1·§R2 no-op·§R11 / gate `RGATE 29`
- 허용(exact): `js/main.js`(lightbox trap·리스너 제거만), `css/style.css`(`:focus-visible` outline·outline-offset만), `tests/specs/focus-lightbox.spec.js`(신규)
- 필수 산출물(REQ): `tests/specs/focus-lightbox.spec.js,tests/specs/focus-modal.spec.js,js/main.js,css/style.css`
- runtime: R0
- 추가 금지: `index.html`, `js/data.js`, 새 색·named·`currentColor`, 색 규칙 순서, trapFocus 시그니처·모달 연결, focus-modal.spec

## 작업
1. `RSNAP 29` → no-op 첫 probe `REQ 29 tests/specs/focus-lightbox.spec.js,tests/specs/focus-modal.spec.js,js/main.js,css/style.css`. PASS면 나머지 AC 실행 → 통과 시 `resume step29: no-op`. REQ FAIL 또는 AC 실패면 아래 작업 후 완전한 AC 재실행(`focus-modal.spec.js` 없음은 허용 경로 밖 → resume 28 보고·중단).
2. RED spec(desktop-dark/light): 모달 → `.shot-zoom` lightbox Tab/Shift+Tab 내부 순환; Esc 1회 lightbox 닫힘·`.shot-zoom` 복귀·모달 순환; Esc 2회 모달 닫힘·트리거 복귀; 3회 반복 후 Tab 한 칸; 키보드 도달 `.featured-card`·`.project-card`·모달 닫기·`.shot-zoom` outline-style ≠ none.
3. 구현.

## AC
- `REQ 29 tests/specs/focus-lightbox.spec.js,tests/specs/focus-modal.spec.js,js/main.js,css/style.css && T focus-lightbox.spec.js focus-modal.spec.js GS && FULL && VS && RGATE 29 js/main.js,css/style.css,tests/specs/focus-lightbox.spec.js`(첫 명령 stdout `required-artifacts step129: OK 4`)
