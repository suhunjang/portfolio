# Step 1 — scope-snapshot-schema

- 목적: 비교 도구의 projectRoot·경로 유형 검사와 안전 읽기, status 파싱, 최상위 JSON token scanner, strict schema loader를 만들고, 모든 schema 범주와 projectRoot 유형 거부에서 Python S·C와 같은 판정임을 실행으로 증명한다. 종료 검사는 S `reused` + inline C.
- 예상 20분 / 선행 0 / 공통 절차 설계 §15
- read-first: 설계 §11.4(직렬화), §11.7(projectRoot 유형, 경로 유형 계약, schema, `scanJsonTopLevel`, S, C, 설계 블록 추출 규칙, S·C exec harness, 비교 도구 step 1, 테스트 격리), §12(합성 저장소 예외)
- tracked 허용(exact): `tests/scripts/scope-snapshot.mjs`(신규, step 1 API만), `tests/specs/scope-snapshot-schema.spec.js`(신규)
- runtime: R0(합성 저장소 `tests/.tmp/synthetic-repos/<pid>/`, `<pid>-link`, `<pid>-file` 포함)
- 금지: §15.7, 상태 수집·identity·판정·CLI(step 2·5), 정규식으로 schemaVersion 찾기, S·C 본문 변경, 실제 저장소의 비runtime 경로에 symlink·FIFO 생성

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step1`
2. `scope-snapshot.mjs`: 설계 §11.7 비교 도구 step 1 API(상수, `UnsafePathError`, `checkRoot`, `pathKind`, `checkPath`, `readRegular`, `parseStatusZ`, `statusXyMap`, `scanJsonTopLevel`, `isSchemaVersion1(value, token)`, `loadStartSnapshot`). fs 주입 가능, snapshot 생성·수정 기능 없음, CLI 없음.
3. `scope-snapshot-schema.spec.js` (node 전용, desktop-dark만, subprocess timeout 10초)
   - projectRoot 유형(가짜 fs): root lstat이 symlink → `checkRoot`·`checkPath`·`loadStartSnapshot` 모두 `symlink:{root}`, regular file → `non-regular:{root}`, 없음 → `missing:{root}`; 가짜 fs 호출 기록이 root에 대한 `lstatSync` 1회뿐(하위 lstat·open·readdir 없음)
   - projectRoot 유형(합성 저장소): `tests/.tmp/synthetic-repos/<pid>/`에서 `git -C <dir> init -q`만 실행하고 그 안에 정상 형식 `tests/.tmp/start-snapshot-parity-1.json`을 둔다. 옆에 `<pid>-link → <pid>` symlink와 regular file `<pid>-file`을 만든다. JS `loadStartSnapshot('tests/.tmp/start-snapshot-parity-1.json', { root: <link> })` → `unsafe path: symlink:<link>`, root `<file>` → `non-regular:<file>`, 기록용 fs에 root 외 호출 없음. S·C는 설계 S·C exec harness로(cwd `<dir>`, `rev-parse --show-toplevel` 결과만 `<link>` 또는 `<file>`로 대체, S 본문은 `tests/scripts/start-snapshot.py`, C 본문은 설계 블록 추출) 실행 → 각각 `unsafe path: symlink:<link>` / `non-regular:<file>`, 기록상 `os.lstat`은 root 경로 1회뿐이고 `os.walk`·`os.open`·`os.makedirs`·`open` 호출과 그 밖 git 호출 0, 합성 디렉터리 목록·bytes·mtime 불변, snapshot·after.z 미생성. 끝나면 셋 모두 삭제
   - `checkPath`(가짜 fs): 조상 symlink → `symlink:{조상}`, 조상 regular file → `non-regular:{조상}`, 조상 missing + leaf 허용 missing → null, 필수 file이 missing → `missing:`, leaf dir·FIFO·socket·symlink → `non-regular:`/`symlink:`; 호출 기록이 `lstatSync`뿐
   - `readRegular`(가짜 fs): `openSync` flags에 `O_NOFOLLOW`·`O_NONBLOCK` 포함, fstat이 FIFO면 `UnsafePathError('non-regular:…')`
   - `parseStatusZ`: ` M CLAUDE.md`, `?? docs/a.md` 정확; `R  new.md`+NUL+`old.md` → origPath, `statusXyMap`에 두 경로 `R `; 빈 입력 `[]`; 길이 < 4 레코드·세 번째 바이트가 공백 아님·origPath 누락 throw
   - `scanJsonTopLevel`: `{"schemaVersion":1}` → `[{key:'schemaVersion', token:'1'}]`; `{"a":{"schemaVersion":1},"schemaVersion":1.0}` → 최상위 token `1.0`만; `{"s":"\"schemaVersion\": 1","schemaVersion":1e0}` → 문자열 안 무시, token `1e0`; `{"a":[{"b":"},"}],"schemaVersion" : 1 }` → `1`; 최상위 중복(어느 순서든)·이스케이프 key `schema\u0056ersion`과 평문 공존·중첩 중복 → duplicate throw; `[1]` → `[]`; 입력 불변
   - `isSchemaVersion1`: (`1`, `'1'`) true; (`2`,`'2'`), (`true`,`'true'`), (`'1'`,`'"1"'`), (`1`,`'1.0'`), (`1`,`'1e0'`) false
   - S·loader 동일 판정(실제 저장소, `workers: 1` 직렬): S로 정상 `parity-<A>`를 만들고 원문 텍스트 변형으로 `parity-<n>` 파일들을 만든다(`stepId`는 새 이름으로 맞춤). 각 파일에 대해 `python3 -I tests/scripts/start-snapshot.py parity-<n>`(재사용 분기)와 `loadStartSnapshot`을 실행해 둘 다 거부하고 `bad start snapshot:` 뒤 범주가 같으며 파일 sha256 불변. 변형: 깨진 JSON, `files` 값 `NaN`(`invalid json`); 최상위 중복 schemaVersion(마지막 `1.0`, 마지막 `1e0`, 처음 `1.0`·마지막 `1`)과 `harness` 안 중복 key(`invalid json`); 키 누락·여분(`keys`); schemaVersion `2`·`true`·`1.0`·`1e0`·`"1"`, 최상위 `1.0` + `harness`·`files` 안 `"schemaVersion": 1`(`schemaVersion`); statusZHex `zz`·홀수 `0`·대문자(`statusZHex`); 잘린 레코드 `3f3f`(`status parse`); xy 경로 추가·값 변경(`xy`); files 값 `abc`·대문자 64hex·숫자(`files`); status 비SKIP 경로를 files에서 제거(`files/status`). 정상 사본은 loader가 반환하고 S는 `reused`
   - loader: 파일 없음 → `unsafe path: missing:`, stepId≠파일명·형식 오류 throw
   - snapshot 파일 자체 symlink는 step 3이 검증한다

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-schema.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step1` (전체는 `workers: 1` 직렬, 마지막은 `reused`)
2. 범위 gate: `python3 -I - step1 'tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-schema.spec.js' 'tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-schema.spec.js' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
