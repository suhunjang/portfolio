# Step 7: state-color-contract

## Current authoritative contract
Always-on: preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata. Historical references are read-only context; only current index argv and current contract execute.

- Reference-only: `phases/HOO-81-portfolio-redesign-resume/step25.md`, SHA-256 `edb28b425da2a3353701514f14f2cb0cff41508eb1f98f13c85d43ac83cf4038`. Do **not** execute its legacy RSNAP/REQ/DI/RGATE/FULL/no-op commands; the current argv contract below replaces them.
### Current carried-forward requirements from historical boundary 25 (authoritative, not a command)

Current contract: before code is written, shared evidence schema is fixed as `{schemaVersion:1,original,scenarios,occurrences,colorChanges}`; occurrence IDs and colorChanges fields/rules are those in current step13. Fixture schema is theme keys desktop-dark/desktop-light, component keys `hero-cta-btn-0`, `hero-cta-btn-1`, `grid-card-0`, `grid-card-1`, each with states default/hover/active and exact color/backgroundColor/borderColor strings. Multiple occurrences may map to one selector/property only when theme,state,from,to,tokenOrRole are identical; otherwise `state-colors: conflicting-remediation` exit1. Missing required key/state/linked occurrence is invalid. Exact CLI: base-expectation uses `--mode base-expectation --base-ref <40hex> (--write|--check) [--fixture path]`; approved delta uses `--mode approved-remediation-delta --base-ref <40hex> --remediation evidence (--validate|--write|--check) [--fixture path]`. Other args exit2. approved `--validate` is read-only; `--write` derives fixture from base+evidence only; `--check` compares derived fixture and current DOM after remediation. Step7 specs include minimal valid evidence plus conflict, missing occurrence, missing state, invalid token/role and no-write cases. No-op forbidden.

## Exact write boundary
state-color: tests/scripts/make-state-colors.mjs, tests/fixtures/component-state-colors.json, tests/specs/state-colors.spec.js

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Run every immutable argv in index.json for this step in order. Nonzero blocks. emptyAllowed=false means each worker wave must produce its declared artifact/spec/source change; legacy no-op branches do not apply.
