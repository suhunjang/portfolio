# Step 27 — axe-baseline-regression

- 목적: §8.5 baseline schema 검증(`validateBaseline`), 회귀 판정, 분류 대기 계약.
- 예상 19분 / 선행 0~26 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §8.3(step 27, 실행 모드), §8.5(전체)
- tracked 허용(exact): `tests/helpers/axe.js`(추가만), `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 디렉터리)
- 금지: §15.7, step 22·26 동작, 실제 fixtures

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step27`
2. 설계 §8.3 step 27 계약. `validateBaseline`은 §8.5 규칙·오류 형식 그대로.
3. spec(desktop-dark): §8.5 정상 예 → `[]`, `[]` → `[]`; §8.5 오류 예 2종의 정확한 메시지; 그 밖 `not-array`, `not-object`, 필드 누락, scenario·project·ruleId·impact 오류, key-mismatch, targets empty·duplicate·unsorted, selectors unsorted, fixes count, fix target-mismatch·bad-fixKind, text-change `fixFiles: []`이고 entry `fixFiles: []` 통과, duplicate-key, unsorted; checkRegression new-key/new-target·사라짐 허용·입력 불변; resolveBaselineMode 4상태 + 환경변수 무시; loadBaseline 오류 3종; CLI `--assert-empty`.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step27.json --allow tests/helpers/axe.js,tests/specs/axe-helper.spec.js` → exit 0
