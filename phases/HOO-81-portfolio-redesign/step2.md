# Step 2 — scope-snapshot-parse

- 목적: status parser, 최상위 JSON token scanner, schemaVersion 판정 함수(모두 순수)와 단위 검증.
- 예상 15분 / 선행 0~1 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.7(schema, `scanJsonTopLevel`, S의 `parse_status`, 비교 도구 step 2)
- tracked 허용(exact): `tests/scripts/scope-snapshot.mjs`(추가만), `tests/specs/scope-snapshot-parse.spec.js`(신규)
- runtime: R0
- 금지: §15.7, step 1 함수 동작, loader(step 3), 정규식으로 schemaVersion 찾기, 파일 시스템 접근

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step2`
2. `scope-snapshot.mjs`에 step 2 API(`parseStatusZ`, `statusXyMap`, `scanJsonTopLevel`, `isSchemaVersion1(value, token)`) 추가. 순수 함수만.
3. `scope-snapshot-parse.spec.js` (node 전용, desktop-dark만)
   - `parseStatusZ`: ` M CLAUDE.md`, `?? docs/a.md` 정확; `R  new.md`+NUL+`old.md` → origPath, `statusXyMap`에 두 경로 `R `; 빈 입력 `[]`; 끝 NUL 하나 허용; 길이 < 4 레코드·세 번째 바이트가 공백 아님·origPath 누락·빈 origPath throw
   - `scanJsonTopLevel`: `{"schemaVersion":1}` → `[{key:'schemaVersion', token:'1'}]`; `{"a":{"schemaVersion":1},"schemaVersion":1.0}` → 최상위 token `1.0`만; `{"s":"\"schemaVersion\": 1","schemaVersion":1e0}` → 문자열 안 무시, token `1e0`; `{"a":[{"b":"},"}],"schemaVersion" : 1 }` → `1`; 객체·배열 값은 전체 원문이 token; 최상위 중복(어느 순서든)·이스케이프 key `schema\u0056ersion`과 평문 공존·중첩 중복 → duplicate throw; `[1]` → `[]`
   - `isSchemaVersion1`: (`1`, `'1'`) true; (`2`,`'2'`), (`true`,`'true'`), (`'1'`,`'"1"'`), (`1`,`'1.0'`), (`1`,`'1e0'`) false
   - 모든 함수가 입력을 바꾸지 않는다

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-parse.spec.js scope-snapshot-paths.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step2` (마지막은 `reused`)
2. 범위 gate: `python3 -I - step2 'tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-parse.spec.js' 'tests/specs/scope-snapshot-parse.spec.js' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
