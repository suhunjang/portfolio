# Step 15 — axe-prepare-lightbox

- 목적: lightbox 준비와 결합 진입점 `prepareForAxe`.
- 예상 19분 / 선행 0~14 / 공통 절차 설계 §15
- read-first: 설계 §3(lightbox), §7.4, §8.4(step 15, 오류 코드, 합성 fixture)
- tracked 허용(exact): `tests/helpers/axe-prepare.js`(추가만: `prepareLightbox`, `prepareOverlay`, `prepareForAxe`), `tests/specs/axe-prepare-lightbox.spec.js`(신규)
- runtime: R0
- 금지: §15.7, step 13·14 함수 동작, 기존 spec·helper(import만)

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step15`
2. 설계 §8.4 step 15 계약 구현.
3. spec(desktop-dark/light): 실제 사이트 page → `body`·null, modal → `#projectModal`, lightbox → `.lightbox`·img 로딩·포커스 내부(본문 텍스트 없어도 통과); shots 없는 grid index로 lightbox → `lightbox-not-open`; `page.route`로 이미지 abort → `content-not-loaded:img`; `scenario: 'x'`, `prepareOverlay({ scenario: 'page' })` → `unknown-scenario`; no-shots fixture(grid 0·1 shots 없음 + 대표 버튼 0) → `findProjectWithShots` null·`__opens === 2`·`__closes === 2`·`modal-open` 없음·대표 click 0, lightbox → `no-shots-project`; shots fixture(1에만 `.shot-zoom` + 대표 버튼 1) → 1·opens/closes 2·대표 0; `.modal-section` 안 깨진 src img → `content-not-loaded:img`, 0×0 svg → `content-not-loaded:svg`.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-prepare-lightbox.spec.js axe-prepare-modal.spec.js axe-prepare-page.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step15.json --allow tests/helpers/axe-prepare.js,tests/specs/axe-prepare-lightbox.spec.js` → exit 0
