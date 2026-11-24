# Step 21 — scope-content

- 목적: verify-scope 내용 판정과 `--final`.
- 예상 19분 / 선행 0~20 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §11.1, §11.5
- tracked 허용(exact): `tests/scripts/verify-scope.mjs`
- runtime: R0
- 금지: §15.7, 두 diff 인자 상수 값

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step21`
2. `checkGitignore(text)`, `checkDataJsDiff(patch, { requireExactly3 })`(삭제 줄 0, 추가 줄은 trim 후 `featured: true,`만, 3줄 이하), `evaluateContent(input, { final })`, `evaluateScope`(CLI 기본 `verify-scope: OK`, `--final`).
3. self-test 추가: patch 전달 합성(PATCH 인자+data.js면 3줄 patch, `--name-only`면 이름만) → final 0; `+    title: 'x',` 추가 위반; name-only 수집기 3줄 미달; data.js 위반(삭제 줄, featured 외 줄, 4줄, stage 후 원복); final 정상·위반(BASE→HEAD 0줄, BASE→index 2줄, index→worktree featured 외 줄); Space Grotesk 제거 stage 후 원복; gitignore 위반(추가·중복·빈 줄·순서·주석·CRLF·index만), 끝 개행 없음 통과.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests run verify-scope:selftest && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step21.json --allow tests/scripts/verify-scope.mjs` → exit 0
