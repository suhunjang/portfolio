# Step 27 — axe-prepare-lightbox

- 목적: lightbox 준비와 `prepareForAxe`.
- 예상 19분 / 선행 0~26 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §3(lightbox), §7.4, §8.4(step 27, 합성 fixture)
- tracked 허용(exact): `tests/helpers/axe-prepare.js`(추가만: `prepareLightbox`, `prepareOverlay`, `prepareForAxe`), `tests/specs/axe-prepare-lightbox.spec.js`(신규)
- runtime: R0
- 금지: §15.7, step 25·26 함수 동작

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step27`
2. 설계 §8.4 step 27 계약.
3. spec(desktop-dark/light): page → `body`·null, modal → `#projectModal`, lightbox → `.lightbox`·img 로딩·포커스 내부; shots 없는 grid index → `lightbox-not-open`; `page.route`로 이미지 abort → `content-not-loaded:img`; `scenario: 'x'`·`prepareOverlay({ scenario: 'page' })` → `unknown-scenario`; no-shots fixture(grid 0·1 shots 없음 + 대표 버튼 0) → `findProjectWithShots` null·`__opens === 2`·`__closes === 2`·대표 click 0·lightbox `no-shots-project`; shots fixture(1에만 `.shot-zoom` + 대표 버튼 1) → 1·opens/closes 2·대표 0; `.modal-section` 안 깨진 img → `content-not-loaded:img`, 0×0 svg → `content-not-loaded:svg`.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-prepare-lightbox.spec.js axe-prepare-modal.spec.js axe-prepare-page.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step27.json --allow tests/helpers/axe-prepare.js,tests/specs/axe-prepare-lightbox.spec.js` → exit 0
