# Step 10: state-color-base-transaction

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

BASE fixture transaction only. Read immutable `tests/fixtures/component-state-colors.candidate.json` and atomically publish byte-identical canonical bytes to `tests/fixtures/component-state-colors.base.json` and `tests/fixtures/component-state-colors.json` as one rollback-safe transaction; `--check` is read-only and requires candidate/base/working byte equality. Lane runs publish then check; fan-in acceptance runs check first and never publish, so bad submitted bytes are not regenerated away. Inject failure after each temporary write and rename and prove both destination bytes roll back exactly. The BASE fixture becomes permanently immutable after this step; only `tests/fixtures/component-state-colors.json` changes later at the dedicated post-remediation writer. No browser, measurement, CSS or candidate generation. <=12 minutes.

## Exact write boundary
state-color-base-transaction: tests/scripts/make-state-colors.mjs, tests/fixtures/component-state-colors.base.json, tests/fixtures/component-state-colors.json, tests/specs/state-colors.spec.js

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
