# Step 34: a11y-live-scan-contract

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

Live scan only atop Step33 lifecycle. Implement exact `expandScenarios` and use it now only in verify-lane and verify-full; do not require future Step35/39/45 consumers before they exist. Ordered expansion is page mobile-dark/light, tablet-dark/light, desktop-dark/light with projectIndex null; modal desktop-dark/light projectIndex 0 from grid card 0; lightbox desktop-dark/light projectIndex 0 from that modal's first shot. Every scenario runs preparePage before overlay preparation. This step's specs prove exact input/output order and that current verify-lane/verify-full share the helper; omission, duplication, reordering or another index fails. verify-lane requires owned=0 and exact non-owned IDs, writes nothing and prints deterministic JSON. verify-full requires both zero, rejects new rules and supports exactly one output mode. No observation validator yet.

## Exact write boundary
a11y-live-scan: tests/scripts/verify-a11y-remediation.mjs, tests/specs/verify-a11y-remediation.spec.js

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
