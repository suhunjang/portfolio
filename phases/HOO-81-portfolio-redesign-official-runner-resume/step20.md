# Step 20: state-color-remediation-contract

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

Remediation expectation derivation only. Strict mode `approved-remediation-expectation` accepts exactly base-ref, remediation, expected-fixture, base-fixture, server-root, port and one of derive/validate. `--derive` validates evidence change-unit decisions, immutable BASE identity, token/state/conflict/path links and deterministically writes canonical `tests/fixtures/component-state-colors.remediation-expected.json`; it never writes the working fixture or checks live DOM. `--validate` is read-only and must be the first fan-in AC, rejecting a bad submitted expected fixture before any generation. Reconstruct BASE via step8 lifecycle and require `tests/fixtures/component-state-colors.base.json` equality. Lane runs derive then validate; fan-in runs validate only. Specs cover conflict, missing state/unit, token/path mismatch, immutable BASE drift, canonical determinism and failure preservation. <=16 minutes.

## Exact write boundary
state-color-remediation-contract: tests/scripts/make-state-colors.mjs, tests/specs/state-colors.spec.js, tests/fixtures/component-state-colors.remediation-expected.json

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
