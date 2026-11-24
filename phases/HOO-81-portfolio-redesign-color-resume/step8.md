# Color-resume Step 8 — a11y-wave-verify

- 존재 이유: `COORD_WAVE2`의 integration을 검증하고, 위반 0을 확인한 뒤 baseline·plan을 빈 상태로 확정한다.
- 시간: agent 예상 ≤20분. 근거: 검증 명령, 수집 1회, 고정 내용 파일 2개. Harness hard timeout은 30분.
- 선행: 0~7과 `COORD_WAVE2` 완료. 완료 조건은 `tests/.tmp/parallel/current-wave-2.json`이 있고 integration commit이 HEAD인 것이다. 빈 wave도 유효한 envelope다.
- 공통 규칙: 원 §9 + §C1·§C9
- gate: `XGATE 8`
- 허용(exact): `tests/fixtures/axe-baseline.json`, `tests/fixtures/axe-remediation-plan.json`(둘 다 신규)
- runtime: R0 + `tests/.tmp/axe-current.json`, `tests/.tmp/parallel/idx-*`
- 추가 금지: 사이트·helper·spec 수정, 위반이 남은 상태에서 baseline·plan 작성, manifest 밖 변경 수용

## 작업
1. `XSNAP 8`
2. `PW verify-record --wave 2 --current --manifest tests/.tmp/a11y-wave/components.json`
3. `PW validate-manifest …`를 다시 실행하고 `GS`를 실행한다.
4. `COLLECT_CHAIN --out tests/.tmp/axe-current.json && AXE --assert-no-violations --collected tests/.tmp/axe-current.json`. 실패하면 남은 target을 보고하고 중단한다. 이때는 파일을 쓰지 않는다.
5. 파일 2개를 쓴다.
   - baseline: 정확히 `[]` + 끝 개행
   - plan: 정확히 `{ "groups": [] }`, 2칸 들여쓰기, 끝 개행
6. AC가 PASS한 뒤에만 `COORD_CLEANUP 2`를 할 수 있다.

## AC
- `PW verify-record --wave 2 --current --manifest tests/.tmp/a11y-wave/components.json && PW validate-manifest --collected tests/.tmp/axe-final/collected.json --manifest tests/.tmp/a11y-wave/components.json && GS && AXE --assert-no-violations --collected tests/.tmp/axe-current.json && AXE --assert-empty && AXE --check-plan --require-empty && FULL && VS && XGATE 8 tests/fixtures/axe-baseline.json,tests/fixtures/axe-remediation-plan.json tests/fixtures/axe-baseline.json,tests/fixtures/axe-remediation-plan.json`
