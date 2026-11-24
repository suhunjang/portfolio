# Resume Step 17 — axe-classify-merge

- 목적: §R7 — pairs.json 결정을 12 entry·139 occurrence로 확장해 원 §6.4 baseline·§6.5 plan 작성, strict 검증.
- 18분 / 선행 0~16 / 공통 §R1 / gate `RGATE 17`
- 허용(exact): `tests/fixtures/axe-baseline.json`, `tests/fixtures/axe-remediation-plan.json`(신규)
- runtime: R0
- 추가 금지: batch·pairs·collected·helper·spec·사이트 수정, pairs 결정과 다른 `fixKind`·`requiresColorChange`, manual block 생성, 계약 밖 필드

## 작업
1. `RSNAP 17`
2. pairs.json 읽기 → baseline 작성 → plan 작성(`requiredBlockReason`으로 blocked·reason).
3. blocked 그룹이 있거나 executable 실패면 원 §6.2 remediation 재계획 경로로 중단·보고.

## AC
- `MERGE_CHECK && AXE --check-baseline-match --collected tests/fixtures/axe-collected.json && AXE --check-plan --coverage && AXE --check-executable && AXE --check-regression --collected tests/fixtures/axe-collected.json && FULL && VS && RGATE 17 tests/fixtures/axe-baseline.json,tests/fixtures/axe-remediation-plan.json tests/fixtures/axe-baseline.json,tests/fixtures/axe-remediation-plan.json`(첫 명령 stdout `merge-check: OK 25 139`)
