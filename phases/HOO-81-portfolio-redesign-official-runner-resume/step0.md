# Step 0: inherit-preflight

## Current authoritative contract
Always-on: preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata. Historical references are read-only context; only current index argv and current contract execute.

Verify exact immutable inputs before any product step: `CLAUDE.md` SHA b63e8c71bea72313c7ae312c6c5582e6fd1ccc98b122d2f4ade46f09e65cb8aa; original design `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` SHA eb229f57acb23bd9a24d990d3c510ec3fb824fc24051909bb02665408cd54e49; resume design `docs/superpowers/specs/2026-11-24-portfolio-redesign-resume-design.md` SHA 351a18f1b6ca30f46606ab25ff310329eeecd8cd4db138d7848a86d414b3ffe1; `.harness/harness.lock.json` SHA d7df38b1d032e1c7ef6c535f5257b69a42143ce323baf80cfc9bddee8be62aa3; `.harness/install-state.json` SHA a022500410b8a145121b6693f4315dfd90ae9a06f2082621a623ad5a39ec5e7f; `.harness/policy.json` SHA ad59822299dee5f9aeaca8dba8ee6232e788b9e66af09c70b1ec4b9ba838aaa0. All are regular non-symlink files. Official runner approval/snapshot gate must bind approvedPlanCommit=current plan HEAD, issue HOO-81, current plan SHA, current execution SHA and CLEAN review record before launching step0; continuation-preflight verifies current index `executionPlan` resolves to execution.json and recomputed manifest/execution hashes equal the launch descriptor. It separately rejects missing document, hash mismatch, lock identity mismatch, approval/snapshot mismatch, execution-binding mismatch and non-descendant BASE. Verify/copy `/Volumes/P9/dev/hoonlabs/work/HOO-81-portfolio/tests/.tmp/axe-classify/pairs.json` 47392 bytes/SHA `1ba8778ab6cc9254b4404a5349f53c4463c0c55e4a1b2b447eac02a8bd8acaa1` to `tests/fixtures/axe-pairs-inherited.json` and verify collected 28809 bytes/SHA `ff7c76a6214034251f5ebc028706b9ae383ec6ecb9ce8a4c3ed97e266672e63c`. No-op forbidden.

## Exact write boundary
preflight-contract: tests/scripts/continuation-preflight.mjs, tests/specs/continuation-preflight.spec.js, tests/fixtures/axe-pairs-inherited.json

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Run every immutable argv in index.json for this step in order. Nonzero blocks. emptyAllowed=false means each worker wave must produce its declared artifact/spec/source change; legacy no-op branches do not apply.
