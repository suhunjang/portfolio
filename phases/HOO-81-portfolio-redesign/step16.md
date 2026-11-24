# Step 16 — scope-content

- 목적: verify-scope 내용 판정(data.js patch, Space Grotesk, gitignore)과 `--final`.
- 예상 19분 / 선행 0~15 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §11.1, §11.5
- tracked 허용(exact): `tests/scripts/verify-scope.mjs`
- runtime: R0
- 금지: §15.7, 두 diff 인자 상수 값

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step16`
2. `checkGitignore(text)`, `checkDataJsDiff(patch, { requireExactly3 })`, `evaluateContent(input, { final })`, `evaluateScope = [...evaluatePaths, ...evaluateContent]`(CLI 기본 `verify-scope: OK`, `--final`).
3. self-test 추가: patch 전달 합성(PATCH 인자+data.js면 `featured: true,` 3줄, `--name-only`면 이름만) → final 0; `title` 추가 위반; name-only 수집기 → 3줄 미달 위반; data.js 위반 4종; final 정상·위반 3종; Space Grotesk 제거 stage 후 원복 위반; gitignore 위반 7종, 끝 개행 없음 통과.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests run verify-scope:selftest && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step16.json --allow tests/scripts/verify-scope.mjs` → exit 0
