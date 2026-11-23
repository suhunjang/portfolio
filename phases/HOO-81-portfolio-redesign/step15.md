# Step 15 — modal-regression

- 목적: modal.js helper와 모달·lightbox 회귀(BASE 사이트에서 통과).
- 예상 18분 / 선행 0~14 / 공통 절차 설계 §15
- read-first: 설계 §3(모달, lightbox), §5(같은 data-project), §7.4, §11.4
- tracked 허용(exact): `tests/helpers/modal.js`(신규), `tests/specs/modal-regression.spec.js`(신규)
- runtime: R0
- 금지: §15.7, 테마·메뉴·scrollspy·typing·reduced-motion(step 16)

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step15`
2. `modal.js`: 설계 §7.4 계약 그대로(`GRID_CARD`, `gridCard`, `openFirstProjectByClick/Enter`, `closeVia`, `expectFocused`, `modalTitle`, `findProjectWithShots`).
3. `modal-regression.spec.js`(6 project): click·Enter로 열기, 제목 일치, `modal-open`; button·backdrop·esc 닫기 후 트리거 포커스 복귀·`modal-open` 해제; desktop lightbox: `findProjectWithShots` index 반환·탐색 후 닫힘·그 카드에서 `.shot-zoom`으로 열림; Esc 1회 lightbox만, 2회 모달.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- modal-regression.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step15.json --allow tests/helpers/modal.js,tests/specs/modal-regression.spec.js` → exit 0
