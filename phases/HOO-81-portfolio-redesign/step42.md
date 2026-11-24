# Step 42 — component-hit-open

- 목적: 44px hit target(6 project), mobile menu open(`mobile-dark`), modal open(6 project) 측정과 hit target CSS.
- 예상 18분 / 선행 0~41 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §3, §16.2(component state 대상·측정 시점·step 42 절차), §16.4(DESIGN_HASH_CHECK 후 `Components.dc.html`·`MobileMenu.dc.html` 읽기 전용); fixture tokens
- tracked 허용(exact): `css/style.css`(§16.2 대상의 min-width·min-height·padding·line-height·display 등 비색 hit target 규칙만), `tests/specs/component-hit.spec.js`(신규)
- runtime: R0
- 금지: §15.7, `index.html`, `js/*`, 색 선언, hover·active·clamp 규칙(step 43·44), 기존 spec 수정

## 작업 (TDD)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step42` → `python3 -I tests/scripts/design-intake-check.py`
2. `component-hit.spec.js` 먼저 실패 확인(측정은 상태 진입 후 `document.getAnimations().length === 0`까지 `expect.poll`한 뒤)
   - hit target(6 project): `.nav-link`(그 project에서 기본 상태로 보이는 것만), `#menuToggle`(보이면), `#themeToggle`, `.hero-cta .btn` 각각, `.featured-card` 3개, `#projectGrid .project-card` 13개, `#contactActions a`(있으면), `.scroll-hint`(보이면)의 bbox width·height ≥ tokens.hitTargetMinPx
   - menu open(`mobile-dark`만, 다른 project는 `test.skip`): 설계 §16.2 step 42 menu open 절차 그대로(열기 전 `#menuToggle` color·background-color·border-color 측정 → click → `aria-expanded="true"`·`#navLinks.open` → 보이는 `.nav-link` 각각 bbox ≥ 44px → toggle 색 3속성 동일 → 다시 click → `aria-expanded="false"`)
   - modal open(6 project): 설계 §16.2 step 42 modal open 절차 그대로(`#projectGrid .project-card[data-project="0"]` 색 3속성 측정 → click → body `modal-open`·`#projectModal` visible → `#projectModal .modal-close` bbox ≥ 44px → button 닫기 → `modal-open` 해제 후 카드 색 3속성 동일)
3. style.css(guard 통과).

## AC

- `python3 -I tests/scripts/design-intake-check.py && sh tests/scripts/with-env.sh npm --prefix tests test -- component-hit.spec.js css-parse.spec.js design-guard-color.spec.js design-guard-css.spec.js design-guard.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step42.json --allow css/style.css,tests/specs/component-hit.spec.js --require-absent tests/specs/component-hit.spec.js` → exit 0
