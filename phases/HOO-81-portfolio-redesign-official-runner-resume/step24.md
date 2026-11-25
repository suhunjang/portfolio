# Step 24: a11y-contrast-base-target-observation

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

BASE observation only. Execute baseProjectRootSelector/baseRelativeSelector and require one role-preserving BASE target. Featured mappings are root-only: PROJECTS 1/5/7 must resolve uniquely to BASE grid cards at nth projectIndex+1; a featured descendant is rejected upstream and is also rejected here as `featured-descendant-unmapped`. State exact `{occurrenceId,baseMapping,foreground,background,changedPropertyBase,backgroundReplacementMode,foregroundChangeUnitIds,backgroundChangeUnitIds}`. backgroundReplacementMode is null for color; background-color permits only `direct-opaque`, where changed source is opaque and every layer from target to source exclusive has alpha 0. Semi-transparent/multiple nontransparent layers or image/blend/filter stop `unsupported-background-layered-change`. Tests cover three featured root successes, synthetic featured descendant rejection, transparent chain success and semi-transparent child over ancestor failure. <=20 minutes.

## Exact write boundary
a11y-contrast-target: tests/scripts/verify-a11y-remediation.mjs, tests/specs/verify-a11y-remediation.spec.js, tests/fixtures/axe-contrast-base-targets.json

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
