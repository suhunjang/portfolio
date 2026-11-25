# Step 19: a11y-observation-contract

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

Observation validation only atop steps17-18. Implement browser-free read-only verify-observation plus self-test-live integration. Observation has exactly: `schemaVersion` integer 1; `evidenceSha256` lowercase 64hex; `scenarios` equal the complete ordered expansion; `collectionPayload` object with exact keys `schemaVersion` integer 1 and `results` array in scenario order, each exact `{scenario:string,project:string,projectIndex:null|integer,color:integer,nested:integer,occurrenceIds:string[]}` with occurrenceIds sorted unique lowercase 64hex; and `collectionOutputSha256` lowercase 64hex. Canonical payload bytes are UTF-8 of recursive code-unit-sorted object keys, arrays preserved, JSON compact separators and no trailing newline; the hash is SHA-256 of exactly those bytes. Top-level counts are derived from payload and CLI expectations, never trusted fields. Validate evidence SHA, complete scenarios, counts, IDs and payload hash. Specs mutate one payload field while retaining the old SHA and separately mutate the SHA while retaining payload; both must fail, as do duplicate/missing/reordered scenarios. self-test-live proves lifecycle+scan+observation with an isolated fixture server. No mutation.

## Exact write boundary
a11y-observation-contract: tests/scripts/verify-a11y-remediation.mjs, tests/specs/verify-a11y-remediation.spec.js

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
