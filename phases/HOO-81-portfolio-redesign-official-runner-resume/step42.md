# Step 42: final-fixture-transition

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

Actual tracked transition only after Steps40/41. The Step42 worker command validates originals and writes only canonical `tests/fixtures/final-transition-ready.json`; worker diff validation requires exactly that one path and rejects script/spec/baseline/plan worker changes. Harness 2.0.1 lint requires mutation targetPaths to appear in lane files, so lane files declare manifest plus baseline/plan, but baseline/plan are reserved exclusively for checks.mutation and the worker command is contractually read-only for them; script/spec are excluded because implementation completed earlier. Detached acceptance runs only read-only manifest check, then Harness executes the destructive command solely as checks.mutation.command with exact targetPaths, forbiddenPaths=[], requireChanged=true. It revalidates summed original 139 target pairs and transactionally empties baseline/plan with rollback; no duplicate or later fallible repository command. <=12 minutes.

## Exact write boundary
final-transition: tests/fixtures/final-transition-ready.json, tests/fixtures/axe-baseline.json, tests/fixtures/axe-remediation-plan.json

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
