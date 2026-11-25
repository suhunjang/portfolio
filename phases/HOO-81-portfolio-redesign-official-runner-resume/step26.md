# Step 26: a11y-coupled-contrast-guard

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

Coupled foreground/background change guard only; no fixture write and no token selection. Read exact `tests/fixtures/axe-contrast-change-units.json` and `tests/fixtures/axe-contrast-base.json`. For each requiredState, verify `baseMapping.effectiveTargetKey` by recomputing Step21's exact strategy-independent hash from `baseMapping.projectRootSelector,relativeSelector,pseudoSelector,canonicalTargetFallback` plus the requiredState scenario fields; hash mismatch stops `effective-target-key-mismatch`. Group only by the verified effectiveTargetKey, which already includes scenario/viewport/theme/project/state/root/relative/pseudo/concrete fallback identity. If both `color` and `background-color` occur for the same key, stop exactly `coupled-contrast-change-unsupported` before Step27 chooses any token; otherwise print canonical summary and exit zero. Border-color does not form a contrast pair. Self-test includes two units that each pass against the opposite BASE color but jointly fall below 4.5 and must be rejected, plus uncoupled foreground-only/background-only cases. <=10 minutes.

## Exact write boundary
a11y-coupled-contrast-guard: tests/scripts/verify-a11y-remediation.mjs, tests/specs/verify-a11y-remediation.spec.js

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
