# Step 37 — axe-remediation-gate

- 목적: 재수집·회귀 gate·plan 정리·coverage·실행 가능성 판정, remediation 재계획 입력 생성.
- 예상 18분 / 선행 0~36 / 공통 절차 설계 §15
- read-first: 설계 §7.2, §8.3(COLLECT_CHAIN, REGRESSION_GATE, step 25·27 도구, step 37 gate, 재계획 그룹 step 계약); baseline·plan 파일
- tracked 허용(exact): `tests/fixtures/axe-remediation-plan.json`(`--prune-plan` 결과로만, 손 편집 금지)
- runtime: R0(COLLECT_DIR, `axe-current.json`)
- 금지: §15.7, 사이트 파일, baseline·collected·helper·spec

## 작업 (step 38이 같은 절차를 재실행)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step37`
2. 아래 AC 체인을 순차 실행(병렬 금지). REGRESSION_GATE 실패 시 plan 불변으로 중단, coverage 실패는 자동 편입 없이 재계획 사유, `--check-executable` 실패는 remediation step 생성 없이 중단·재계획 사유.
3. 결과 로그: groups `[]`이면 `remediation 불필요`, 그룹이 남고 모두 통과면 `Harness 재계획 필요`와 그룹별 상세. 그룹 step은 설계 §8.3 재계획 그룹 step 계약(첫 동작 `python3 -I tests/scripts/start-snapshot.py axe-remediation-{id}`, gate `--check tests/.tmp/start-snapshot-axe-remediation-{id}.json --allow {fixFiles}`)대로 하네스가 37과 38 사이에 만든다.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset && AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge --out tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-regression --collected tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --prune-plan --collected tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-coverage --collected tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-plan && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-executable && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step37.json --allow tests/fixtures/axe-remediation-plan.json` → exit 0
