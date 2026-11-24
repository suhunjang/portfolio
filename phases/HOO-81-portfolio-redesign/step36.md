# Step 36 — axe-plan-executable

- 목적: §6.2 step 36.
- 15분 / 선행 0~35 / 공통 §9 / gate GATE
- 허용(exact): `tests/helpers/axe.js`, `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 디렉터리)
- 추가 금지: 이전 helper 동작, 실제 fixtures

## 작업
1. `SNAP 36`
2. spec(step 35 상수 재사용): `{ groups: [] }` → `[]`; FIXTURE_OK+정상 예 → `[]`; FIXTURE_THEMES+blocked true → 정확히 `["blocked-group:career-kicker-contrast"]`; text-change 하나뿐 baseline+그 그룹(blocked, fixFiles `[]`) → `blocked-group:{id}`·`text-change:{id}:{key}:{target}`·`empty-fixfiles:{id}`; 혼합 → blocked 관련만; 입력 불변; CLI 빈 0·가능만 0·blocked 1(첫 줄 `Harness 재계획 필요: 실행 불가 remediation 그룹`)·plan 없음·baseline JSON 오류 1.

## AC
- `T axe-helper.spec.js && FULL && VS && GATE 36 tests/helpers/axe.js,tests/specs/axe-helper.spec.js`
