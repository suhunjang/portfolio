# Step 2 — scope-snapshot-parse (재검증)

- 목적: 경로 판정·status parser·token scanner·schemaVersion 판정(순수)과, 같은 malformed status 입력에 대해 S·C·JS가 같은 거부 판정·오류 형식을 내는지 확인한다. §11.6 재검증 모드.
- 예상 19분 / 선행 0~1 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.6, §11.7(경로 계약, status parser 계약, schema, `scanJsonTopLevel`, S·C의 `rel_ok`·`parse_status`, 블록 추출, exec harness, 비교 도구 step 2)
- tracked 허용(exact): `tests/scripts/scope-snapshot.mjs`(step 2 API), `tests/specs/scope-snapshot-parse.spec.js`
- runtime: R0(`tests/.tmp/status-harness-<pid>/`)
- 금지: §15.7, step 1 함수·spec 수정, 정규식 schemaVersion 탐색, step 2 함수의 파일 시스템 접근, S·C 본문 변경

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step2`
2. AC 실행 → 통과면 no-op. status parser 동일성 검증이 없거나 `parseStatusZ`가 계약과 다르면 허용 파일 안에서 추가·수정.
3. spec 계약(node 전용, desktop-dark, timeout 10초)
   - `isRepoRelative`: true 4종, false 15종(빈 문자열·절대·`..`·`.`·빈 구성요소·NUL·비문자열); S 블록 `rel_ok`와 결과 일치
   - `parseStatusZ` 기본 사례
   - 동일성: S·C `parse_status` 정의 bytes 동일; 입력 — 정상 4종(빈, ` M a.txt`+NUL, 두 레코드, rename), 형식 거부 9종(`M`, `?? `, `MMxa.txt`, 중간 빈 레코드, NUL 두 개, `R  new.txt`, `R  new.txt`+NUL+NUL, `C  new.txt`+NUL, `?? `+0xFF), 경로 거부 5종(` M ../x`, `?? /abs/x`, ` M a//b`, ` M ./a`, `R  new.txt`+NUL+`../old.txt`) → JS 범주와 S·C 추출 함수 `ValueError` 범주 일치, 다른 예외 없음; 정상은 세 구현 xy 동일; 프로그램 수준(로컬 exec harness, status bytes 지정, `tests/.tmp/status-harness-<pid>/`, C용 키만 맞춘 `parity-1` start) 거부 입력마다 S·C `SystemExit` 정확히 `bad git status`, `ls-files` 0, S `os.makedirs` 0, C `os.walk` 0·after.z 없음; 정상은 `ls-files` 기록; 디렉터리 삭제
   - `scanJsonTopLevel`·`isSchemaVersion1` 기존 사례, 입력 불변

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-parse.spec.js scope-snapshot-paths.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step2`
2. 범위 gate: `python3 -I - step2 'tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-parse.spec.js' '' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
