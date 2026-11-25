# Step 18: a11y-declaration-resolver-contract

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

CDP declaration-candidate collector implementation only. Export exact async collectDeclarationCandidates(page,{target,pseudoSelector=null}); target is `{selector:string,nth:integer>=0,expectedBackendNodeId:null|positive integer}` and pseudoSelector is null|::before|::after. Return exact `{targetIdentity,candidates}`; targetIdentity is `{selector,nth,backendNodeId,outerHTMLSha256}` and candidates is a stable code-unit-sorted array of exact `{property,resolvedValue,selector,sourceFile,startLine,startColumn,atRuleChain,specificity,sourceOrder,origin,important,matchedBackendNodeId,sourceBackendNodeId,inheritedDepth,active}` records for color/background-color from CDP matched and inherited evidence. This step does not choose a winner, extract scope, iterate occurrences or write fixtures. Self-tests independently cover direct/inherited/pseudo/at-rule/duplicate-selector collection, stable order, target identity and rejection of inline, UA, runtime/generated and non-css/style.css sources. <=12 minutes.

## Exact write boundary
a11y-declaration-resolver: tests/scripts/verify-a11y-remediation.mjs, tests/specs/verify-a11y-remediation.spec.js

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
