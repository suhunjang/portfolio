# Step 40: final-transition-manifest-contract

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

Transition-manifest implementation only. Implement prepare-transition-manifest and verify-transition-manifest plus exact option `--expect-worker-diff-only <repo-relative-path>`. After atomically writing the requested manifest, that option obtains the worker worktree diff paths using `git status --porcelain=v1 -z --untracked-files=all`, parses NUL-delimited records including rename two-path records, normalizes safe repo-relative paths and requires the changed path set exactly equals the one argument; any script/spec/baseline/plan/extra path fails before success. Self-tests use a temporary git repo and cover only-manifest success, tracked modification, untracked extra, rename, spaces and malformed/unsafe paths. Existing manifest hash/original-139/schema/tamper tests remain process-owned temp only. Do not write tracked manifest or mutate baseline/plan in this implementation wave. Step42 may invoke this already-implemented option while owning only the manifest. <=8 minutes.

## Exact write boundary
final-transition-manifest-contract: tests/scripts/verify-final-contract.mjs, tests/specs/final-contract.spec.js

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
