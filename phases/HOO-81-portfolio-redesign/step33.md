# Step 33 — axe-baseline-regression

- 목적: §6.2 step 33, §6.4 `validateBaseline`.
- 19분 / 선행 0~32 / 공통 §9 / gate GATE
- 허용(exact): `tests/helpers/axe.js`, `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 디렉터리)
- 추가 금지: step 28·32 동작, 실제 fixtures

## 작업
1. `SNAP 33`
2. spec(desktop-dark): 통과 — §6.4 정상 예, FIXTURE_OK, `[]`, text-change만 entry(`fixFiles: []`); §6.4 오류 예 A·B·C 정확한 배열; 그 밖 각 한 항목 `baseline: not-array`(`{}`), `baseline[0]: not-object`, `fields missing=[impact] extra=[]`, `bad-scenario`, `bad-project`, `bad-ruleId`(`a:b`), `key-mismatch`, `bad-impact`(`minor`), `targets empty`, `targets duplicate`, `targets unsorted`, `selectors unsorted`, `fixes count`, `fixes[0]: target-mismatch`, `fixes[0]: bad-fixKind`, `baseline: duplicate-key {key}`, `baseline: unsorted`; checkRegression 새 key·새 target·사라짐 허용·dark 전용 target이 light에 나오면 new-key·입력 불변; resolveBaselineMode baseline 있음 `check`, 없음+collected+plan 없음 `pending`, 없음+collected 없음 throw, 없음+collected+plan throw, `AXE_ALLOW_MISSING_BASELINE='1'`이어도 collected 없으면 throw; loadBaseline 없음·깨짐·`{}` throw; `--assert-empty` `[]` 0, `[{}]`·`{}`·깨짐·없음 1.

## AC
- `T axe-helper.spec.js && FULL && VS && GATE 33 tests/helpers/axe.js,tests/specs/axe-helper.spec.js`
