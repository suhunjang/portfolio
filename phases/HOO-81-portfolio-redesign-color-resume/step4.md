# Color-resume Step 4 — a11y-wave-verify

- 존재 이유: coordinator wave 2(manifest shard별 direct Claude worktree worker)의 integration을 검증한다. 위반 0을 확인한 뒤 baseline과 plan을 빈 상태로 확정한다.
- 시간: agent 예상 ≤20분, Harness hard timeout 30분. gate: `XGATE 4`.
- 선행: step 0~3과 coordinator wave 2. wave 2 완료 조건은 runtime·external record가 있고 integration commit이 HEAD인 것이다. `shards: []`였다면 coordinator가 빈 lane 목록 record를 만들고 integration commit은 parallelBase와 같다.
- 공통 규칙: 원 §9 + §C1·§C7.
- 허용(exact): `tests/fixtures/axe-baseline.json`, `tests/fixtures/axe-remediation-plan.json`(둘 다 신규)
- runtime: R0 + `tests/.tmp/axe-current.json`, `tests/.tmp/parallel/idx-*`
- 추가 금지: 사이트·helper·spec 수정, 위반이 남은 상태에서 baseline·plan 작성, manifest 밖 변경 수용

## 작업
1. `XSNAP 4`. record가 없으면 `wave-record-missing`으로 fail-closed한다.
2. `PW verify-record --wave 2 --runtime tests/.tmp/parallel/wave-2.json --external <SCR>/record-wave-2.json --manifest tests/.tmp/a11y-wave/components.json`
3. `PW validate-manifest`를 다시 실행하고 `GS`를 돌린다. 색 변경이 상수의 정확한 `to`뿐인지 확인하기 위해서다.
4. `COLLECT_CHAIN --out tests/.tmp/axe-current.json && AXE --assert-no-violations --collected tests/.tmp/axe-current.json`. 실패하면 남은 target을 보고하고 중단한다. 파일은 쓰지 않는다.
5. baseline과 plan을 쓴다.
   - baseline: 정확히 `[]` + 끝 개행
   - plan: 정확히 `{ "groups": [] }`을 2칸 들여쓰기 + 끝 개행으로
6. 아래 AC가 PASS한 뒤에만 coordinator가 wave 2 cleanup을 할 수 있다.

## AC
- `PW verify-record --wave 2 --runtime tests/.tmp/parallel/wave-2.json --external <SCR>/record-wave-2.json --manifest tests/.tmp/a11y-wave/components.json && PW validate-manifest --collected tests/.tmp/axe-final/collected.json --manifest tests/.tmp/a11y-wave/components.json && GS && AXE --assert-no-violations --collected tests/.tmp/axe-current.json && AXE --assert-empty && AXE --check-plan --require-empty && FULL && VS && XGATE 4 tests/fixtures/axe-baseline.json,tests/fixtures/axe-remediation-plan.json tests/fixtures/axe-baseline.json,tests/fixtures/axe-remediation-plan.json`
