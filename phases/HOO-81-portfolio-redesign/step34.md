# Step 34 — axe-baseline-projection

- 목적: §6.2 step 34.
- 17분 / 선행 0~33 / 공통 §9 / gate GATE
- 허용(exact): `tests/helpers/axe.js`, `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 디렉터리)
- 추가 금지: 이전 helper 동작, 실제 fixtures

## 작업
1. `SNAP 34`
2. `projectEntry`(7필드만, targets·selectors 정렬·중복 제거, 누락·key 불일치 throw), `compareCollectedBaseline`(key 중복 throw, 입력 불변), CLI `--check-baseline-match`(기본 `tests/fixtures/axe-collected.json`·`tests/fixtures/axe-baseline.json`, ok면 stdout `baseline-match: OK`, 파일 없음·JSON 오류 1).
3. spec(같은 entry 2개 기준): 같음 ok·다섯 `[]`; collected에만 entry → missingEntries; baseline에만 → extraEntries; collected target 추가 → missingTargets `[{key, target}]`; baseline target 추가 → extraTargets; impact 다름 → `[{key, field: 'impact'}]`, selectors 다름 → `[{key, field: 'selectors'}]`; 중복 throw; projectEntry 계약; CLI 5종 불일치 각각 exit 1·정확한 줄, 일치 0, collected 없음·baseline JSON 오류 1.

## AC
- `T axe-helper.spec.js && FULL && VS && GATE 34 tests/helpers/axe.js,tests/specs/axe-helper.spec.js`
