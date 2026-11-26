# Step 17: a11y-current-browser-mapping-lifecycle

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

Current-working-tree mapping lifecycle and scenario preparation only. Export exactly `async function withCurrentMappingBrowser({serverRoot='.',port=4188,tempRoot=process.env.TMPDIR},callback)` and `prepareCurrentScenario(page,{scenarioKind,viewport,theme,projectIndex,state})`. The lifecycle owns one UUID root/server/browser, rejects occupied port/symlinks, returns callback result unchanged and always cleans only owned resources. prepareCurrentScenario implements the exact ten-scenario order and default/hover/active state setup without reading BASE. Import is side-effect free. Focused tests cover both signatures, all scenarios/states, error propagation and cleanup. No fixture writes or declaration mapping. <=10 minutes.

## Exact write boundary
a11y-current-mapping-lifecycle: tests/scripts/verify-a11y-remediation.mjs, tests/specs/verify-a11y-remediation.spec.js

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
