# Step 8: state-color-base-lifecycle

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

- Reference-only: `phases/HOO-81-portfolio-redesign-resume/step25.md`, SHA-256 `edb28b425da2a3353701514f14f2cb0cff41508eb1f98f13c85d43ac83cf4038`. Do **not** execute its legacy RSNAP/REQ/DI/RGATE/FULL/no-op commands; the current argv contract below replaces them.
### Current carried-forward requirements from historical boundary 25 (authoritative, not a command)

Current contract: BASE archive/server lifecycle only. Export exactly `async function withBaseArchiveBrowser({baseRef, serverRoot='.', port, tempRoot=process.env.TMPDIR}, callback)`. It validates baseRef/paths/port, creates process-owned UUID below `<tempRoot>/hoo-103-state-colors`, materializes `git archive baseRef`, starts one child process group and browser, then awaits `callback({archiveRoot, baseUrl, browser, childPid, processGroupId})`. It returns callback result unchanged; callback/start/setup errors propagate unchanged after finally cleanup. Finally closes browser, kills only recorded child/group and removes only owned UUID. Module import never runs CLI; CLI entry executes only when `import.meta.url === pathToFileURL(process.argv[1]).href`. Steps9,18 and21 import and call this exact export; no internal alternative is allowed. Specs prove signature, import side-effect freedom, callback values/result/error, symlink/occupied-port rejection and scoped cleanup. <=12 minutes.

## Exact write boundary
state-color-base-lifecycle: tests/scripts/make-state-colors.mjs, tests/specs/state-colors.spec.js

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
