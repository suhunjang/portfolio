# Step 1: inherited-artifact-supply

## Current authoritative contract
Always-on preparation: before each worker acts, read CLAUDE.md and both pinned design docs and apply every compatible guardrail; current step contracts replace only legacy execution wrappers, never repository instructions or approved product constraints. If any conflict exists, stop before writing. Preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata.

Inherited artifact supply only. Source is actual 0644 regular non-symlink. Open one read-only FD, capture path and FD device/inode/mode/size/mtime/SHA, require 47392 bytes/SHA `1ba8778ab6cc9254b4404a5349f53c4463c0c55e4a1b2b447eac02a8bd8acaa1`, and write bytes from that FD to a same-destination-directory temporary regular file. fsync temp; before rename, revalidate both open FD and source path identity/metadata/SHA against the initial snapshot and require temp SHA exact. Only after all checks atomically rename temp to `tests/fixtures/axe-pairs-inherited.json` and fsync parent. No post-publish source check is required; failures before rename unlink temp and preserve prior destination bytes exactly. Tests inject source path replacement, FD mutation, temp write/fsync, pre-rename identity/SHA and rename failures and prove destination preservation. `artifact-post` is read-only and verifies submitted destination/collected bytes and candidate paths without external source access. Never chmod or mutate source.

## Exact write boundary
artifact-supply: tests/scripts/continuation-preflight.mjs, tests/specs/continuation-preflight.spec.js, tests/fixtures/axe-pairs-inherited.json

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Each worker runs only its own execution.json lane `requiredCommands` and `focusedTests` in order; it never runs index.json `acceptanceCommands` inside the uncommitted lane worktree. Nonzero blocks and `emptyAllowed=false` requires the declared lane artifact/spec/source change. After all lane outputs form one deterministic fan-in candidate, the official runner applies it to an isolated detached staging tree, runs this step's index.json `acceptanceCommands` exactly once there, binds acceptanceEvidenceSha/inputsSha256 into the completion record, and only then publishes fan-in commits. Legacy no-op branches do not apply.
