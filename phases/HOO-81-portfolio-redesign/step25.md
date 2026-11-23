# Step 25 — axe-baseline-projection

- 목적: collected↔baseline 투영과 양방향 일치 검사.
- 예상 17분 / 선행 0~24 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §8.3(entry key, step 25, fixture)
- tracked 허용(exact): `tests/helpers/axe.js`(추가만), `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 디렉터리)
- 금지: §15.7, step 19·23·24 동작, 실제 fixtures

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step25`
2. 설계 §8.3 step 25 계약 구현.
3. spec(desktop-dark): projectEntry 7필드만·정렬·중복 제거·key 불일치/누락 throw; compareCollectedBaseline 같은 내용 ok, collected만 entry → missingEntries, baseline만 → extraEntries, missingTargets, extraTargets, impact·selectors 차이 → fieldMismatches, 중복 key throw, 입력 불변; CLI 일치 0, 다섯 불일치 각각 1, collected 없음·baseline JSON 오류 1.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step25.json --allow tests/helpers/axe.js,tests/specs/axe-helper.spec.js` → exit 0
