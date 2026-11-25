# Step 41: final-transition-transaction-contract

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

Transactional commit implementation only. Implement commit-fixture-transition and self-test exclusively on process-owned temporary copies. The exact self-test argv uses --prepare-manifest-in-temp --temp-root-env TMPDIR, not tracked final-transition-ready.json: inside the owned temp root it invokes the Step40 prepare-manifest implementation on temp baseline/plan/evidence/zero data, then injects validation, first/second rename, file/directory fsync and cleanup failures and proves both original byte sequences restored/fsynced. It must succeed when tracked manifest is absent and must not create or modify any tracked manifest/baseline/plan. <=10 minutes.

## Exact write boundary
final-transition-transaction-contract: tests/scripts/verify-final-contract.mjs, tests/specs/final-contract.spec.js

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
