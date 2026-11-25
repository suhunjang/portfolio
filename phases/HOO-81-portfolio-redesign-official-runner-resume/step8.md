# Step 8: state-color-base-fixture

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

BASE state measurement and fixture create/check only, reusing the completed step7 archive/server lifecycle without reimplementing it. Fixture themes are desktop-dark/light; component keys `hero-cta-btn-0`, `hero-cta-btn-1`, `featured-card-0`, `grid-card-0`, `grid-card-1`; states default/hover/active; values exact color/backgroundColor/borderColor strings. featured-card-0 BASE values are copied exactly from BASE `grid-card-1` (project index 1) for the same theme/state because BASE has no featured DOM; never query a nonexistent BASE featured card or current DOM. Exact argv is `node tests/scripts/make-state-colors.mjs --mode base-expectation --base-ref <40hex> (--write|--check) --fixture tests/fixtures/component-state-colors.json --server-root . --port 4175`; missing, duplicate or extra options and all other mode/action combinations exit2. `--write` atomically replaces only the tracked fixture; `--check` is read-only byte/semantic comparison. Mismatch exits1, setup/argv exits2; failures preserve fixture/repo bytes. Specs cover strict argv parsing, theme/state measurement, featured mapping, create/check success, no-write check and atomic failure preservation.

## Exact write boundary
state-color-base-fixture: tests/scripts/make-state-colors.mjs, tests/fixtures/component-state-colors.json, tests/specs/state-colors.spec.js

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs are deterministically fanned in and committed, the official runner runs this step's index.json `acceptanceCommands` exactly once. Legacy no-op branches do not apply.
