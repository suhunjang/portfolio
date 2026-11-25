# Step 17: final-artifact-preparation

## Current authoritative contract
Always-on: preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata. Historical references are read-only context; only current index argv and current contract execute.

Single-owner final-artifact lane. Verify `tests/fixtures/axe-zero-observation.json` and preserved `tests/fixtures/axe-remediation-evidence.json` before the worker prepare command alone sets baseline [] and plan groups[]. This worker is the only writer of those fixtures and also implements screenshots/final-contract verification. No later mutation reruns prepare.

## Exact write boundary
final-artifacts: tests/fixtures/axe-baseline.json, tests/fixtures/axe-remediation-plan.json, tests/specs/screenshots.spec.js, tests/scripts/verify-final-contract.mjs, tests/specs/final-contract.spec.js

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Run every immutable argv in index.json for this step in order. Nonzero blocks. emptyAllowed=false means each worker wave must produce its declared artifact/spec/source change; legacy no-op branches do not apply.
