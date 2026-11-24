# Step 33 — axe-classify

- 목적: baseline과 remediation plan 확정(색 변경 필요 target은 blocked). 이후 axe.spec.js는 `check` 모드.
- 예상 20분 이하(초과 산정 시 즉시 재계획) / 선행 0~32 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §7.2, §8.3(색 변경 제외, step 27·29, fixture, FIX_FILES_BY_KIND, step 33), §16.3; `axe-collected.json`
- tracked 허용(exact): `tests/fixtures/axe-baseline.json`(신규), `tests/fixtures/axe-remediation-plan.json`(신규)
- runtime: R0
- 금지: §15.7, 사이트 파일, helper·spec·axe-collected.json

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step33`
2. 시간 산정 먼저(묶음별 2분 + target × 1분, 합 + 6분). 20분 초과면 쓰지 않고 재계획. 위반 0건이면 baseline `[]`, plan `{ groups: [] }`.
3. 조사: `tests/.tmp` 임시 Playwright 스크립트(`prepareForAxe`)로 fixKind 판별. 색 값·색 역할을 바꿔야 해소되는 target은 fixKind 그대로 기록하되 그 그룹은 `blocked: true`, reason `color change excluded (HOO-81 §16.3)`.
4. baseline: projectEntry 7필드 + `fixes`, `fixFiles`. plan: kebab-case id, difficulty·estMinutes(≤20)·fixFiles·blocked·reason, coverage 완전. blocked가 있으면 `--check-executable`이 실패해 재계획으로 끝난다.

## AC

- `sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-baseline-match --collected tests/fixtures/axe-collected.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-plan --coverage && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-executable && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-regression --collected tests/fixtures/axe-collected.json && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step33.json --allow tests/fixtures/axe-baseline.json,tests/fixtures/axe-remediation-plan.json` → exit 0
