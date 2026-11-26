# Step 43: final-fixture-transition

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

Actual tracked transition only after Steps41/42. Step43 worker writes only canonical `tests/fixtures/final-transition-ready.json`; worker-diff validation rejects every other path. Lane files include baseline/plan solely because Harness requires mutation targets there; worker treats them read-only. Detached acceptance is read-only, then Harness alone executes checks.mutation.command with exact targets and requireChanged, revalidates original 139 and empties both transactionally with rollback. <=12 minutes.

## Exact write boundary
final-transition: tests/fixtures/final-transition-ready.json, tests/fixtures/axe-baseline.json, tests/fixtures/axe-remediation-plan.json

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
