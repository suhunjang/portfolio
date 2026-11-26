# Step 31 — axe-prepare-lightbox

- 목적: §6.3 step 31.
- 19분 / 선행 0~30 / 공통 §9 / gate GATE
- 허용(exact): `tests/helpers/axe-prepare.js`(추가만: `prepareLightbox`, `prepareOverlay`, `prepareForAxe`), `tests/specs/axe-prepare-lightbox.spec.js`(신규)
- runtime: R0
- 추가 금지: step 29·30 동작

## 작업
1. `SNAP 31`
2. spec(desktop-dark/light): page → `body`·null, modal → `#projectModal`, lightbox → `.lightbox`·img 로딩·포커스 내부; shots 없는 index → `lightbox-not-open`; 이미지 abort → `content-not-loaded:img`; `scenario: 'x'`·`prepareOverlay({ scenario: 'page' })` → `unknown-scenario`; no-shots fixture(grid 0·1 + 대표 0) → `findProjectWithShots` null·`__opens === 2`·`__closes === 2`·대표 click 0·`no-shots-project`; shots fixture(1에만 `.shot-zoom` + 대표 1) → 1·opens/closes 2·대표 0; 깨진 img → `content-not-loaded:img`, 0×0 svg → `content-not-loaded:svg`.

## AC
- `T axe-prepare-lightbox.spec.js axe-prepare-modal.spec.js axe-prepare-page.spec.js && FULL && VS && GATE 31 tests/helpers/axe-prepare.js,tests/specs/axe-prepare-lightbox.spec.js`
