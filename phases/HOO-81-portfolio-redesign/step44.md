# Step 44 — component-hit-open

- 목적: 대상 한정 애니메이션 대기·측정 helper 신설, 44px hit target(6 project), mobile menu open(`mobile-dark`), modal open(6 project) 측정과 hit target CSS.
- 예상 19분 / 선행 0~43 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §3(무한 장식 애니메이션), §16.2(component state 측정 helper·대상·step 44 절차), §16.4(DESIGN_HASH_CHECK 후 `Components.dc.html`·`MobileMenu.dc.html` 읽기 전용); fixture tokens
- tracked 허용(exact): `css/style.css`(§16.2 대상의 min-width·min-height·padding·line-height·display 등 비색 hit target 규칙만), `tests/helpers/component-state.js`(신규), `tests/specs/component-hit.spec.js`(신규)
- runtime: R0
- 금지: §15.7, `index.html`, `js/*`, 색 선언(기존 규칙에 추가 포함), hover·active·clamp 규칙(step 45·46), 무한 장식 애니메이션 제거·변경, 문서 전체 `document.getAnimations()` 대기, 기존 spec 수정

## 작업 (TDD)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step44` → `python3 -I tests/scripts/design-intake-check.py`
2. `component-state.js`: 설계 §16.2 `waitForFiniteAnimations(page, selectors, { timeoutMs = 5000 })`(대상·subtree의 `getAnimations({ subtree: true })` 중 `iterations !== Infinity`이고 `playState`가 `running`·`pending`인 것만 `finished` 대기, 취소 reject는 완료로 처리, 초과 시 `Error('animation-timeout:{selector}')`)와 `measureState(page, selector, { nth = 0 })`(먼저 대기 후 `{ color, backgroundColor, borderColor, outlineColor, transform, opacity, box }`).
3. `component-hit.spec.js` 먼저 실패 확인(상태 측정은 `measureState`만 사용)
   - helper 회귀: (a) 실제 사이트 desktop-dark에서 `.caret`(있으면)과 `.scroll-hint span`에 `iterations === Infinity`이고 `playState === 'running'`인 애니메이션이 있음을 확인한 상태로 `waitForFiniteAnimations(page, ['#hero', '.scroll-hint'], { timeoutMs: 5000 })`가 resolve되고 `measureState(page, '.hero-cta .btn')`가 값을 반환; (b) `setContent` 합성에서 300ms 유한 transition을 시작한 요소 → helper 반환 시 그 animation `playState === 'finished'`; (c) 10초 유한 animation + `timeoutMs: 200` → 정확히 `animation-timeout:{selector}`; (d) 무한 animation만 있는 요소 → 즉시 resolve
   - hit target(6 project): `.nav-link`(그 project에서 기본 상태로 보이는 것만), `#menuToggle`(보이면), `#themeToggle`, `.hero-cta .btn` 각각, `.featured-card` 3개, `#projectGrid .project-card` 13개, `#contactActions a`(있으면), `.scroll-hint`(보이면)의 bbox width·height ≥ tokens.hitTargetMinPx
   - menu open(`mobile-dark`만, 다른 project는 `test.skip`): 설계 §16.2 step 44 menu open 절차 그대로
   - modal open(6 project): 설계 §16.2 step 44 modal open 절차 그대로
4. style.css(guard 통과).

## AC

- `python3 -I tests/scripts/design-intake-check.py && sh tests/scripts/with-env.sh npm --prefix tests test -- component-hit.spec.js css-parse.spec.js color-vocab.spec.js design-guard-color-rules.spec.js design-guard-color.spec.js design-guard-css.spec.js design-guard.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step44.json --allow css/style.css,tests/helpers/component-state.js,tests/specs/component-hit.spec.js --require-absent tests/helpers/component-state.js,tests/specs/component-hit.spec.js` → exit 0
