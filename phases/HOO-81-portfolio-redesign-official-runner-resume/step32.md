# Step 32: state-color-remediation-apply-contract

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

Remediation apply/check implementation only, consuming validated `tests/fixtures/component-state-colors.remediation-expected.json` from Step31. Strict `approved-remediation-apply` implements atomic `--write`, read-only `--check`, and `--self-test-atomic-live`. This step's lane and fan-in run only self-test against process-owned temporary fixture/server data: inject each temp-write/rename/live-DOM/setup failure, prove prior bytes preserved and unrelated files/processes untouched, and prove check detects fixture or live mismatch. It does not mutate tracked `tests/fixtures/component-state-colors.json` yet. Actual tracked write/check runs only at the dedicated post-remediation expectation step after product remediation. <=14 minutes.

## Exact write boundary
state-color-remediation-apply: tests/scripts/make-state-colors.mjs, tests/specs/state-colors.spec.js

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
