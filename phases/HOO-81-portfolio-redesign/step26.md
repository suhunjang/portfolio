# Step 26 — axe-baseline-regression

- 목적: baseline 스키마·회귀 판정·분류 대기 baseline 계약.
- 예상 19분 / 선행 0~25 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §8.3(entry key, step 26, 실행 모드)
- tracked 허용(exact): `tests/helpers/axe.js`(추가만), `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 디렉터리)
- 금지: §15.7, step 21·25 동작, 실제 fixtures

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step26`
2. 설계 §8.3 step 26 계약 구현(`resolveBaselineMode`는 환경변수를 읽지 않음).
3. spec(desktop-dark): validateBaseline 통과·거부 사례(key·중복·정렬·kind별 파일 5종·빈 배열·여분·합집합·누락·범위 밖·알 수 없는 kind); checkRegression new-key/new-target·사라짐 허용·입력 불변; resolveBaselineMode 4상태 + 환경변수 무시; loadBaseline 오류 3종; CLI `--assert-empty`.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step26.json --allow tests/helpers/axe.js,tests/specs/axe-helper.spec.js` → exit 0
