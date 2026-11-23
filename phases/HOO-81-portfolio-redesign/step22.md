# Step 22 — axe-regression-prune

- 목적: plan 수정 전 회귀 gate와 plan 정리 도구.
- 예상 19분 / 선행 0~21 / 공통 절차 설계 §15
- read-first: 설계 §8.3(entry key, step 22, REGRESSION_GATE, gate/recheck)
- tracked 허용(exact): `tests/helpers/axe.js`(추가만), `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 디렉터리 사본만, 실제 plan 파일에 쓰지 않음)
- 금지: §15.7, step 12·16~21 동작, 실제 fixtures

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step22`
2. 설계 §8.3 step 22 계약 구현.
3. spec(desktop-dark): checkCollectedRegression 같음 `[]`, 새 key `new-key:`, 새 target `new-target:`, key 불일치 `bad-key:`, 사라짐 `[]`; prunePlan 사라진 target 제거·빈 그룹 삭제·fixFiles 부분집합·id 유지·plan 밖 target 추가 없음·blocked 불변·입력 불변; CLI check-regression 0/1(new-target, baseline 없음, collected 없음); prune-plan 전 sha256·mtime 기록 → new-target이면 exit 1·불변, collected 없음·baseline JSON 오류 exit 1·불변, `sh -c 'node axe.js --check-regression ... && node axe.js --prune-plan ...'` 회귀 실패 시 exit 1·불변, 회귀 없음+사라진 target 1개 exit 0·target 제거·`validateRemediationPlan`(coverage false) 통과.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step22.json --allow tests/helpers/axe.js,tests/specs/axe-helper.spec.js` → exit 0
