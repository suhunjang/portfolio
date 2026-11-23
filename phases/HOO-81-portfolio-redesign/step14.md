# Step 14 — scope-content

- 목적: verify-scope 내용 판정(data.js patch, Space Grotesk, gitignore)과 `--final`.
- 예상 19분 / 선행 0~13 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §11.1, §11.5(내용 판정, final, 합성)
- tracked 허용(exact): `tests/scripts/verify-scope.mjs`
- runtime: R0
- 금지: §15.7, 두 diff 인자 상수 값

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step14`
2. `checkGitignore(text)`(null 위반, 끝 `\n` 1개 제거 후 7줄 정확), `checkDataJsDiff(patch, { requireExactly3 })`, `evaluateContent(input, { final })`(4구간 patch 그대로 전달, BASE→HEAD/index/worktree는 `requireExactly3: final`, index→worktree는 false, index.html 3종·gitignore 2종), `evaluateScope = [...evaluatePaths, ...evaluateContent]`(CLI 기본, `verify-scope: OK`, `--final`).
3. self-test 추가(기존 유지): patch 전달 합성(가짜 git: PATCH 인자+data.js면 `featured: true,` 3줄 patch, `--name-only`면 이름만) → final 위반 0; `+    title: 'x',` 추가 → 위반; name-only 수집기 → final 3줄 미달 위반. data.js 위반: 삭제 줄, featured 외 줄, 4줄, stage 후 worktree 원복. final: 각 3줄·index→worktree 0 → 0; BASE→HEAD 0줄, BASE→index 2줄, index→worktree featured 외 줄 → 위반. Space Grotesk 제거 stage 후 원복 → 위반. gitignore 위반: 추가 줄, 중복, 빈 줄, 순서, 주석, CRLF, index만 잘못됨; 끝 개행 없음은 통과.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests run verify-scope:selftest && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step14.json --allow tests/scripts/verify-scope.mjs` → exit 0
