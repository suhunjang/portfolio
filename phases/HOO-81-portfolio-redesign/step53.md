# Step 53 — axe-remediation-recheck

- 목적: remediation 후 gate 재실행, plan 비었음과 현재 위반 0 확인.
- 예상 18분 / 선행 0~52 + 재계획 `axe-remediation-*` 전부 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §8.3, §8.6, `step52.md`
- tracked 허용(exact): `tests/fixtures/axe-remediation-plan.json`(`--prune-plan` 결과로만)
- runtime: R0
- 금지: §15.7, 사이트 파일, baseline·collected·helper·spec, plan 임의 비우기

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step53`
2. step 52 체인 + `--check-plan --require-empty` + `--assert-no-violations`. 실패 시 남은 그룹·target 보고 후 재계획.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset && AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge --out tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-regression --collected tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --prune-plan --collected tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-coverage --collected tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-plan && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-executable && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-plan --require-empty && sh tests/scripts/with-env.sh node tests/helpers/axe.js --assert-no-violations --collected tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step53.json --allow tests/fixtures/axe-remediation-plan.json` → exit 0
