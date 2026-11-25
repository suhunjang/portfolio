# Step 35: final-fixture-transition

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

Fixture transition only. Step16 initially creates remediation plan. Worker lane never mutates baseline/plan: `prepare-transition-manifest` read-only validates regular original inputs, evidence SHA, complete zero scenarios and original 139 mapping, then writes only canonical `tests/fixtures/final-transition-ready.json` containing exact input hashes and expected empty-output hashes. Fan-in first validates that manifest and the still-nonempty submitted baseline/plan read-only, then runs exact `verify-transition`; any mismatch exits before mutation. Only then fan-in runs `prepare`, which revalidates the same hashes and atomically writes baseline `[]` and plan `{"groups":[]}`; final clean verification follows. The official acceptance mutation record must name only baseline and plan so Harness folds these two checked bytes into the accepted candidate. Any failure preserves both original bytes. Specs cover already-empty input, hash/occurrence mismatch, manifest tamper, mutation targetPaths, and rollback. No browser/screenshots.

## Exact write boundary
final-prepare: tests/scripts/verify-final-contract.mjs, tests/specs/final-contract.spec.js, tests/fixtures/final-transition-ready.json

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
