# Resume Step 28 — focus-trap-modal (원 step 51)

- 목적: 원 §6.1 `trapFocus` 구현과 모달 연결.
- 17분 / 선행 0~27 / 공통 원 §9 + §R1·§R2 no-op·§R11 / gate `RGATE 28`
- 허용(exact): `js/main.js`(`trapFocus`·모달 trap만), `tests/specs/focus-modal.spec.js`(신규)
- 필수 산출물(REQ): `tests/specs/focus-modal.spec.js,js/main.js`
- runtime: R0
- 추가 금지: `index.html`, `js/data.js`, `css/*`, lightbox 코드

## 작업
1. `RSNAP 28` → no-op 첫 probe `REQ 28 tests/specs/focus-modal.spec.js,js/main.js`. PASS면 나머지 AC 실행 → 통과 시 `resume step28: no-op`. REQ FAIL 또는 AC 실패면 아래 작업 후 완전한 AC 재실행.
2. RED spec(desktop-dark/light, mobile-dark): 마지막→Tab→첫, 첫→Shift+Tab→마지막, 밖으로 안 나감; button·backdrop·esc 닫기 후 트리거 복귀; `#heroFeatured`·`#projectGrid` 트리거; 2회 열고 닫아도 Tab 한 칸.
3. 구현.

## AC
- `REQ 28 tests/specs/focus-modal.spec.js,js/main.js && T focus-modal.spec.js && FULL && VS && RGATE 28 js/main.js,tests/specs/focus-modal.spec.js`(첫 명령 stdout `required-artifacts step128: OK 2`)
