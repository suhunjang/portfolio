# Color-resume Step 3 — a11y-wave-verify

- 존재 이유: coordinator wave 2(manifest shard별 direct Claude worktree worker, §C4·§C5)의 canonical integration을 검증하고, 위반 0을 확인한 뒤 baseline·plan을 빈 상태로 확정한다.
- ≤25분 / 선행 0~2 + coordinator wave 2 완료(`tests/.tmp/parallel/wave-2.json`, integration commit = HEAD; manifest `shards: []`였다면 coordinator가 빈 wave record를 기록) / 공통 원 §9 + §C1·§C7 / gate `XGATE 3`
- 허용(exact): `tests/fixtures/axe-baseline.json`, `tests/fixtures/axe-remediation-plan.json`(신규)
- runtime: R0 + `tests/.tmp/axe-current.json`
- 추가 금지: 사이트·helper·spec 수정, 위반이 남은 상태에서 baseline·plan 작성, manifest 밖 변경 수용

## 작업
1. `XSNAP 3` → `WAVE_CHECK 2`(§C6; record 없음이면 `wave-record-missing` fail-closed).
2. `GS`(색 변경이 `HOO81_COLOR_V52_ALLOW`의 정확한 `to`뿐인지 guard로 확인).
3. `COLLECT_CHAIN --out tests/.tmp/axe-current.json && AXE --assert-no-violations --collected tests/.tmp/axe-current.json`. 실패면 남은 target 보고·중단(파일 미작성).
4. baseline = 정확히 `[]` + 끝 개행, plan = 정확히 `{ "groups": [] }` 2칸 들여쓰기 + 끝 개행.

## AC
- `WAVE_CHECK 2 && GS && AXE --assert-no-violations --collected tests/.tmp/axe-current.json && AXE --assert-empty && AXE --check-plan --require-empty && FULL && VS && XGATE 3 tests/fixtures/axe-baseline.json,tests/fixtures/axe-remediation-plan.json tests/fixtures/axe-baseline.json,tests/fixtures/axe-remediation-plan.json`(첫 명령 stdout 접두 `wave-check 2: OK`)
