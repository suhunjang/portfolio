# Step 1 — scope-snapshot-schema

- 목적: 비교 도구의 status 파싱, 최상위 JSON token scanner, strict schema loader를 만들고 모든 schema 범주에서 Python S와 같은 판정임을 실행으로 증명한다. 종료 검사는 S `reused` + inline C.
- 예상 18분 / 선행 0 / 공통 절차 설계 §15
- read-first: 설계 §11.4(직렬화), §11.7(schema, `scanJsonTopLevel`, S, C, 비교 도구 step 1, 테스트 격리)
- tracked 허용(exact): `tests/scripts/scope-snapshot.mjs`(신규, step 1 API만), `tests/specs/scope-snapshot-schema.spec.js`(신규)
- runtime: R0
- 금지: §15.7, 상태 수집·identity·판정·CLI(step 2·4), 정규식으로 schemaVersion 찾기, 실제 저장소에 새 비runtime 파일·symlink 생성

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step1`
2. `scope-snapshot.mjs`: 설계 §11.7 비교 도구 step 1 API(상수, `parseStatusZ`, `statusXyMap`, `scanJsonTopLevel`, `isSchemaVersion1(value, token)`, `loadStartSnapshot`). fs 주입 가능, snapshot 생성·수정 기능 없음, CLI 없음.
3. `scope-snapshot-schema.spec.js` (node 전용, desktop-dark만)
   - `parseStatusZ`: ` M CLAUDE.md`, `?? docs/a.md` 정확; `R  new.md`+NUL+`old.md` → origPath, `statusXyMap`에 두 경로 `R `; 빈 입력 `[]`; 길이 < 4 레코드·세 번째 바이트가 공백 아님·origPath 누락 throw
   - `scanJsonTopLevel`: `{"schemaVersion":1}` → `[{key:'schemaVersion', token:'1'}]`; `{"a":{"schemaVersion":1},"schemaVersion":1.0}` → 최상위 schemaVersion token `1.0`만(중첩 무시); `{"s":"\"schemaVersion\": 1","schemaVersion":1e0}` → 문자열 안 무시, token `1e0`; `{"a":[{"b":"},"}],"schemaVersion" : 1 }` → `1`; `{"schemaVersion":1,"schemaVersion":1.0}`·`{"schemaVersion":1.0,"schemaVersion":1}` → duplicate throw; 이스케이프 key `schema\u0056ersion`과 평문 key 공존 → duplicate throw; 중첩 `{"a":{"x":1,"x":2}}` → duplicate throw; `[1]` → `[]`; 입력 불변
   - `isSchemaVersion1`: (`1`, `'1'`) true; (`2`, `'2'`), (`true`, `'true'`), (`'1'`, `'"1"'`), (`1`, `'1.0'`), (`1`, `'1e0'`) false
   - S·loader 동일 판정(실제 저장소 읽기 전용, `workers: 1` 직렬): S로 정상 `parity-<A>`를 만들고 원문 텍스트 변형으로 `parity-<n>` 파일들을 만든다(`stepId`는 새 이름으로 맞춤). 각 파일에 대해 `python3 -I tests/scripts/start-snapshot.py parity-<n>`(재사용 분기)와 `loadStartSnapshot`을 실행해 둘 다 거부하고 `bad start snapshot:` 뒤 범주가 같으며 파일 sha256 불변. 변형: 깨진 JSON, `files` 값 `NaN`(`invalid json`); 최상위 중복 schemaVersion(마지막 `1.0`, 마지막 `1e0`, 처음 `1.0`·마지막 `1`)과 `harness` 안 중복 key(`invalid json`); 키 누락·여분(`keys`); schemaVersion `2`·`true`·`1.0`·`1e0`·`"1"`, 최상위 `1.0` + `harness`·`files` 안에 `"schemaVersion": 1`(`schemaVersion`); statusZHex `zz`·홀수 `0`·대문자 hex(`statusZHex`); 잘린 레코드 `3f3f`(`status parse`); xy에 없는 경로 추가·값 변경(`xy`); files 값 `abc`·대문자 64hex·숫자(`files`); status 비SKIP 경로를 files에서 제거(`files/status`). 정상 사본은 loader가 반환하고 S는 `reused`
   - snapshot 파일 symlink: `tests/.tmp/start-snapshot-parity-<m>.json`을 정상 사본(`tests/.tmp` 안)으로 가리키는 symlink로 만들면 S exit ≠ 0·stderr `unsafe path: symlink:tests/.tmp/start-snapshot-parity-<m>.json`, loader `unsafe path: symlink:` throw, 대상 파일 sha256 불변. 끝나면 링크와 사본 삭제
   - loader: 파일 없음 throw, stepId≠파일명·형식 오류 throw

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-schema.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step1` (전체는 `workers: 1` 직렬, 마지막은 `reused`)
2. 범위 gate: `python3 -I - step1 'tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-schema.spec.js' 'tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-schema.spec.js' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
