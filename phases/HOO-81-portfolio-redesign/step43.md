# Step 43 — component-hover-active

- 목적: desktop dark/light hover·active 비색 상태(transform·opacity만).
- 예상 15분 / 선행 0~42 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §16.2(step 43 hover·active), §16.4(DESIGN_HASH_CHECK 후 `Components.dc.html` 읽기 전용)
- tracked 허용(exact): `css/style.css`(`.hero-cta .btn`·`.featured-card`·`#projectGrid .project-card`의 `:hover`·`:active` 규칙에서 transform·opacity·transition만), `tests/specs/component-hover.spec.js`(신규)
- runtime: R0
- 금지: §15.7, `index.html`, `js/*`, 색 선언, hit target·clamp 규칙, focus-visible, 기존 spec 수정

## 작업 (TDD)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step43` → `python3 -I tests/scripts/design-intake-check.py`
2. `component-hover.spec.js`(`desktop-dark`·`desktop-light`만, 나머지 `test.skip`) 먼저 실패 확인: 대상 `.hero-cta .btn`(각각), 첫 `.featured-card`, `#projectGrid .project-card[data-project="0"]`마다 — `page.mouse.move(0, 0)` 후 default 측정 → `locator.hover()` 후 측정 → `page.mouse.down()` 상태 측정 → `page.mouse.up()`; 측정은 `document.getAnimations().length === 0`까지 poll한 뒤 `transform`·`opacity`·color·background-color·border-color·outline-color; hover와 active 각각에서 transform 또는 opacity가 default와 다르고 색 4속성은 default와 같음.
3. style.css(guard 통과).

## AC

- `python3 -I tests/scripts/design-intake-check.py && sh tests/scripts/with-env.sh npm --prefix tests test -- component-hover.spec.js component-hit.spec.js css-parse.spec.js design-guard-color.spec.js design-guard-css.spec.js design-guard.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step43.json --allow css/style.css,tests/specs/component-hover.spec.js --require-absent tests/specs/component-hover.spec.js` → exit 0
