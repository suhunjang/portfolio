# Step 19: a11y-contrast-validation

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

Contrast completeness validation and canonical publication only. Read occurrence/map/measurement fixtures without browser. Published contrast BASE top-level keys are exactly `schemaVersion,mapSha256,measurementSha256,units`, schemaVersion=1 and hashes over exact submitted bytes. Units follow map order and are exactly `{changeUnitId,cssDeclaration,scope,occurrenceIds,candidateTokenNames,states}`; the first five fields copy the map and states copy the exact canonical measurement states. Canonical bytes use the named key/array order, compact UTF-8 JSON and one trailing LF. Require all 61 IDs exactly once; exact map/measurement schemas, unit mapping and requiredStates; every state carries exactly all candidateTokenNames with valid eligibility/reason pairs. Reject missing/extra/duplicate, split/overlap, incomplete state, candidate mismatch, an eligible invalid color or a unit with no candidate eligible in every required state; retain ineligible candidate records as evidence. Publish `tests/fixtures/axe-contrast-base.json` canonically. Lane writes; fan-in verify-contrast-base is read-only and validates submitted bytes before any generation. <=12 minutes.

## Exact write boundary
a11y-contrast-validation: tests/scripts/verify-a11y-remediation.mjs, tests/specs/verify-a11y-remediation.spec.js, tests/fixtures/axe-contrast-base.json

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
