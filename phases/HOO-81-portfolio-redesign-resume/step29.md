# Resume Step 29 — axe-remediation-gate (원 step 54, §R8 변경형)

- 목적: 원 §6.2 gate — 재수집·회귀 확인 후 작업 부분에서만 prune, 이어 coverage·plan·executable 검증. no-op 규칙 대상 아님.
- 18분 / 선행 0~28 / 공통 원 §9 + §R1·§R8 / gate `RGATE 29`
- 허용(exact): `tests/fixtures/axe-remediation-plan.json`(`--prune-plan` 결과로만)
- runtime: R0(COLLECT_DIR, `tests/.tmp/axe-current.json`, `tests/.tmp/resume-sha/`)
- 추가 금지: 사이트 파일, baseline·collected·helper·spec, AC·probe에서 `--prune-plan` 실행, 변경 후 no-op 선언

## 작업
1. `RSNAP 29`
2. 사전 검사(쓰기 없음): `COLLECT_CHAIN --out tests/.tmp/axe-current.json && REGRESSION_GATE`(회귀 실패면 plan 불변 중단).
3. `SHA_SAVE tests/fixtures/axe-remediation-plan.json plan-29`
4. 변경: `AXE --prune-plan --collected tests/.tmp/axe-current.json`
5. `SHA_DIFF tests/fixtures/axe-remediation-plan.json plan-29 plan-pruned`(로그 `plan-pruned: changed|unchanged`).
6. AC 실행. groups `[]`면 로그 `remediation 불필요`, 남으면 `Harness 재계획 필요`+그룹 상세(재계획 `axe-remediation-{id}`는 resume 29와 30 사이, `css/themes.css` 포함이면 생성 안 함). coverage·plan·executable 실패는 재계획 사유.

## AC (작업 4 뒤, 모두 쓰기 없음)
- `REGRESSION_GATE && AXE --check-coverage --collected tests/.tmp/axe-current.json && AXE --check-plan && AXE --check-executable && FULL && VS && RGATE 29 tests/fixtures/axe-remediation-plan.json`
