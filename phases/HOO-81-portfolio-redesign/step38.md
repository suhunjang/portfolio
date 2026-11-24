# Step 38 — axe-classify

- 목적: §8.5 baseline과 §8.6 plan을 계약대로만 생성(색 변경 필요 target은 blocked).
- 예상 20분 이하(초과 산정 시 즉시 재계획) / 선행 0~37 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §7.2, §8.3, §8.5, §8.6, §16.3; `axe-collected.json`
- tracked 허용(exact): `tests/fixtures/axe-baseline.json`(신규), `tests/fixtures/axe-remediation-plan.json`(신규)
- runtime: R0
- 금지: §15.7, 사이트 파일, helper·spec·axe-collected.json, §8.5·§8.6 밖 필드

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step38`
2. 시간 산정 먼저(묶음별 2분 + target × 1분, 합 + 6분). 20분 초과면 쓰지 않고 재계획. 위반 0건이면 baseline `[]`, plan `{ "groups": [] }`.
3. 조사: `tests/.tmp` 임시 Playwright 스크립트(래퍼, `prepareForAxe`)로 fixKind 판별.
4. baseline: collected entry마다 §8.5 형식(fixes는 targets 순서 1:1, fixFiles는 FIX_FILES_BY_KIND, entry fixFiles 합집합).
5. plan: §8.6 형식(PlanTarget 정렬, id 정렬, coverage 완전, blocked·reason 규칙). blocked가 있으면 AC의 `--check-executable`이 실패해 재계획으로 끝난다.

## AC

- `sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-baseline-match --collected tests/fixtures/axe-collected.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-plan --coverage && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-executable && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-regression --collected tests/fixtures/axe-collected.json && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step38.json --allow tests/fixtures/axe-baseline.json,tests/fixtures/axe-remediation-plan.json` → exit 0
