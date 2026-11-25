# Step 8: state-color-base-lifecycle

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

BASE archive/server lifecycle only. Export exactly async withBaseArchiveBrowser({baseRef,serverRoot='.',port,tempRoot=process.env.TMPDIR},callback) with process-owned UUID archive/server/browser and scoped cleanup. Actual BASE-browser consumers are Steps9,23,24,25 and29, each of which must import/call this exact export; Steps22 and28 are explicitly browser-free fixture consumers and must not call it. Tests prove signature, import side-effect freedom, callback values/result/error, symlink/occupied-port rejection and scoped cleanup. <=20 minutes.

## Exact write boundary
state-color-base-lifecycle: tests/scripts/make-state-colors.mjs, tests/specs/state-colors.spec.js

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
