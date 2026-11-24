# Step 31 — axe-regression-prune

- 목적: plan 수정 전 회귀 gate와 plan 정리 도구.
- 예상 19분 / 선행 0~30 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §8.3(step 31, REGRESSION_GATE)
- tracked 허용(exact): `tests/helpers/axe.js`(추가만), `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 디렉터리 사본만)
- 금지: §15.7, 이전 helper 동작, 실제 fixtures

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step31`
2. 설계 §8.3 step 31 계약 구현.
3. spec(desktop-dark): checkCollectedRegression 5사례; prunePlan 제거·삭제·부분집합·id 유지·추가 없음·blocked 불변·입력 불변; CLI check-regression 0/1; prune-plan 회귀·파일 오류 시 exit 1·bytes·mtime 불변, 체인 실패 시 불변, 정상 시 target 제거·검증 통과.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step31.json --allow tests/helpers/axe.js,tests/specs/axe-helper.spec.js` → exit 0
