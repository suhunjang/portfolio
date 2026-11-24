# Step 38 — axe-regression-prune

- 목적: §6.2 step 38, §6.5 prune.
- 19분 / 선행 0~37 / 공통 §9 / gate GATE
- 허용(exact): `tests/helpers/axe.js`, `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 사본만)
- 추가 금지: 이전 helper 동작, 실제 fixtures

## 작업
1. `SNAP 38`
2. `checkCollectedRegression`(`bad-key:`, `new-key:`, `new-target:`), `prunePlan`, CLI `--check-regression`, `--prune-plan`.
3. spec: 회귀 같음 `[]`·새 key·새 target·key 불일치·사라짐 `[]`; prune 결과 validateRemediationPlan(coverage false) 통과·제거·fixFiles 재계산·빈 그룹 삭제·순서 유지·추가 없음·입력 불변; CLI sha256·mtime 기록 → new-target·collected 없음·baseline JSON 오류 시 1·불변, `sh -c '<check-regression> && <prune-plan>'` 회귀 실패 시 불변, 회귀 없음+사라진 1개 → 0·제거.

## AC
- `T axe-helper.spec.js && FULL && VS && GATE 38 tests/helpers/axe.js,tests/specs/axe-helper.spec.js`
