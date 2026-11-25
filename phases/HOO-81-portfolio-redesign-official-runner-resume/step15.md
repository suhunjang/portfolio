# Step 15: a11y-evidence-contract

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

Evidence collect/schema contract only. Occurrence id is SHA-256 lowercase of UTF-8 `ruleId\0scenario\0project\0canonicalTarget`; canonicalTarget is trimmed target with internal ASCII whitespace collapsed and selectors sorted code-unit order. Evidence occurrences include id, ruleId, scenario, project, target, canonicalTarget, anchor, allowedFile, preStatus, postStatus. Reject ID mismatch, duplicate or missing inherited target. colorChanges exact fields are occurrenceId, theme, state, selector, property, from, to, tokenOrRole; derive from/to only from BASE and existing approved css/style.css token/role reaching >=4.5 in every linked scenario. Require every contrast occurrence linked once and reject unresolved pair/themes.css/index need. `collect` is deterministic fixture-only writer. Specs cover mapping, schema, conflicts and exact 25/139 counts. No browser/live verifier or remediation here.

## Exact write boundary
a11y-evidence: tests/scripts/verify-a11y-remediation.mjs, tests/specs/verify-a11y-remediation.spec.js, tests/fixtures/axe-remediation-plan.json, tests/fixtures/axe-remediation-evidence.json

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
