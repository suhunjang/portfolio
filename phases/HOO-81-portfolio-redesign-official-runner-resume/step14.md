# Step 14: a11y-live-verifier-contract

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

Live verifier CLI contract only, using frozen evidence from step13. Implement verify-lane, verify-full, verify-observation and self-test-live. Each live invocation binds server root to its current worktree realpath, requires its PW_PORT to be free, starts its own server/browser, refuses an existing server even if responsive, and kills only its recorded child PID/process group in finally. verify-lane expands evidence scenarios, requires owned=0 and exact non-owned IDs, writes nothing and prints JSON. verify-full requires both zero, supports exactly one of write-observation or observation-stdout, rejects new rules and writes only the declared observation. verify-observation is browser-free read-only schema/hash/count/scenario validation. Setup/browser error exit2, validation exit1, success0. Tests cover ports 4175/4176 isolation, occupied-port refusal, cross-worktree root mismatch, child-only cleanup, new rule, missing scenario, duplicate ID and no-write behavior.

## Exact write boundary
a11y-verifier: tests/scripts/verify-a11y-remediation.mjs, tests/specs/verify-a11y-remediation.spec.js

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Run every immutable argv in index.json for this step in order. Nonzero blocks. emptyAllowed=false means each worker wave must produce its declared artifact/spec/source change; legacy no-op branches do not apply.
