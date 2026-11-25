# Step 26: final-screenshots

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

Screenshot contract only. `screenshots.spec.js` must import `resolveScreenshotOutputRoot` from `tests/scripts/verify-final-contract.mjs`; it may not duplicate, wrap or fall back from resolution. The returned screenshot directory is the sole persistent external runtime output for worker lanes; the steps8/9/16 process-owned temp tree is ephemeral and removed in finally. Create only that returned directory. Required files: desktop-dark-page.png and desktop-light-page.png at 1280x800; mobile-dark-menu-open.png at 375x812; desktop-dark-modal-1.png, -5.png, -7.png, -0.png, -2.png, -12.png at 1280x800. Each newly written nonempty PNG with exact state/dimensions. Worker verification captures HEAD and tracked diff before focused tests and requires both unchanged afterward, with no path outside `tests/specs/screenshots.spec.js` added or modified; it does not require whole-repository clean while the allowed lane diff is uncommitted. When final-contract.spec.js runs in this worker, clean-tree enforcement occurs only if the CLI is explicitly passed `--require-clean`, which this worker focused test does not pass. Missing/malformed resolver input exits2 before any write.

## Exact write boundary
final-screenshot: tests/specs/screenshots.spec.js

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
