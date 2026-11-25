# Step 7: state-color-contract

## Current authoritative contract
Always-on: preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata. Historical references are read-only context; only current index argv and current contract execute.

- Reference-only: `phases/HOO-81-portfolio-redesign-resume/step25.md`, SHA-256 `edb28b425da2a3353701514f14f2cb0cff41508eb1f98f13c85d43ac83cf4038`. Do **not** execute its legacy RSNAP/REQ/DI/RGATE/FULL/no-op commands; the current argv contract below replaces them.
### Current carried-forward requirements from historical boundary 25 (authoritative, not a command)
   - `existing`: 작업 2~4 생략, 쓰기 없는 AC 전체 실행(`--check`는 쓰기 없음) → 통과 시 `resume step25: no-op`, 실패 시 tracked 불변 중단·재계획.
   - `new`: 아래 진행. `branch-mixed`면 중단.
2. generator: 원 step 48 작업 2 그대로(테마별 context 1280×800, `route('http://base.invalid/**')`로 BASE 파일, BASE `THEME_KEY` 정규식 추출, `context.addInitScript` 1회 null-only, `measureStateSequence`로 `hero-cta-btn-{i}`·`grid-card-0`·`grid-card-1`, color·backgroundColor·borderColor만, 키 정렬·2칸·끝 개행 1, `--check [--fixture]` → `state-colors: OK`/`state-colors: mismatch`, 그 밖 인자 exit 2).
3. 생성 `W node tests/scripts/make-state-colors.mjs`.
4. spec(node, desktop-dark; 독립 test 4개): `schema`, `serialization`, `check-ok`(첫 줄 `test.setTimeout(75000)`, subprocess 60000ms), `check-mismatch`(첫 줄 `test.setTimeout(75000)`, 사본 변경·subprocess 60000ms·원본 불변·finally 삭제) — 원 step 48 작업 4 그대로.
Current contract: generator modes are explicit. `base-expectation` compares the approved BASE semantic values to the committed expectation; it never captures current output to bless it. Step13 later computes `approved-remediation-delta` from the immutable remediation evidence and applies only declared token/role deltas to expected values. After step14 the same approved-delta expectation is checked against current implementation. No-op forbidden.

## Exact write boundary
state-color: tests/scripts/make-state-colors.mjs, tests/fixtures/component-state-colors.json, tests/specs/state-colors.spec.js

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Run every immutable argv in index.json for this step in order. Nonzero blocks. emptyAllowed=false means each worker wave must produce its declared artifact/spec/source change; legacy no-op branches do not apply.
