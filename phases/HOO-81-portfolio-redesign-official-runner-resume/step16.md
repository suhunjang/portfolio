# Step 16: a11y-color-derivation

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

ColorChanges derivation and validation only, after step15 occurrence mapping. Read immutable `tests/fixtures/axe-remediation-occurrences.json`, immutable `tests/fixtures/component-state-colors.base.json`, and existing `css/style.css`; write final `tests/fixtures/axe-remediation-evidence.json` by copying the verified occurrences and adding exact colorChanges fields occurrenceId, theme, state, selector, property, from, to, tokenOrRole. BASE foreground/background and theme/state come only from the immutable BASE fixture; selectors/properties/token roles must resolve to existing css/style.css declarations. Compute sRGB linearized relative luminance and WCAG2 contrast `(Llighter+0.05)/(Ldarker+0.05)`, require >=4.5 for every linked theme/state/scenario, and reject alpha/unresolved backgrounds, missing links, duplicates, conflicts, new literals, themes.css/index needs, or mutation of occurrence fields. Specs cover positive 61 mappings and boundary/rounding, background composition, conflict and incomplete-input negatives. Fixture-only, <=14 minutes; step17 delta may run only after this final evidence is committed.

## Exact write boundary
a11y-color-derive: tests/scripts/verify-a11y-remediation.mjs, tests/specs/verify-a11y-remediation.spec.js, tests/fixtures/axe-remediation-evidence.json

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
