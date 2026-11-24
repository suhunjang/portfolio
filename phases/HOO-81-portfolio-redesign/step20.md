# Step 20 — scope-paths

- 목적: verify-scope 경로 정책(`css/themes.css` 변경 위반 포함)과 diff 인자 분리.
- 예상 19분 / 선행 0~19 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §11.1, §11.5, §12
- tracked 허용(exact): `tests/scripts/verify-scope.mjs`(신규), `tests/package.json`(`verify-scope`, `verify-scope:selftest` 추가만)
- runtime: R0
- 금지: §15.7

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step20`
2. `GIT_DIFF_PATH_ARGS`, `GIT_DIFF_PATCH_ARGS`, `collectInput({ git = runGit })`, `evaluatePaths(input)`.
3. CLI: 인자 없음 → `verify-scope: OK (paths)`. `--self-test`: 상수; 가짜 git 호출 기록(경로 층 PATH 인자만, data.js PATCH 인자만); 정상 0; 위반 — worktree `docs/other.md`, README stage 후 원복, assets 추가, 루트 package.json, `CLAUDE.md` 미커밋, `tests/node_modules/x` 추적, `.harness/harness.lock.json` 미커밋, worktree `css/themes.css` 수정; 허용 — committed `scripts/harness.py`, untracked `.harness/runtime/x.json`, worktree phases index; rename 우회 위반(README→tests/fixtures/x.md, assets/favicon.svg→tests/fixtures/f.svg, docs/superpowers/plans/…→tests/fixtures/p.md, .claude/settings.json→tests/fixtures/s.json).

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests run verify-scope:selftest && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step20.json --allow tests/scripts/verify-scope.mjs,tests/package.json` → exit 0
