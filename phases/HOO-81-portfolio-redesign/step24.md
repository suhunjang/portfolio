# Step 24 — axe-prepare-modal

- 목적: 콘텐츠 로딩 검사와 modal 준비.
- 예상 18분 / 선행 0~23 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §3, §5, §7.4, §8.4(step 24)
- tracked 허용(exact): `tests/helpers/axe-prepare.js`(추가만), `tests/specs/axe-prepare-modal.spec.js`(신규)
- runtime: R0
- 금지: §15.7, modal.js·axe.js(import만)

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step24`
2. 설계 §8.4 step 24 계약.
3. spec(desktop-dark/light): 실제 사이트 `prepareModal`; 동작 fixture grid 우선(`__opens === 1`); `project-card-not-found:3`; `modal-not-open`; `content-not-loaded:text`; textLocator 단위.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-prepare-modal.spec.js axe-prepare-page.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step24.json --allow tests/helpers/axe-prepare.js,tests/specs/axe-prepare-modal.spec.js` → exit 0
