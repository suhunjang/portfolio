# Resume Step 15 — focus-trap-modal (원 step 51)

- 목적: 원 §6.1 `trapFocus` 구현과 모달 연결.
- 17분 / 선행 0~14 / 공통 원 §9 + §R1·§R2 no-op / gate `RGATE 15`
- 허용(exact): `js/main.js`(`trapFocus`·모달 trap만), `tests/specs/focus-modal.spec.js`(신규)
- runtime: R0
- 추가 금지: `index.html`, `js/data.js`, `css/*`, lightbox 코드

## 작업
1. `RSNAP 15`
2. RED spec(desktop-dark/light, mobile-dark): 마지막→Tab→첫, 첫→Shift+Tab→마지막, 밖으로 안 나감; button·backdrop·esc 닫기 후 트리거 복귀; `#heroFeatured`·`#projectGrid` 트리거; 2회 열고 닫아도 Tab 한 칸.
3. 구현.

## AC
- `T focus-modal.spec.js && FULL && VS && RGATE 15 js/main.js,tests/specs/focus-modal.spec.js`
