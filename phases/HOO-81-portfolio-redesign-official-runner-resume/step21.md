# Step 21: a11y-scope-role-extractor-contract

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

Scope/DOM-role extractor only. Consume exact Step20 winner result and never re-run cascade. Return exact `{scope,roleMetadata}`. scope is `{mediaQueries:string[],themeSelectors:string[],pseudoSelectors:string[],projectScoped:boolean}` and canonical SHA-256 must equal sourceIdentity.scopeHash. roleMetadata is `{role,projectRootSelector,relativeSelector,pseudoSelector}`. Root precedence lightbox > modal > project. Fixed roots: `body > .lightbox`, `#projectModal > .modal-dialog`, `#heroFeatured > .featured-card:nth-of-type(k)`, `#projectGrid > .project-card:nth-of-type(k)`. Project root versus strict descendants is exact; overlays require strict descendants; no root means same-selector. relativeSelector is ordered per-edge `:scope > tag:nth-of-type(k)` and replay-identical. Fail ambiguity/replay/identity. Tests cover all roots and Step23 round-trip. <=10 minutes.

## Exact write boundary
a11y-scope-role-extractor: tests/scripts/verify-a11y-remediation.mjs, tests/specs/verify-a11y-remediation.spec.js

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
