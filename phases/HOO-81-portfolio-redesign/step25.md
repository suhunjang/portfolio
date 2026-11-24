# Step 25 — axe-prepare-lightbox

- 목적: lightbox 준비와 `prepareForAxe`.
- 예상 19분 / 선행 0~24 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §3, §7.4, §8.4(step 25)
- tracked 허용(exact): `tests/helpers/axe-prepare.js`(추가만), `tests/specs/axe-prepare-lightbox.spec.js`(신규)
- runtime: R0
- 금지: §15.7, step 23·24 함수 동작

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step25`
2. 설계 §8.4 step 25 계약.
3. spec(desktop-dark/light): page·modal·lightbox include; `lightbox-not-open`; 이미지 abort `content-not-loaded:img`; `unknown-scenario` 2종; no-shots·shots fixture; 깨진 img·0×0 svg.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-prepare-lightbox.spec.js axe-prepare-modal.spec.js axe-prepare-page.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step25.json --allow tests/helpers/axe-prepare.js,tests/specs/axe-prepare-lightbox.spec.js` → exit 0
