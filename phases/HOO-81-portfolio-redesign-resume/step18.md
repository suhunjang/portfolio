# Resume Step 18 — axe-remediation-gate (원 step 54)

- 목적: 원 §6.2 gate(재수집·회귀·prune·coverage·plan 검증·실행 가능성), 재계획 입력.
- 18분 / 선행 0~17 / 공통 원 §9 + §R1 / gate `RGATE 18`
- 허용(exact): `tests/fixtures/axe-remediation-plan.json`(`--prune-plan` 결과로만)
- runtime: R0(COLLECT_DIR, `axe-current.json`)
- 추가 금지: 사이트 파일, baseline·collected·helper·spec

## 작업
1. `RSNAP 18`
2. AC 순차(`--check-plan`이 `--check-executable`보다 먼저). 회귀 실패 시 plan 불변 중단, coverage·plan·executable 실패는 재계획 사유.
3. 로그: groups `[]`면 `remediation 불필요`, 남으면 `Harness 재계획 필요`+그룹 상세(재계획 `axe-remediation-{id}`는 resume 18과 19 사이, `css/themes.css` 포함이면 생성 안 함).

## AC
- `COLLECT_CHAIN --out tests/.tmp/axe-current.json && REGRESSION_GATE && AXE --prune-plan --collected tests/.tmp/axe-current.json && AXE --check-coverage --collected tests/.tmp/axe-current.json && AXE --check-plan && AXE --check-executable && FULL && VS && RGATE 18 tests/fixtures/axe-remediation-plan.json`
