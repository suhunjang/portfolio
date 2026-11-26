# Step 9: state-color-base-measurement

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

BASE state measurement and candidate-byte generation only, importing exact `withBaseArchiveBrowser` from step8. Lane runs measure-write then measure-check; detached fan-in acceptance runs measure-check first and never measure-write, so submitted candidate bytes cannot be healed. Implement strict `base-measurement` parser with exactly one of `--measure-write|--measure-check`, base-ref, candidate, server-root and port. Measure desktop-dark/light; keys hero-cta-btn-0/1, featured-card-0, grid-card-0/1; states default/hover/active; exact color/backgroundColor/borderColor. featured-card-0 maps deterministically from BASE grid-card-1. Canonical UTF-8 compact JSON with recursively code-unit-sorted keys and one trailing newline is written atomically only to component-state-colors.candidate.json. No BASE/working fixture write, no two-file transaction or rollback implementation in this step. Specs cover parser, measurement, mapping, canonical bytes, no-write check and failure preservation. <=14 minutes.

## Exact write boundary
state-color-base-measurement: tests/scripts/make-state-colors.mjs, tests/fixtures/component-state-colors.candidate.json, tests/specs/state-colors.spec.js

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
