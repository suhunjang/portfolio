# Step 1 — scope-snapshot-state

- 목적: 비교 도구의 strict schema/parsing과 현재 status+hash 상태 수집을 만들고, 합성 저장소 수집과 실제 저장소 Python S parity를 증명한다. 종료 검사는 inline C.
- 예상 19분 / 선행 0 / 공통 절차 설계 §15
- read-first: 설계 §11.1, §11.4(직렬화), §11.7(규칙, schema, 재시도, S, C, 비교 도구 step 1, 테스트 격리), §12(합성 저장소 예외)
- tracked 허용(exact): `tests/scripts/scope-snapshot.mjs`(신규, step 1 API만), `tests/specs/scope-snapshot-state.spec.js`(신규)
- runtime: R0(합성 저장소 `tests/.tmp/synthetic-repos/<pid>/` 포함)
- 금지: §15.7, 변경 판정·정책 분류·CLI(step 2), 실제 저장소에 새 비runtime 파일 생성

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step1`
2. `scope-snapshot.mjs`: 설계 §11.7 비교 도구 step 1 API(상수, `parseStatusZ`, `statusXyMap`, `loadStartSnapshot` strict schema, `hashPath`, `walkTests`, `takeCurrent` with `root`). git·fs 주입 가능, Git 읽기만, snapshot 생성·수정 기능 없음, CLI 없음.
3. `scope-snapshot-state.spec.js` (node 전용, desktop-dark만)
   - `parseStatusZ`: ` M CLAUDE.md`, `?? docs/a.md` 정확; `R  new.md`+NUL+`old.md` → origPath, `statusXyMap`에 두 경로 `R `; 빈 입력 `[]`; 길이 < 4 레코드·세 번째 바이트가 공백 아님·origPath 누락 throw
   - `loadStartSnapshot`(`parity-{숫자}` 파일, S로 만든 정상 snapshot을 변형): 정상 반환; throw — 파일 없음, 깨진 JSON, 키 누락·여분, schemaVersion 2, stepId≠파일명, stepId 형식 오류, statusZHex `zz`·홀수·대문자, 잘린 레코드, xy≠status 파싱, files 값 `abc`·대문자 64hex·숫자, status 비runtime 경로가 files에 없음. 각 오류 메시지 범주가 S 재사용 분기와 같다
   - `hashPath`: 파일 sha256, 없음 null, 디렉터리 null(가짜 fs)
   - 합성 저장소(실제 git, §12 예외): `tests/.tmp/synthetic-repos/<pid>/`에서 `git -C <dir> init -q`, `.gitignore`(`tests/fixtures/local.json`, `tests/.tmp/`), `tracked.txt`, `tests/specs/a.spec.js` 작성·커밋 후 `tracked.txt` 수정, ignore된 `tests/fixtures/local.json`과 runtime `tests/.tmp/x` 작성 → `takeCurrent(null, { root: <dir> })`의 `files`에 `.gitignore`, `tracked.txt`(수정 후 hash), `tests/specs/a.spec.js`, `tests/fixtures/local.json`이 각 파일 sha256으로 있고 `tests/.tmp/x`는 없다. 시작 files에만 있던 경로를 지우면 다시 hash되어 null. rename(`git mv`) 시 origPath 포함. 끝나면 디렉터리 삭제
   - parity(실제 저장소 읽기 전용, config `workers: 1`로 직렬): `python3 -I tests/scripts/start-snapshot.py parity-<pid>` 결과를 `loadStartSnapshot`으로 읽을 수 있고 `xy`·`files`가 같은 시점 `takeCurrent(null)`과 같다. 끝나면 삭제
   - 모든 함수가 입력을 바꾸지 않는다

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-state.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step1` (전체는 `workers: 1` 직렬, 마지막은 `reused`)
2. 범위 gate: `python3 -I - step1 'tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-state.spec.js' 'tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-state.spec.js' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
