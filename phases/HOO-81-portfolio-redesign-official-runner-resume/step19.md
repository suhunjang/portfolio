# Step 19: a11y-color-derivation

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

ColorChanges derivation only, after validated contrast BASE. Exact 61 remains inherited classification, but selection is per `changeUnitId`, not per occurrence. For each change unit, candidate set is existing tokens whose state-specific resolvedColor yields WCAG2 >=4.5 in every linked state for every occurrence in that unit. Sum squared 8-bit sRGB distance to each member's BASE changed-property value; choose minimum sum, then code-unit token name. Emit one unit decision plus colorChanges entries for every occurrenceId, all sharing the same token/declaration decision. Reject any unit split, multiple tokens for one declaration/scope, incomplete member, new literal or themes.css need; no candidate stops `color-scope-themes-required`. Specs cover shared declarations across scenarios/themes, conflict rejection, distance/tie and no-candidate stop. <=14 minutes.

## Exact write boundary
a11y-color-derive: tests/scripts/verify-a11y-remediation.mjs, tests/specs/verify-a11y-remediation.spec.js, tests/fixtures/axe-remediation-evidence.json

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
