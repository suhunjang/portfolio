# Step 24 — axe-prepare-lightbox

- 목적: lightbox 준비와 결합 진입점 `prepareForAxe`.
- 예상 19분 / 선행 0~23 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §3(lightbox), §7.4, §8.4(step 24, 합성 fixture)
- tracked 허용(exact): `tests/helpers/axe-prepare.js`(추가만: `prepareLightbox`, `prepareOverlay`, `prepareForAxe`), `tests/specs/axe-prepare-lightbox.spec.js`(신규)
- runtime: R0
- 금지: §15.7, step 22·23 함수 동작

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step24`
2. 설계 §8.4 step 24 계약 구현.
3. spec(desktop-dark/light): page → `body`·null, modal → `#projectModal`, lightbox → `.lightbox`·img 로딩·포커스 내부; shots 없는 index → `lightbox-not-open`; 이미지 abort → `content-not-loaded:img`; `unknown-scenario` 2종; no-shots fixture → null·opens/closes 2·`no-shots-project`; shots fixture → 1·대표 click 0; 깨진 img·0×0 svg.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-prepare-lightbox.spec.js axe-prepare-modal.spec.js axe-prepare-page.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step24.json --allow tests/helpers/axe-prepare.js,tests/specs/axe-prepare-lightbox.spec.js` → exit 0
