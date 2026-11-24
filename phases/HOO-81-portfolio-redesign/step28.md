# Step 28 — axe-baseline-projection

- 목적: collected↔baseline 투영과 양방향 일치 검사.
- 예상 17분 / 선행 0~27 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §8.3(step 28), §8.5
- tracked 허용(exact): `tests/helpers/axe.js`(추가만), `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 디렉터리)
- 금지: §15.7, 이전 helper 동작, 실제 fixtures

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step28`
2. 설계 §8.3 step 28 계약(투영은 §8.5 앞 7필드).
3. spec(desktop-dark): projectEntry; compareCollectedBaseline 6결과·중복 throw·입력 불변; CLI 일치 0·불일치 5종 1·파일 오류 1.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step28.json --allow tests/helpers/axe.js,tests/specs/axe-helper.spec.js` → exit 0
