# Step 30 — axe-baseline-projection

- 목적: collected↔baseline 투영과 양방향 일치 검사.
- 예상 17분 / 선행 0~29 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §8.3(step 30), §8.5
- tracked 허용(exact): `tests/helpers/axe.js`(추가만), `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 디렉터리)
- 금지: §15.7, 이전 helper 동작, 실제 fixtures

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step30`
2. 구현: `PROJECTION_FIELDS = ['key','scenario','project','ruleId','impact','targets','selectors']`; `projectEntry(entry)`(이 7필드만 남기고 targets·selectors 정렬·중복 제거, 7필드 중 누락 또는 key ≠ makeEntryKey면 throw); `compareCollectedBaseline(collected, baseline)` → `{ ok, missingEntries, extraEntries, missingTargets, extraTargets, fieldMismatches }`:
   - `missingEntries`: collected에만 있는 key 배열(정렬)
   - `extraEntries`: baseline에만 있는 key 배열(정렬)
   - `missingTargets`: 같은 key에서 collected에만 있는 target의 `{ key, target }` 배열((key, target) 정렬)
   - `extraTargets`: 같은 key에서 baseline에만 있는 target의 `{ key, target }` 배열
   - `fieldMismatches`: 같은 key에서 scenario·project·ruleId·impact·selectors 중 다른 필드의 `{ key, field }` 배열(key, 그다음 필드 위 순서)
   - `ok`: 위 다섯 배열이 모두 비었으면 true; 어느 쪽이든 key 중복이면 throw; 입력 불변
   - CLI `--check-baseline-match [--collected 기본 tests/fixtures/axe-collected.json] [--baseline 기본 tests/fixtures/axe-baseline.json]`: ok면 stdout `baseline-match: OK` exit 0, 아니면 stderr에 `missing-entry:{key}`, `extra-entry:{key}`, `missing-target:{key}|{target}`, `extra-target:{key}|{target}`, `field-mismatch:{key}|{field}` 줄을 이 범주 순서로 출력하고 exit 1; 파일 없음·JSON 오류 exit 1
3. spec(desktop-dark, 기준 collected·baseline은 같은 entry 2개):
   - 결과 6종: 같은 내용 → `ok: true`·다섯 배열 `[]`; collected에만 entry → `missingEntries: [key]`; baseline에만 entry → `extraEntries: [key]`; collected entry에 target 추가 → `missingTargets: [{key, target}]`; baseline entry에 target 추가 → `extraTargets: [{key, target}]`; impact 다름 → `fieldMismatches: [{key, field: 'impact'}]`, selectors 다름 → `[{key, field: 'selectors'}]`
   - 중복 key throw; projectEntry 7필드·정렬·throw; 입력 불변
   - CLI 불일치 5종(missing-entry, extra-entry, missing-target, extra-target, field-mismatch) 각각 exit 1과 정확한 stderr 줄; 일치 0; collected 없음·baseline JSON 오류 1

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step30.json --allow tests/helpers/axe.js,tests/specs/axe-helper.spec.js` → exit 0
