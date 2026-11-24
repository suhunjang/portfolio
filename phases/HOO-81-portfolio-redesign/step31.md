# Step 31 — axe-baseline-regression

- 목적: §8.5 baseline schema 검증(`validateBaseline`), 회귀 판정, 분류 대기 계약.
- 예상 19분 / 선행 0~30 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §8.3(step 31, 실행 모드), §8.5(전체)
- tracked 허용(exact): `tests/helpers/axe.js`(추가만), `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 디렉터리)
- 금지: §15.7, step 26·30 동작, 실제 fixtures

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step31`
2. 설계 §8.3 step 31 계약. `validateBaseline`은 §8.5 규칙·오류 형식 그대로.
3. spec(desktop-dark):
   - 통과: §8.5 정상 예 → `[]`; `[]` → `[]`; text-change fix(`fixFiles: []`)만 있는 entry와 entry `fixFiles: []` → `[]`
   - §8.5 오류 예 A → 정확히 `["baseline[0]: fields missing=[] extra=[note]"]`
   - §8.5 오류 예 B(fixKind만 `css-rule`, fix·entry fixFiles 유지) → 정확히 `["baseline[0].fixes[0]: fixFiles-mismatch"]`
   - §8.5 오류 예 C(fix 정상, entry `fixFiles`만 `["css/style.css"]`) → 정확히 `["baseline[0]: fixFiles union-mismatch"]`
   - 그 밖 각각 한 항목: `baseline: not-array`(`{}`), `baseline[0]: not-object`, `fields missing=[impact] extra=[]`, `bad-scenario`, `bad-project`, `bad-ruleId`(`a:b`), `key-mismatch`, `bad-impact`(`minor`), `targets empty`, `targets duplicate`, `targets unsorted`, `selectors unsorted`, `fixes count`, `fixes[0]: target-mismatch`, `fixes[0]: bad-fixKind`, `baseline: duplicate-key {key}`, `baseline: unsorted`
   - checkRegression: 새 key → `new-key:{key}`, 기존 key의 새 target → `new-target:{key}:{target}`, 사라짐 허용, `page:desktop-dark`에만 있는 target이 `page:desktop-light`에 나오면 new-key, 입력 불변
   - resolveBaselineMode: baseline 있음 `check`; baseline 없음+collected 있음+plan 없음 `pending`; baseline 없음+collected 없음 throw; baseline 없음+collected+plan throw; `process.env.AXE_ALLOW_MISSING_BASELINE='1'`이어도 collected 없으면 throw
   - loadBaseline 없음·잘못된 JSON·`{}` throw; CLI `--assert-empty` `[]` 0, `[{}]`·`{}`·잘못된 JSON·없음 1

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step31.json --allow tests/helpers/axe.js,tests/specs/axe-helper.spec.js` → exit 0
