# Step 46 — component-hit-open

- 목적: §11.2 측정 helper 신설, hit target·menu open·modal open·애니메이션 회귀, hit target CSS.
- 19분 / 선행 0~45 / 공통 §9 / gate GATE
- 허용(exact): `css/style.css`(대상의 비색 hit target 규칙만), `tests/helpers/component-state.js`(신규), `tests/specs/component-hit.spec.js`(신규)
- runtime: R0
- 추가 금지: `index.html`, `js/*`, 색 선언·순서, hover·active·clamp(49·50), 무한 장식 제거·변경, 문서 전체 `getAnimations()` 대기, 기존 spec

## 작업
1. `SNAP 46` → `DI`(`Components.dc.html`·`MobileMenu.dc.html` 읽기만).
2. helper = §11.2 `waitForFiniteAnimations`·`measureState`.
3. RED spec(측정은 `measureState`만): (a) desktop-dark에서 `.caret`(있으면)·`.scroll-hint span`에 Infinity·running 애니메이션 확인 상태로 `waitForFiniteAnimations(page, ['#hero', '.scroll-hint'], { timeoutMs: 5000 })` resolve·`measureState(page, '.hero-cta .btn')` 반환; (b) 300ms 유한 transition → 반환 시 `playState === 'finished'`; (c) 10초 유한 + `timeoutMs: 200` → 정확히 `animation-timeout:{selector}`; (d) 무한만 → 즉시 resolve; hit target(6 project) `.nav-link`(보이는 것), `#menuToggle`(보이면), `#themeToggle`, `.hero-cta .btn`, `.featured-card` 3, `#projectGrid .project-card` 13, `#contactActions a`(있으면), `.scroll-hint`(보이면) ≥ tokens.hitTargetMinPx; menu open·modal open = §11.2 step 46 절차.
4. style.css(guard 통과).

## AC
- `DI && T component-hit.spec.js GS && FULL && VS && GATE 46 css/style.css,tests/helpers/component-state.js,tests/specs/component-hit.spec.js tests/helpers/component-state.js,tests/specs/component-hit.spec.js`
