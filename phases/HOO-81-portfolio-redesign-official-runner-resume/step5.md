# Step 5: component-hit-targets

## Current authoritative contract
Always-on: preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata. Historical references are read-only context; only current index argv and current contract execute.

- Reference-only: `phases/HOO-81-portfolio-redesign-resume/step23.md`, SHA-256 `c55a549c8491d5c9b0f379325763284738364fd5cd1fa939886a8a897eca42f6`. Do **not** execute its legacy RSNAP/REQ/DI/RGATE/FULL/no-op commands; the current argv contract below replaces them.
### Current carried-forward requirements from historical boundary 23 (authoritative, not a command)
   - `existing`: 작업 2~4 생략, 쓰기 없는 AC 전체 실행 → 통과 시 `resume step23: no-op`, 실패 시 tracked 불변 중단·재계획.
   - `new`: 아래 진행. `branch-mixed`면 중단.
2. `DI`(`Components.dc.html`·`MobileMenu.dc.html` 읽기만). helper = 원 §11.2 `waitForFiniteAnimations`·`measureState`.
3. RED spec(측정은 `measureState`만): (a) desktop-dark에서 `.caret`(있으면)·`.scroll-hint span`에 Infinity·running 애니메이션 확인 상태로 `waitForFiniteAnimations(page, ['#hero', '.scroll-hint'], { timeoutMs: 5000 })` resolve·`measureState(page, '.hero-cta .btn')` 반환; (b) 300ms 유한 transition → 반환 시 `playState === 'finished'`; (c) 10초 유한 + `timeoutMs: 200` → 정확히 `animation-timeout:{selector}`; (d) 무한만 → 즉시 resolve; hit target(6 project) `.nav-link`(보이는 것), `#menuToggle`(보이면), `#themeToggle`, `.hero-cta .btn`, `.featured-card` 3, `#projectGrid .project-card` 13, `#contactActions a`(있으면), `.scroll-hint`(보이면) ≥ tokens.hitTargetMinPx; menu open·modal open = 원 §11.2 step 46 절차.
4. style.css(guard 통과).
Current contract: hit-target CSS/helper/spec, preserving internal links and modal delegation. No-op forbidden.

## Exact write boundary
component-hit: css/style.css, tests/helpers/component-state.js, tests/specs/component-hit.spec.js

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Run every immutable argv in index.json for this step in order. Nonzero blocks. emptyAllowed=false means each worker wave must produce its declared artifact/spec/source change; legacy no-op branches do not apply.
