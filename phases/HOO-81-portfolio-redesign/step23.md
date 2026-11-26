# Step 23 — scope-content

- 목적: verify-scope 내용 판정과 `--final`.
- 19분 / 선행 0~22 / 공통 §9 / gate GATE
- 허용(exact): `tests/scripts/verify-scope.mjs`
- runtime: R0
- 추가 금지: 두 diff 인자 상수 값

## 작업
1. `SNAP 23`
2. `checkGitignore`, `checkDataJsDiff(patch, { requireExactly3 })`(삭제 0, 추가는 trim 후 `featured: true,`만, ≤3줄), `evaluateContent(input, { final })`, `evaluateScope`(기본 `verify-scope: OK`, `--final`).
3. self-test: patch 합성(PATCH+data.js면 3줄, `--name-only`면 이름만) → final 0; `+    title: 'x',` 위반; name-only 3줄 미달; data.js 위반(삭제, featured 외, 4줄, stage 후 원복); final 정상·위반(BASE→HEAD 0줄, BASE→index 2줄, index→worktree featured 외); Space Grotesk 제거 stage 후 원복; gitignore 위반(추가·중복·빈 줄·순서·주석·CRLF·index만), 끝 개행 없음 통과.

## AC
- `W npm --prefix tests run verify-scope:selftest && VS && FULL && GATE 23 tests/scripts/verify-scope.mjs`
