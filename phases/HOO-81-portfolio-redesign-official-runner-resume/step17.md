# Step 17: a11y-change-unit-mapping

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

Change-unit mapping only, no browser. From inherited 61 color occurrence IDs and css/style.css, map each to `changeUnitId = SHA-256(selector+'\0'+property+'\0'+cssDeclaration+'\0'+scope)`. Scope is exact existing declaration applicability. Write `tests/fixtures/axe-contrast-change-units.json` with exact unit schema `{changeUnitId,selector,property,cssDeclaration,scope,occurrenceIds,requiredStates}`; occurrenceIds and requiredStates are sorted, and all occurrences sharing declaration/scope are one unit. Lane writes; fan-in runs verify-change-units read-only first. Specs cover selector/declaration/scope resolution and split/overlap rejection. No browser/token resolution. <=12 minutes.

## Exact write boundary
a11y-change-unit-map: tests/scripts/verify-a11y-remediation.mjs, tests/specs/verify-a11y-remediation.spec.js, tests/fixtures/axe-contrast-change-units.json

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
