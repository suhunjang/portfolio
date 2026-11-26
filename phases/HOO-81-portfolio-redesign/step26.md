# Step 26 — modal-regression

- 목적: §5 `modal.js`와 모달·lightbox 회귀(BASE에서 통과).
- 18분 / 선행 0~25 / 공통 §9 / gate GATE
- 허용(exact): `tests/helpers/modal.js`, `tests/specs/modal-regression.spec.js`(신규)
- runtime: R0

## 작업
1. `SNAP 26`
2. spec(6 project): click·Enter 열기, 제목, `modal-open`; button·backdrop·esc 닫기 후 트리거 포커스·`modal-open` 해제; desktop lightbox: `findProjectWithShots`·탐색 후 닫힘·`.shot-zoom`으로 열림; Esc 1회 lightbox만, 2회 모달.

## AC
- `T modal-regression.spec.js && FULL && VS && GATE 26 tests/helpers/modal.js,tests/specs/modal-regression.spec.js`
