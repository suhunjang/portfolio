# Step 18: a11y-contrast-validation

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

Contrast completeness validation and canonical publication only. Read `tests/fixtures/axe-remediation-occurrences.json` and `tests/fixtures/axe-contrast-measurements.json` without browser work. Require all 61 color occurrence IDs exactly once across change units; every occurrence sharing selector/property/cssDeclaration/scope must be in the same unit; unit occurrenceIds and linkedStates are sorted and complete; each linked state carries scenario/project/projectIndex/theme/state/foreground/background plus every candidate token's state-specific resolvedColor. Reject missing/extra/duplicate occurrence, split/overlapping shared declaration, incomplete state coverage, alpha/unresolved colors, CSS declaration drift or candidate mismatch. Publish `tests/fixtures/axe-contrast-base.json` canonically. Focused mutation tests cover each rejection. <=12 minutes.

## Exact write boundary
a11y-contrast-validation: tests/scripts/verify-a11y-remediation.mjs, tests/specs/verify-a11y-remediation.spec.js, tests/fixtures/axe-contrast-base.json

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
