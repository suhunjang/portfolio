# Step 28: a11y-observation-contract

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

Observation validation atop completed steps26-27. Implement browser-free read-only verify-observation plus self-test-live and prove this now-existing observation consumer calls the exact step27 expandScenarios helper. Observation has exactly schemaVersion, evidenceSha256, scenarios, collectionPayload, collectionOutputSha256; results are in exact helper order with sorted unique IDs. Canonical payload uses recursive code-unit-sorted object keys, preserved arrays, compact UTF-8 JSON and SHA-256. Validate evidence SHA, complete scenarios, counts, IDs and payload hash; payload/SHA tamper and duplicate/missing/reordered scenarios fail. Do not test future step32/36 consumers here. No mutation.

## Exact write boundary
a11y-observation-contract: tests/scripts/verify-a11y-remediation.mjs, tests/specs/verify-a11y-remediation.spec.js

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
