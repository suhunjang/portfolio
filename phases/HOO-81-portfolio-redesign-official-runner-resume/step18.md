# Step 18: a11y-declaration-resolver-contract

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

CDP declaration collector core only. Export exact async collectDeclarationCore(page,{target}); target is `{selector:string,nth:integer>=0,expectedBackendNodeId:null|positive integer}`. Return exact `{targetIdentity,coreCandidates}`; targetIdentity is `{selector,nth,backendNodeId,outerHTMLSha256}` and coreCandidates is code-unit sorted exact `{property,selector,sourceFile,startLine,startColumn,specificity,sourceOrder,origin,important,matchedBackendNodeId,sourceBackendNodeId,inheritedDepth,active}` for direct and inherited color/background-color declarations on the non-pseudo target. Validate target once, direct/inherited source coordinates, specificity/source order and target identity; reject inline/UA/runtime/non-css/style.css sources. Independent self-tests cover direct, inherited, duplicate selector text, target schema/identity, stable ordering and failures. No pseudo, at-rule/scope normalization, authored/computed enrichment, winner, role, full traversal or fixture write. <=12 minutes.

## Exact write boundary
a11y-declaration-resolver: tests/scripts/verify-a11y-remediation.mjs, tests/specs/verify-a11y-remediation.spec.js

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
