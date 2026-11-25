# Step 13: a11y-evidence-contract

## Current authoritative contract
Always-on: preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata. Historical references are read-only context; only current index argv and current contract execute.

Evidence and verifier CLI contract. Occurrence id is SHA-256 lowercase of UTF-8 `ruleId\0scenario\0project\0canonicalTarget`; canonicalTarget is trimmed target with internal ASCII whitespace collapsed and selectors sorted code-unit order. Evidence occurrence fields include id plus ruleId/scenario/project/target/canonicalTarget/anchor/allowedFile/preStatus/postStatus. Reject ID mismatch, duplicate ID, missing inherited target or coverage mismatch. colorChanges are finalized here before evidence freeze: each exact field is occurrenceId, theme, state, selector, property, from, to, tokenOrRole; derive from/to only from BASE computed value and an existing approved css/style.css token/role that reaches >=4.5 contrast in every linked scenario; never sample future DOM. Require every contrast occurrence linked once, sorted unique; reject unresolved pair and themes.css/index need. Implement all CLI subcommands now: collect is deterministic fixture-only writer; verify-lane starts one server/browser lifecycle, expands evidence scenarios, measures live axe, requires owned=0 and exact non-owned IDs, writes nothing, prints JSON then exit0/1; verify-full same lifecycle requires both zero, supports exactly one of `--write-observation path` or `--observation-stdout`, rejects new rules and writes only declared observation; verify-observation is browser-free read-only schema/hash/count/scenario validation. Any setup/browser error exits2; validation failure exits1; success exit0. Specs include positive and new-rule, missing-scenario, duplicate-ID, write-side-effect and cleanup failures. No remediation or guard implementation here.

## Exact write boundary
a11y-evidence: tests/scripts/verify-a11y-remediation.mjs, tests/specs/verify-a11y-remediation.spec.js, tests/fixtures/axe-remediation-plan.json, tests/fixtures/axe-remediation-evidence.json

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Run every immutable argv in index.json for this step in order. Nonzero blocks. emptyAllowed=false means each worker wave must produce its declared artifact/spec/source change; legacy no-op branches do not apply.
