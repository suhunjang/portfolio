# Step 56 — axe-finalize

- 목적: 위반 0 전제 확인 후 baseline `[]` 확정.
- 16분 / 선행 0~55 / 공통 §9 / gate GATE
- 허용(exact): `tests/fixtures/axe-baseline.json`(`[]`로만)
- runtime: R0
- 추가 금지: 사이트 파일, helper·spec·다른 fixture

## 작업
1. `SNAP 56`
2. 전제(실패 시 baseline 불변 중단): `COLLECT_CHAIN --out tests/.tmp/axe-current.json && REGRESSION_GATE && AXE --check-plan --require-empty && AXE --assert-no-violations --collected tests/.tmp/axe-current.json`
3. baseline `[]` 후 일반 axe 전체. 실패 시 보고·재계획.

## AC
- 작업 2 exit 0, 이어 `AXE --assert-empty && FULL && VS && GATE 56 tests/fixtures/axe-baseline.json`
