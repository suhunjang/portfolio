# Step 55 — axe-remediation-recheck

- 목적: remediation 후 gate 재실행, plan 빔·위반 0 확인.
- 18분 / 선행 0~54 + 재계획 `axe-remediation-*` 전부 / 공통 §9 / gate GATE
- 허용(exact): `tests/fixtures/axe-remediation-plan.json`(`--prune-plan` 결과로만)
- runtime: R0
- 추가 금지: 사이트 파일, baseline·collected·helper·spec, plan 임의 비우기

## 작업
1. `SNAP 55` → step 54 체인 + `--require-empty` + `--assert-no-violations`. 실패 시 남은 그룹·target 보고 후 재계획.

## AC
- `COLLECT_CHAIN --out tests/.tmp/axe-current.json && REGRESSION_GATE && AXE --prune-plan --collected tests/.tmp/axe-current.json && AXE --check-coverage --collected tests/.tmp/axe-current.json && AXE --check-plan && AXE --check-executable && AXE --check-plan --require-empty && AXE --assert-no-violations --collected tests/.tmp/axe-current.json && FULL && VS && GATE 55 tests/fixtures/axe-remediation-plan.json`
