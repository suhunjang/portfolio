# Step 5: component-hit-targets

## Always-on invariants
Do not modify historical phase records/evidence. Preserve all copy, numbers, font assets/weights, information architecture, 3 featured project identities, all 13 PROJECTS and order. No new copy, section, image, icon, project or placeholder content. css/themes.css is read-only; if it or index.html is required outside the listed lane, stop and replan. Implementation workers must not commit, push, merge, edit the canonical phase index, or write outside their exact lane files. Run only focused tests in lanes; canonical FULL/UI/a11y run at steps 12 and 14.

## Exact work order
### Bound historical contract: `phases/HOO-81-portfolio-redesign-resume/step23.md`
SHA-256 `c55a549c8491d5c9b0f379325763284738364fd5cd1fa939886a8a897eca42f6`

# Resume Step 23 — component-hit-open (원 step 46, §R10 분기)

- 목적: 원 §11.2 측정 helper 신설, hit target·menu open·modal open·애니메이션 회귀, hit target CSS.
- 19분 / 선행 0~22 / 공통 원 §9 + §R1·§R10 / gate `RGATE_B 23`
- 허용(exact): `css/style.css`(대상의 비색 hit target 규칙만), `tests/helpers/component-state.js`(신규), `tests/specs/component-hit.spec.js`(신규)
- 분기 R: `tests/helpers/component-state.js,tests/specs/component-hit.spec.js`
- runtime: R0
- 추가 금지: `index.html`, `js/*`, 색 선언·순서, hover·active·clamp(resume 26·27), 무한 장식 제거·변경, 문서 전체 `getAnimations()` 대기, 기존 spec, start snapshot 수정·재생성, existing 분기에서 R 파일 수정

## 작업
1. `RSNAP 23` → `RBRANCH 23 tests/helpers/component-state.js,tests/specs/component-hit.spec.js`.
   - `existing`: 작업 2~4 생략, 쓰기 없는 AC 전체 실행 → 통과 시 `resume step23: no-op`, 실패 시 tracked 불변 중단·재계획.
   - `new`: 아래 진행. `branch-mixed`면 중단.
2. `DI`(`Components.dc.html`·`MobileMenu.dc.html` 읽기만). helper = 원 §11.2 `waitForFiniteAnimations`·`measureState`.
3. RED spec(측정은 `measureState`만): (a) desktop-dark에서 `.caret`(있으면)·`.scroll-hint span`에 Infinity·running 애니메이션 확인 상태로 `waitForFiniteAnimations(page, ['#hero', '.scroll-hint'], { timeoutMs: 5000 })` resolve·`measureState(page, '.hero-cta .btn')` 반환; (b) 300ms 유한 transition → 반환 시 `playState === 'finished'`; (c) 10초 유한 + `timeoutMs: 200` → 정확히 `animation-timeout:{selector}`; (d) 무한만 → 즉시 resolve; hit target(6 project) `.nav-link`(보이는 것), `#menuToggle`(보이면), `#themeToggle`, `.hero-cta .btn`, `.featured-card` 3, `#projectGrid .project-card` 13, `#contactActions a`(있으면), `.scroll-hint`(보이면) ≥ tokens.hitTargetMinPx; menu open·modal open = 원 §11.2 step 46 절차.
4. style.css(guard 통과).

## AC
- `DI && T component-hit.spec.js GS && FULL && VS && RGATE_B 23 css/style.css,tests/helpers/component-state.js,tests/specs/component-hit.spec.js tests/helpers/component-state.js,tests/specs/component-hit.spec.js`


Own exact component hit-target anchors, `tests/helpers/component-state.js`, and its spec. Preserve internal link behavior and modal delegation.

## Exact write boundary
component-hit: css/style.css, tests/helpers/component-state.js, tests/specs/component-hit.spec.js

## Acceptance
Run every argv in this step’s immutable `index.json.acceptanceCommands` in order. Any nonzero exit blocks the next step.
