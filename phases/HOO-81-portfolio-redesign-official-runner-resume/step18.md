# Step 18: a11y-color-derivation

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

ColorChanges derivation only, after contrast BASE. Read `tests/fixtures/axe-remediation-occurrences.json`, `tests/fixtures/axe-contrast-base.json` and css/style.css. The exact 61 is the inherited canonical pairs classification (139 total = 61 color + 78 nested), not a new post-design live count. For each occurrence, its stored `linkedStates` array is the sole scoring group. Candidate set is existing tokens whose resolved color yields WCAG2 ratio >=4.5 in every group member. For each candidate and member, compare candidate sRGB 8-bit channels to that member's BASE computed value for the changed property; distance is `(R-R0)^2+(G-G0)^2+(B-B0)^2`, and candidate score is the integer sum across all members. Choose minimum score, then code-unit token name. If no candidate passes, exit with `color-scope-themes-required`; never invent a literal or edit themes.css. No grouping may be inferred outside the stored array. Record occurrenceId, theme/state coverage, selector, property, from, to, tokenOrRole. Specs cover all 61, missing membership, 4.5 threshold, distance scoring, exact tie and no-candidate stop. <=14 minutes.

## Exact write boundary
a11y-color-derive: tests/scripts/verify-a11y-remediation.mjs, tests/specs/verify-a11y-remediation.spec.js, tests/fixtures/axe-remediation-evidence.json

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
