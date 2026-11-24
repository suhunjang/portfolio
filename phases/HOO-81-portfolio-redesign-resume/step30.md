# Resume Step 30 — axe-remediation-recheck (원 step 55, §R8 변경형)

- 목적: remediation 후 재수집·회귀 확인 → 작업 부분에서만 prune → plan 빔·위반 0 확인. no-op 규칙 대상 아님.
- 18분 / 선행 0~29 + 재계획 `axe-remediation-*` 전부 / 공통 원 §9 + §R1·§R8 / gate `RGATE 30`
- 허용(exact): `tests/fixtures/axe-remediation-plan.json`(`--prune-plan` 결과로만)
- runtime: R0(COLLECT_DIR, `tests/.tmp/axe-current.json`, `tests/.tmp/resume-sha/`)
- 추가 금지: 사이트 파일, baseline·collected·helper·spec, plan 임의 비우기, AC·probe에서 `--prune-plan` 실행, 변경 후 no-op 선언

## 작업
1. `RSNAP 30`
2. 사전 검사(쓰기 없음): `COLLECT_CHAIN --out tests/.tmp/axe-current.json && REGRESSION_GATE`(실패면 중단).
3. `SHA_SAVE tests/fixtures/axe-remediation-plan.json plan-30`
4. 변경: `AXE --prune-plan --collected tests/.tmp/axe-current.json`
5. `SHA_DIFF tests/fixtures/axe-remediation-plan.json plan-30 plan-pruned`
6. AC 실행. 실패 시 남은 그룹·target 보고 후 재계획.

## AC (작업 4 뒤, 모두 쓰기 없음)
- `REGRESSION_GATE && AXE --check-coverage --collected tests/.tmp/axe-current.json && AXE --check-plan && AXE --check-executable && AXE --check-plan --require-empty && AXE --assert-no-violations --collected tests/.tmp/axe-current.json && FULL && VS && RGATE 30 tests/fixtures/axe-remediation-plan.json`
