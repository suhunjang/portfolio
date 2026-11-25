# Step 15: state-color-remediation-contract

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

Approved-remediation delta contract only, after immutable evidence exists and before color guard/remediation. Extend the step8 script with the exact argv `node tests/scripts/make-state-colors.mjs --mode approved-remediation-delta --base-ref <40hex> --remediation tests/fixtures/axe-remediation-evidence.json (--validate|--write|--check) --fixture tests/fixtures/component-state-colors.json --server-root . --port 4175`; missing, duplicate or extra options and all other combinations exit2. Evidence path is exactly `tests/fixtures/axe-remediation-evidence.json`. `--validate` reads BASE fixture+evidence only and writes nothing; `--write` atomically derives post fixture from BASE fixture+evidence and never current DOM; `--check` compares that derivation and live current DOM. Reuse the completed step7 archive-based owned temp-root/PID cleanup implementation without reimplementing it. Validation/mismatch exits1. Specs cover validate success, conflict, missing link/state, invalid token/role, payload/path mismatch, occupied port, no-write and failure preservation. This step may edit only the script and its spec; the BASE fixture stays byte-identical.

## Exact write boundary
state-color-remediation-contract: tests/scripts/make-state-colors.mjs, tests/specs/state-colors.spec.js

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs are deterministically fanned in and committed, the official runner runs this step's index.json `acceptanceCommands` exactly once. Legacy no-op branches do not apply.
