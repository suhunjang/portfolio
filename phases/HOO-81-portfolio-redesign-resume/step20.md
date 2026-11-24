# Resume Step 20 — axe-finalize (원 step 56)

- 목적: 위반 0 전제 확인 후 baseline `[]` 확정.
- 16분 / 선행 0~19 / 공통 원 §9 + §R1 / gate `RGATE 20`
- 허용(exact): `tests/fixtures/axe-baseline.json`(`[]`로만)
- runtime: R0
- 추가 금지: 사이트 파일, helper·spec·다른 fixture

## 작업
1. `RSNAP 20`
2. 전제(실패 시 baseline 불변 중단): `COLLECT_CHAIN --out tests/.tmp/axe-current.json && REGRESSION_GATE && AXE --check-plan --require-empty && AXE --assert-no-violations --collected tests/.tmp/axe-current.json`
3. baseline `[]` 후 일반 axe 전체. 실패 시 보고·재계획.

## AC
- 작업 2 exit 0, 이어 `AXE --assert-empty && FULL && VS && RGATE 20 tests/fixtures/axe-baseline.json`
