# Step 40 — component-states

- 목적: component state(비색), 44px hit target, menu open(`mobile-dark`)·modal open(6 project) 측정, blurb line clamp, strength stripe 제거(선택).
- 예상 19분 / 선행 0~39 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §3, §16.2(component state 측정 요소·시점), §16.4(DESIGN_HASH_CHECK 후 `Components.dc.html`·`MobileMenu.dc.html` 읽기 전용); main.js 카드 blurb 요소(spec 상수 `CARD_BLURB`)
- tracked 허용(exact): `css/style.css`(상태·hit target·line clamp 비색 규칙과 `.strength-card::before` 규칙 삭제만), `tests/specs/component-states.spec.js`(신규)
- runtime: R0
- 금지: §15.7, `index.html`, `js/*`, 색 선언·색 역할 변경, focus-visible outline 변경

## 작업 (TDD)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step40` → `python3 -I tests/scripts/design-intake-check.py`
2. `component-states.spec.js` 먼저 실패 확인(측정은 상태 진입 후 `document.getAnimations().length === 0`까지 `expect.poll`한 뒤)
   - hit target(6 project): 그 project에서 기본 상태로 보이는 §16.2 대상 각각 bbox w·h ≥ tokens.hitTargetMinPx
   - hover·active(desktop-dark/light): `.hero-cta .btn`, `.featured-card`, `#projectGrid .project-card` 각각 hover, mouse down 상태에서 `transform` 또는 `opacity`가 default와 다르고 color·background-color·border-color·outline-color는 default와 같음
   - menu open(`mobile-dark`만, 나머지 `test.skip`): 설계 §16.2 menu open 절차 그대로
   - modal open(6 project): 설계 §16.2 modal open 절차 그대로
   - line clamp(6 project): `.featured-blurb`·`CARD_BLURB` computed `-webkit-line-clamp` `3`, textContent = `PROJECTS[i].blurb`(norm), `.modal-blurb` clamp 없음
   - strength: `.strength-card` 6개 텍스트 불변(stripe 유무 무관)
3. style.css(guard 통과).

## AC

- `python3 -I tests/scripts/design-intake-check.py && sh tests/scripts/with-env.sh npm --prefix tests test -- component-states.spec.js design-guard-css.spec.js design-guard.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step40.json --allow css/style.css,tests/specs/component-states.spec.js --require-absent tests/specs/component-states.spec.js` → exit 0
