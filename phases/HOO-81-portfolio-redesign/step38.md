# Step 38 — axe-regression-prune

- 목적: §6.2 step 38 회귀 gate와 §6.5 prune(제거 → 빈 그룹 삭제 → `requiredBlockReason` 재사용으로 fixFiles·blocked·reason 재계산, manual block 보존).
- 20분(작성 11, 단독 3, FULL 4, VS·gate 2) / 선행 0~37 / 공통 §9 / gate GATE
- 허용(exact): `tests/helpers/axe.js`, `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 사본만)
- 추가 금지: 이전 helper 동작(`requiredBlockReason`·`validateRemediationPlan` 재구현 금지, 재사용만), 실제 fixtures

## 작업
1. `SNAP 38`
2. `checkCollectedRegression`(`bad-key:`, `new-key:`, `new-target:`), `prunePlan(plan, collected, baseline)`(§6.5 prune (1)~(6) 그대로), CLI `--check-regression`, `--prune-plan`.
3. spec(step 33 fixture 상수; collected는 남길 target만 담은 MergedEntry 배열; 모든 prune 결과에 `validateRemediationPlan(결과, baseline)` → `[]`):
   - 회귀: 같음 `[]`·새 key·새 target·key 불일치·사라짐 `[]`
   - 기본: 일부 PlanTarget 제거·남은 targets 순서 유지·fixFiles 재계산·빈 그룹 삭제·id·difficulty·estMinutes·그룹 순서 유지·필드 추가 없음
   - FIXTURE_MIXED `kicker-mixed`(blocked true·`text change excluded; color change excluded (HOO-81 §16.3)`·fixFiles `["css/style.css"]`): (a) `#projects`(text-change) target 제거 → targets `[#career]`, blocked true, reason `color change excluded (HOO-81 §16.3)`, fixFiles `["css/style.css"]`; (b) `#career`(색) target 제거 → targets `[#projects]`, blocked true, reason `text change excluded`, fixFiles `[]`
   - 파생 blocker 소멸: FIXTURE_COLOR_PLAIN 한 그룹(color-contrast·target-size 두 target, blocked true, `color change excluded (HOO-81 §16.3)`, fixFiles `["css/style.css"]`)에서 color-contrast target 제거 → blocked false, reason `""`, fixFiles `["css/style.css"]`
   - manual-only: FIXTURE_RULE_PLAIN `theme-toggle-size` blocked true·`manual hold`에서 target 유지 → blocked true·`manual hold` 그대로; FIXTURE_COLOR_PLAIN에 manual 그룹을 만들 수 없음(필수 reason과 혼합은 validator가 거부)도 확인
   - 기존 false 유지: FIXTURE_RULE_PLAIN blocked false·`""` → 그대로
   - 입력 불변(deep-equal 사본 비교), 같은 입력 두 번 호출 결과 동일
4. CLI: prune 전 sha256·mtime 기록 → new-target·collected 없음·baseline JSON 오류 시 exit 1·불변; `sh -c '<check-regression> && <prune-plan>'` 회귀 실패 시 불변; 회귀 없음+사라진 target 1개 → exit 0·제거·재계산 반영·파일 = `JSON.stringify(plan, null, 2) + '\n'`.

## AC
- `T axe-helper.spec.js && FULL && VS && GATE 38 tests/helpers/axe.js,tests/specs/axe-helper.spec.js`
