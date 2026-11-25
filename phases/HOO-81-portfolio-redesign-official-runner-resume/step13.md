# Step 13: a11y-evidence-contract

## Current authoritative contract
Always-on: preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata. Historical references are read-only context; only current index argv and current contract execute.

Evidence collect/schema contract only. Occurrence id is SHA-256 lowercase of UTF-8 `ruleId\0scenario\0project\0canonicalTarget`; canonicalTarget is trimmed target with internal ASCII whitespace collapsed and selectors sorted code-unit order. Evidence occurrences include id, ruleId, scenario, project, target, canonicalTarget, anchor, allowedFile, preStatus, postStatus. Reject ID mismatch, duplicate or missing inherited target. colorChanges exact fields are occurrenceId, theme, state, selector, property, from, to, tokenOrRole; derive from/to only from BASE and existing approved css/style.css token/role reaching >=4.5 in every linked scenario. Require every contrast occurrence linked once and reject unresolved pair/themes.css/index need. `collect` is deterministic fixture-only writer. Specs cover mapping, schema, conflicts and exact 25/139 counts. No browser/live verifier or remediation here.

## Exact write boundary
a11y-evidence: tests/scripts/verify-a11y-remediation.mjs, tests/specs/verify-a11y-remediation.spec.js, tests/fixtures/axe-remediation-plan.json, tests/fixtures/axe-remediation-evidence.json

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Run every immutable argv in index.json for this step in order. Nonzero blocks. emptyAllowed=false means each worker wave must produce its declared artifact/spec/source change; legacy no-op branches do not apply.
