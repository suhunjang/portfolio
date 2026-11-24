# Step 28 — axe-remediation-plan-schema

- 목적: remediation plan 스키마 검증.
- 예상 17분 / 선행 0~27 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §8.3(step 28, plan 규칙)
- tracked 허용(exact): `tests/helpers/axe.js`(추가만), `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 디렉터리)
- 금지: §15.7, 이전 helper 동작, 실제 fixtures

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step28`
2. 설계 §8.3 step 28 계약 구현.
3. spec(desktop-dark): id 통과·거부 목록, 중복 id, 정상, coverage, estMinutes 21·0, fixFiles 불일치, 그룹 간 중복, text-change 비blocked, difficulty, requireEmpty; CLI 정상 0·오류 6종 1·`--require-empty` 0/1.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step28.json --allow tests/helpers/axe.js,tests/specs/axe-helper.spec.js` → exit 0
