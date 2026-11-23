# Step 20 — axe-remediation-plan-schema

- 목적: remediation plan 스키마 검증.
- 예상 17분 / 선행 0~19 / 공통 절차 설계 §15
- read-first: 설계 §8.3(step 20, plan 규칙)
- tracked 허용(exact): `tests/helpers/axe.js`(추가만), `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 디렉터리)
- 금지: §15.7, step 13·17~19 동작, 실제 fixtures

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step20`
2. 설계 §8.3 step 20 계약 구현(target 부분집합은 baseline 전체 canonical 합집합 기준).
3. spec(desktop-dark): id 통과 `color-token-1`, `a`, `x2` / 거부 `Group-1`, `a--b`, `-a`, `a-`, `a_b`, 빈 문자열; 중복 id 거부; 정상 통과; 다른 project의 같은 target을 한 그룹에 한 번 → coverage 통과; 거부 estMinutes 21·0, fixFiles 불일치, 그룹 간 중복, text-change인데 blocked 아님, difficulty 이상, coverage 누락; requireEmpty 빈 통과·그룹 1개 오류; CLI 정상 0, plan 없음·JSON 오류·대문자 id·중복 id·coverage 누락·baseline 없음 1, `--require-empty` 빈 0·그룹 1개 1.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step20.json --allow tests/helpers/axe.js,tests/specs/axe-helper.spec.js` → exit 0
