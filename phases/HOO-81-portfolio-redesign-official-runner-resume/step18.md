# Step 18: a11y-declaration-resolver-contract

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

Declaration resolver and scope-extractor implementation only. Import Step17 current-browser lifecycle/scenario preparation. Implement one-target `resolveAuthoredDeclaration(page,target,property)` and `extractDeclarationScope(...)` that determine the actual CSS-cascade winner from CDP matched styles, require one active non-overridden css/style.css declaration, and return exact normalized cssDeclaration/scope plus DOM role metadata. Role metadata is exactly `{role,projectRootSelector,relativeSelector,pseudoSelector}`: role one of same-selector/project-root/project-descendant/modal-descendant/lightbox-descendant; relativeSelector is null or the browser-observed deterministic `:scope > tag:nth-of-type(k)` ancestry from the matched project/overlay root; pseudoSelector is null or exact pseudo. Focused self-test uses single synthetic targets for direct, inherited, shared selector, at-rule, theme, pseudo and nested descendant cases; it does not iterate occurrence fixture or write any fixture. <=20 minutes.

## Exact write boundary
a11y-declaration-resolver: tests/scripts/verify-a11y-remediation.mjs, tests/specs/verify-a11y-remediation.spec.js

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
