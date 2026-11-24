# Resume Step 33 — axe-finalize (원 step 56, §R8 변경형)

- 목적: 위반 0 전제 확인 후 작업 부분에서 baseline `[]` 확정. no-op 규칙 대상 아님.
- 16분 / 선행 0~32 / 공통 원 §9 + §R1·§R8 / gate `RGATE 33`
- 허용(exact): `tests/fixtures/axe-baseline.json`(`[]`로만)
- runtime: R0(`tests/.tmp/axe-current.json`, `tests/.tmp/resume-sha/`)
- 추가 금지: 사이트 파일, helper·spec·다른 fixture, 변경 후 no-op 선언

## 작업
1. `RSNAP 33`
2. 전제(쓰기 없음, 실패 시 baseline 불변 중단): `COLLECT_CHAIN --out tests/.tmp/axe-current.json && REGRESSION_GATE && AXE --check-plan --require-empty && AXE --assert-no-violations --collected tests/.tmp/axe-current.json`
3. `SHA_SAVE tests/fixtures/axe-baseline.json baseline-33`
4. 변경: baseline을 정확히 `[]` + 끝 개행으로 기록.
5. `SHA_DIFF tests/fixtures/axe-baseline.json baseline-33 baseline-finalized`

## AC (작업 4 뒤, 모두 쓰기 없음)
- `AXE --assert-empty && FULL && VS && RGATE 33 tests/fixtures/axe-baseline.json`
