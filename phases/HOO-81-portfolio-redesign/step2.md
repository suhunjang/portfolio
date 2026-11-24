# Step 2 — scope-snapshot-parse (재검증)

- 목적: 저장소 상대 경로 판정, status parser, 최상위 JSON token scanner, schemaVersion 판정(순수)과, 같은 malformed status 입력에 대해 고정 S·고정 C·JS `parseStatusZ`가 같은 거부 판정·오류 형식을 내는지 확인한다. 설계 §11.6 재검증 모드.
- 예상 19분 / 선행 0~1 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.6, §11.7(저장소 상대 경로 계약, status parser 계약, schema, `scanJsonTopLevel`, S·C의 `rel_ok`·`parse_status`, 설계 블록 추출 규칙, S·C exec harness, 비교 도구 step 2)
- tracked 허용(exact): `tests/scripts/scope-snapshot.mjs`(step 2 API), `tests/specs/scope-snapshot-parse.spec.js`
- runtime: R0(`tests/.tmp/status-harness-<pid>/`)
- 금지: §15.7, step 1 함수 동작·step 1 spec 수정, 정규식으로 schemaVersion 찾기, step 2 함수의 파일 시스템 접근, S·C 본문 변경

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step2`
2. AC를 실행한다. 통과하면 no-op. 기존 commit에 아래 status parser 동일성 검증이 없거나 `parseStatusZ`가 계약과 다르면 허용 파일 안에서 추가·수정한다.
3. API 계약: `isRepoRelative`, `parseStatusZ`(설계 parser 계약, 엄격 UTF-8), `statusXyMap`, `scanJsonTopLevel`, `isSchemaVersion1(value, token)`.
4. spec 계약(node 전용, desktop-dark, timeout 10초)
   - `isRepoRelative`: true — `a`, `tests/specs/a.spec.js`, `.harness/policy.json`, `a..b/c`; false — 빈 문자열, `/abs`, `/`, `../outside.txt`, `a/../b`, `./a`, `a/./b`, `..`, `.`, `a//b`, `a/`, NUL 포함, `null`·숫자·객체; 같은 목록을 S 블록에서 추출한 `rel_ok`로 판정한 결과와 일치
   - `parseStatusZ` 기본 사례(정상·rename·빈 입력·끝 NUL·형식 throw·`bad path` throw)
   - status parser 동일성: S·C 블록의 `parse_status` 정의 bytes 동일; 입력 목록 — 정상: 빈 bytes, ` M a.txt`+NUL, ` M a.txt`+NUL+`?? b.txt`+NUL, `R  new.txt`+NUL+`old.txt`+NUL; 형식 거부: `M`, `?? `, `MMxa.txt`, ` M a.txt`+NUL+NUL+` M b.txt`+NUL, NUL 두 개, `R  new.txt`, `R  new.txt`+NUL+NUL, `C  new.txt`+NUL, `?? `+0xFF; 경로 거부: ` M ../x`, `?? /abs/x`, ` M a//b`, ` M ./a`, `R  new.txt`+NUL+`../old.txt` → JS 범주(`bad status record:`/`bad path:`)와 S·C 추출 함수의 `ValueError` 메시지 범주가 같고 다른 예외 유형 없음; 정상 입력은 세 구현 xy 동일; 프로그램 수준(spec 내부 로컬 exec harness, `status` bytes 지정, cwd·toplevel `tests/.tmp/status-harness-<pid>/`, C용 키만 맞춘 `parity-1` start) 거부 입력마다 S·C `SystemExit`이 정확히 `bad git status`, `ls-files` 호출 0, S `os.makedirs` 0·snapshot 없음, C `os.walk` 0·after.z 없음; 정상 입력은 `ls-files` 호출 기록; 끝나면 디렉터리 삭제
   - `scanJsonTopLevel`·`isSchemaVersion1` 기존 사례(최상위 token, 문자열·중첩 무시, 중복·이스케이프 key throw, `[1]` → `[]`)
   - 입력 불변

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-parse.spec.js scope-snapshot-paths.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step2` (마지막은 `reused`)
2. 범위 gate: `python3 -I - step2 'tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-parse.spec.js' '' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
- parse spec 단독 실행에 S·C `parse_status` 정의 동일, S·C·JS 동일 거부 범주, 정확한 `bad git status` 종료가 포함되어 통과한다.
