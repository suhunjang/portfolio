# Step 15: a11y-occurrence-contract

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

Occurrence collection and schema contract only. Normalize inherited pairs into exact 139 occurrences and write `tests/fixtures/axe-remediation-occurrences.json` plus the remediation-plan groups; do not derive colorChanges here. Occurrence id is SHA-256 lowercase of UTF-8 `ruleId\0scenario\0project\0canonicalTarget`; canonicalTarget trims and collapses ASCII whitespace and sorts selectors in code-unit order. Exact fields are id, ruleId, scenario, project, target, canonicalTarget, anchor, allowedFile, preStatus, postStatus. Reject ID mismatch, duplicate/missing inherited targets, new rules and wrong exact 25 pair/139 occurrence/61 color/78 nested counts. Fixture-only, <=14 minutes, no browser or contrast calculation.

## Exact write boundary
a11y-occurrence: tests/scripts/verify-a11y-remediation.mjs, tests/specs/verify-a11y-remediation.spec.js, tests/fixtures/axe-remediation-plan.json, tests/fixtures/axe-remediation-occurrences.json

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
