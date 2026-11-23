# Step 1 — scope-snapshot-state

- 목적: 비교 도구의 schema/parsing과 현재 status+hash 상태 수집을 만들고 Python S와 parity를 증명한다. 종료 검사는 inline C.
- 예상 18분 / 선행 0 / 공통 절차 설계 §15
- read-first: 설계 §11.1, §11.7(규칙, schema, 재시도, S, C, 비교 도구 step 1)
- tracked 허용(exact): `tests/scripts/scope-snapshot.mjs`(신규, step 1 API만), `tests/specs/scope-snapshot-state.spec.js`(신규)
- runtime: R0
- 금지: §15.7, 변경 판정·정책 분류·CLI(step 2)

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step1`
2. `scope-snapshot.mjs`: 설계 §11.7 비교 도구 step 1 API(상수, `parseStatusZ`, `statusXyMap`, `loadStartSnapshot` strict schema, `hashPath`, `walkTests`, `takeCurrent`). git·fs 주입 가능, Git 읽기만, snapshot 생성·수정 기능 없음, CLI 없음.
3. `scope-snapshot-state.spec.js` (node 전용, desktop-dark만)
   - `parseStatusZ`: ` M CLAUDE.md`, `?? docs/a.md` 정확; `R  new.md`+NUL+`old.md` → origPath, `statusXyMap`에 두 경로 `R `; 빈 입력 `[]`; 잘린 레코드 throw
   - `loadStartSnapshot`(독립 `parity-{숫자}` 파일): 정상 반환; throw — 파일 없음, 깨진 JSON, 키 누락, 여분 키, schemaVersion 2, stepId≠파일명, stepId 형식 오류, xy≠statusZHex, files 값이 숫자
   - `hashPath`: 파일 sha256, 없음 null, 디렉터리 null(가짜 fs)
   - `walkTests`: RUNTIME 디렉터리 미진입, `tests/.gitignore`와 ignore된 `tests/fixtures/local.json` 포함(가짜 fs)
   - `takeCurrent`(가짜 git·fs): 시작 `files`의 `CLAUDE.md`가 status에서 사라져도 재hash(변경 시 다른 hash, 삭제 시 null), rename origPath 포함, RUNTIME은 files에 없고 xy에는 남음
   - parity(실제 저장소 읽기 전용): `python3 -I tests/scripts/start-snapshot.py parity-<pid>` 결과를 `loadStartSnapshot`으로 읽을 수 있고 `xy`·`files`가 같은 시점 `takeCurrent(null)`과 같다. 끝나면 삭제
   - 모든 함수가 입력을 바꾸지 않는다

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-state.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step1`
2. 범위 gate: `python3 -I - step1 'tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-state.spec.js' 'tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-state.spec.js' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
