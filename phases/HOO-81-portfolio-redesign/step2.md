# Step 2 — scope-snapshot-parse (재검증)

- 목적: 경로 판정·status parser·token scanner·schemaVersion 판정(순수)과, 같은 malformed status 입력에 대해 S·C·JS가 같은 거부 판정·오류 형식을 내는지 확인한다. §11.6 재검증 모드.
- 예상 19분 / 선행 0~1 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.6, §11.7(경로 계약, status parser 계약, schema, `scanJsonTopLevel`, S·C의 `rel_ok`·`parse_status`(decode 실패 변환 포함), 블록 추출, exec harness, 비교 도구 step 2)
- tracked 허용(exact): `tests/scripts/scope-snapshot.mjs`(step 2 API), `tests/specs/scope-snapshot-parse.spec.js`
- runtime: R0(`tests/.tmp/status-harness-<pid>/`)
- 금지: §15.7, step 1 함수·spec 수정, 정규식 schemaVersion 탐색, step 2 함수의 파일 시스템 접근, 설계 문서·S·C 본문 변경(불일치가 고정 본문 때문이면 중단·보고)

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step2`
2. AC 실행 → 통과면 no-op. status parser 동일성 검증이 없거나 `parseStatusZ`가 계약과 다르면 허용 파일 안에서 추가·수정.
3. spec 계약(node 전용, desktop-dark, timeout 10초)
   - `isRepoRelative`: true — `a`, `tests/specs/a.spec.js`, `.harness/policy.json`, `a..b/c`; false — 빈 문자열, `/abs`, `/`, `../outside.txt`, `a/../b`, `./a`, `a/./b`, `..`, `.`, `a//b`, `a/`, NUL 포함, `null`, 숫자, 객체; S 블록 `rel_ok`와 결과 일치
   - `parseStatusZ` 기본: ` M CLAUDE.md`·`?? docs/a.md`, rename origPath·`statusXyMap` 두 경로 `R `, 빈 입력 `[]`, 끝 NUL 허용
   - 동일성: S·C `parse_status` 정의 bytes 동일. 입력 — 정상: 빈 bytes, ` M a.txt`+NUL, ` M a.txt`+NUL+`?? b.txt`+NUL, `R  new.txt`+NUL+`old.txt`+NUL; 형식 거부: `M`, `?? `, `MMxa.txt`, ` M a.txt`+NUL+NUL+` M b.txt`+NUL, NUL 두 개, `R  new.txt`, `R  new.txt`+NUL+NUL, `C  new.txt`+NUL, `?? `+0xFF, `R  new.txt`+NUL+0xFF; 경로 거부: ` M ../x`, `?? /abs/x`, ` M a//b`, ` M ./a`, `R  new.txt`+NUL+`../old.txt`
   - 함수 수준: JS throw 접두어(`bad status record:`/`bad path:`)와 S·C 블록에서 추출한 `rel_ok`·`parse_status`를 exec한 결과가 같은 범주; Python 쪽은 예외 유형이 정확히 `ValueError`이고 `str(e)`가 정확히 `bad status record` 또는 `bad path`(0xFF 두 입력은 `bad status record`, `UnicodeDecodeError`가 아님); 정상은 세 구현 xy 동일
   - 프로그램 수준(spec 내부 로컬 exec harness, status bytes 지정, cwd·toplevel `tests/.tmp/status-harness-<pid>/`, C용 키 집합만 맞춘 `tests/.tmp/start-snapshot-parity-1.json`): 거부 입력 전부(0xFF 포함)에서 S·C `SystemExit` 정확히 `bad git status`, 그 밖 예외 없음, `ls-files` 호출 0, S `os.makedirs` 0·snapshot 없음, C `os.walk` 0·after.z 없음; 정상은 `ls-files` 호출 기록; 디렉터리 삭제
   - `scanJsonTopLevel`: 최상위 token만, 문자열·중첩 무시, 중복·이스케이프 key throw, `[1]` → `[]`; `isSchemaVersion1` 6사례; 입력 불변

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-parse.spec.js scope-snapshot-paths.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step2`
2. 범위 gate: `python3 -I - step2 'tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-parse.spec.js' '' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
