# Step 6: state-sequence

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

- Reference-only: `phases/HOO-81-portfolio-redesign-resume/step24.md`, SHA-256 `628ce602b7be6eb93b1e1a3ada5e519839cbc7bb69974343c1254cfa9b9923d4`. Do **not** execute its legacy RSNAP/REQ/DI/RGATE/FULL/no-op commands; the current argv contract below replaces them.
### Current carried-forward requirements from historical boundary 24 (authoritative, not a command)
2. RED spec(`desktop-dark`·`desktop-light`, 나머지 skip; §THEME `test`의 `context`, url `/`; 각 test 정확히 `test.setTimeout(60000)`): 반환 6필드×3상태; 호출마다 `context.on('page')` 1회·pages 수 동일; 측정 page `html[data-theme]` = project suffix; 격리 (a) grid 0 → 1, 두 번째 `beforeMeasure`에서 `#projectModal` hidden·`modal-open` 없음; (b) `.hero-cta .btn` 0 뒤 `location.hash === ''`·`scrollY === 0`; (c) `beforeMeasure`에서 `page.setDefaultTimeout(500)` + 없는 selector → reject·pages 원복·이어 정상 측정 성공; (d) `beforeMeasure` throw → 같은 오류·pages 동일; (e) `page.setDefaultTimeout(500)` 후 pointerdown 제거 listener → reject·pages 원복·이어 정상 측정 성공.
Current contract: export `async function measureStateSequence(context, {url='/', selector, nth=0, beforeMeasure=null})`. It returns exactly `{default, hover, active}`, each value the six style fields `color, backgroundColor, borderColor, outlineColor, transform, opacity` plus `box` from measureState. Fixed order: newPage→goto→fonts.ready→beforeMeasure→scrollIntoView→finite wait→mouse(0,0) default→hover→pointerdown active→pointerup; always close the one new page in finally, remove listeners, and leave context page count unchanged. Theme comes only from the supplied context init script. Failures propagate unchanged and cleanup still runs. No product writes; no-op forbidden.

## Exact write boundary
state-sequence: tests/helpers/state-sequence.js, tests/specs/state-sequence.spec.js

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs are deterministically fanned in and committed, the official runner runs this step's index.json `acceptanceCommands` exactly once. Legacy no-op branches do not apply.
