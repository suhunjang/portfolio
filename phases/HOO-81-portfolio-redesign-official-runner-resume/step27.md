# Step 27: a11y-coupled-contrast-guard

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

Observation-linked coupled foreground/background guard only; no fixture write/token selection. Read exact map and `tests/fixtures/axe-contrast-base.json`. Recompute every effectiveTargetKey as an integrity check, then for each submitted observation state use its persisted foregroundChangeUnitIds/backgroundChangeUnitIds. Intersect those arrays with planned change-unit IDs; if at least one planned unit influences each side of the same observed contrast pair, stop coupled-contrast-change-unsupported before token selection, regardless of whether selectors, baseMapping strategies or effectiveTargetKeys differ. One-sided pairs pass. Reject missing/extra/unknown/duplicate observation links. Self-tests cover inherited foreground plus ancestor background under different selectors/strategies, same-key pair, each independent-pass/joint-fail, one-sided pass and link tamper. <=10 minutes.

## Exact write boundary
a11y-coupled-contrast-guard: tests/scripts/verify-a11y-remediation.mjs, tests/specs/verify-a11y-remediation.spec.js

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
