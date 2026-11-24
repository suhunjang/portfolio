# Step 43 — axe-remediation-gate

- 목적: 재수집·회귀 gate·plan 정리·coverage·실행 가능성 판정, remediation 재계획 입력 생성.
- 예상 18분 / 선행 0~42 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §7.2, §8.3(COLLECT_CHAIN, REGRESSION_GATE, 색 변경 제외, step 43, 재계획 그룹 계약), §16.3
- tracked 허용(exact): `tests/fixtures/axe-remediation-plan.json`(`--prune-plan` 결과로만)
- runtime: R0(COLLECT_DIR, `axe-current.json`)
- 금지: §15.7, 사이트 파일, baseline·collected·helper·spec

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step43`
2. 아래 AC 체인 순차 실행. REGRESSION_GATE 실패 시 plan 불변 중단, coverage 실패·`--check-executable` 실패(색 변경 blocked 포함)는 재계획 사유.
3. 결과 로그: groups `[]`이면 `remediation 불필요`, 남으면 `Harness 재계획 필요`와 그룹별 상세(재계획 그룹 step은 43과 44 사이).

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset && AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge --out tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-regression --collected tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --prune-plan --collected tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-coverage --collected tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-plan && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-executable && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step43.json --allow tests/fixtures/axe-remediation-plan.json` → exit 0
