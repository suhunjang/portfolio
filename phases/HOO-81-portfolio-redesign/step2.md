# Step 2 — scope-snapshot-parse (재검증)

- 목적: 경로 판정·status parser·token scanner·schemaVersion(순수)과 malformed status에 대한 S·C·JS 동일 거부. §8.6.
- 19분 / 선행 0~1 / 공통 §9 / gate CGATE
- 허용(exact): `tests/scripts/scope-snapshot.mjs`(step 2 API), `tests/specs/scope-snapshot-parse.spec.js`
- runtime: R0(`tests/.tmp/status-harness-<pid>/`)
- 추가 금지: step 1 함수·spec, 정규식 schemaVersion 탐색, step 2 함수 fs 접근, 설계·S·C 변경(고정 본문 원인이면 중단·보고)

## 작업
1. `SNAP 2` → AC → no-op / 계약 안에서 추가·수정.
2. spec(node, desktop-dark, 10초):
   - `isRepoRelative` true: `a`, `tests/specs/a.spec.js`, `.harness/policy.json`, `a..b/c`; false: 빈 문자열, `/abs`, `/`, `../outside.txt`, `a/../b`, `./a`, `a/./b`, `..`, `.`, `a//b`, `a/`, NUL, `null`, 숫자, 객체; S `rel_ok`와 일치.
   - `parseStatusZ`: ` M CLAUDE.md`·`?? docs/a.md`, rename origPath·`statusXyMap` 두 경로 `R `, 빈 입력 `[]`, 끝 NUL.
   - 동일성(S·C `parse_status` bytes 동일). 정상: 빈 bytes, ` M a.txt`+NUL, ` M a.txt`+NUL+`?? b.txt`+NUL, `R  new.txt`+NUL+`old.txt`+NUL. 형식 거부: `M`, `?? `, `MMxa.txt`, ` M a.txt`+NUL+NUL+` M b.txt`+NUL, NUL 두 개, `R  new.txt`, `R  new.txt`+NUL+NUL, `C  new.txt`+NUL, `?? `+0xFF, `R  new.txt`+NUL+0xFF. 경로 거부: ` M ../x`, `?? /abs/x`, ` M a//b`, ` M ./a`, `R  new.txt`+NUL+`../old.txt`.
   - 함수 수준: JS 접두어(`bad status record:`/`bad path:`)와 추출 `rel_ok`·`parse_status` exec 결과 범주 동일; Python 예외는 정확히 `ValueError`, `str(e)` 정확히 `bad status record`/`bad path`(0xFF 두 입력은 `bad status record`); 정상 xy 세 구현 동일.
   - 프로그램 수준(로컬 harness, cwd·toplevel `tests/.tmp/status-harness-<pid>/`, C용 키만 맞춘 parity-1): 모든 거부 입력에서 S·C `SystemExit` 정확히 `bad git status`, 다른 예외 없음, `ls-files` 0, S makedirs 0·snapshot 없음, C walk 0·after.z 없음; 정상은 `ls-files` 기록; 삭제.
   - `scanJsonTopLevel` 최상위 token만·문자열·중첩 무시·중복/이스케이프 key throw·`[1]` → `[]`; `isSchemaVersion1` 6사례; 입력 불변.

## AC
1. `T scope-snapshot-parse.spec.js scope-snapshot-paths.spec.js && FULL && SNAP 2`
2. `CGATE 2 tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-parse.spec.js`
