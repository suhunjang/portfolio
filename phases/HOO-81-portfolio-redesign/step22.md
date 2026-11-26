# Step 22 — scope-paths

- 목적: 설계 §8.4 경로 정책과 diff 인자 분리.
- 19분 / 선행 0~21 / 공통 §9 / gate GATE
- 허용(exact): `tests/scripts/verify-scope.mjs`(신규), `tests/package.json`(`verify-scope`, `verify-scope:selftest` 추가만)
- runtime: R0

## 작업
1. `SNAP 22`
2. `GIT_DIFF_PATH_ARGS`, `GIT_DIFF_PATCH_ARGS`, `collectInput`, `evaluatePaths`. CLI 인자 없음 `verify-scope: OK (paths)`. `--self-test`: 상수; 가짜 git 기록(경로 PATH 인자만, data.js PATCH만); 정상 0; 위반 — worktree `docs/other.md`, README stage 후 원복, assets 추가, 루트 package.json, `CLAUDE.md` 미커밋, `tests/node_modules/x` 추적, `.harness/harness.lock.json` 미커밋, worktree `css/themes.css`; 허용 — committed `scripts/harness.py`, untracked `.harness/runtime/x.json`, worktree phases index; rename 우회 위반(README→tests/fixtures/x.md, assets/favicon.svg→tests/fixtures/f.svg, docs/superpowers/plans/…→tests/fixtures/p.md, .claude/settings.json→tests/fixtures/s.json).

## AC
- `W npm --prefix tests run verify-scope:selftest && VS && FULL && GATE 22 tests/scripts/verify-scope.mjs,tests/package.json`
