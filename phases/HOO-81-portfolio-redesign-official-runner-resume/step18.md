# Step 18: a11y-live-scan-contract

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

Live scan only atop step17 lifecycle. Implement one shared `expandScenarios` used unchanged by this step and steps19/23/27. The only complete ordered expansion is page mobile-dark/light, tablet-dark/light, desktop-dark/light each with projectIndex null; modal desktop-dark then desktop-light each projectIndex 0 opened from `#projectGrid .project-card[data-project="0"]`; lightbox desktop-dark then desktop-light each projectIndex 0, opened by that same grid-card modal then its first `.shot-zoom`. Every scenario runs preparePage (fonts, reveal, scroll reset) before overlay preparation; order is exactly the listed order and omission, duplication, reordering or any other index fails. Implement verify-lane and verify-full. verify-lane requires owned=0 and exact non-owned IDs, writes nothing and prints deterministic JSON. verify-full requires both zero, rejects new rules and supports exactly one of write-observation or observation-stdout. Setup/browser exit2, validation exit1, success0. Specs prove all four consumers use the same expansion and fail when one scenario/project index is removed.

## Exact write boundary
a11y-live-scan: tests/scripts/verify-a11y-remediation.mjs, tests/specs/verify-a11y-remediation.spec.js

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
