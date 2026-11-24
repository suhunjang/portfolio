# Step 36 — axe-plan-executable

- 목적: §6.2 step 36 — step 35 validation 통과를 전제로 blocked 그룹만 거부.
- 15분 / 선행 0~35 / 공통 §9 / gate GATE
- 허용(exact): `tests/helpers/axe.js`, `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 디렉터리)
- 추가 금지: 이전 helper 동작, 실제 fixtures, `requiresColorChange` 재판정(step 35 몫)

## 작업
1. `SNAP 36`
2. `validateRemediationExecutable(plan, baseline)`, CLI `--check-executable`.
3. spec(step 35 상수 재사용; 모든 입력은 먼저 `validateRemediationPlan` → `[]` 확인 후 호출): `{ groups: [] }` → `[]`; FIXTURE_OK+정상 → `[]`; FIXTURE_RULE_PLAIN+blocked false → `[]`; FIXTURE_THEMES+blocked true → 정확히 `["blocked-group:career-kicker-contrast"]`; FIXTURE_RULE_COLOR+blocked true → `["blocked-group:career-kicker-rule"]`; text-change 하나뿐 baseline(false)+그 그룹(blocked, `text change excluded`, fixFiles `[]`) → `blocked-group:{id}`·`text-change:{id}:{key}:{target}`·`empty-fixfiles:{id}`; 혼합 → blocked 관련만; 입력 불변.
4. 잘못 분류 순서: FIXTURE_RULE_COLOR + blocked false plan 파일에 `AXE --check-plan` → exit 1(`groups[0]: blocked-required`)이므로 `--check-plan && --check-executable` 체인은 executable 전에 멈춤을 subprocess로 확인.
5. CLI: 빈 0·가능만 0·blocked 1(첫 줄 `Harness 재계획 필요: 실행 불가 remediation 그룹`)·plan 없음·baseline JSON 오류 1.

## AC
- `T axe-helper.spec.js && FULL && VS && GATE 36 tests/helpers/axe.js,tests/specs/axe-helper.spec.js`
