# Step 2 — scope-snapshot-state

- 목적: 경로 유형 검사를 포함한 현재 status+hash 상태 수집과 합성 저장소 helper를 만들고, 합성 저장소 수집·rename과 실제 저장소 Python S parity를 증명한다. 종료 검사는 S `reused` + inline C.
- 예상 19분 / 선행 0~1 / 공통 절차 설계 §15
- read-first: 설계 §11.1, §11.4(직렬화), §11.7(규칙, 경로 유형 계약, S, 비교 도구 step 2, 설계 블록 추출 규칙, 테스트 격리), §12(합성 저장소 예외)
- tracked 허용(exact): `tests/scripts/scope-snapshot.mjs`(추가만), `tests/helpers/synthetic-repo.js`(신규), `tests/specs/scope-snapshot-state.spec.js`(신규)
- runtime: R0(합성 저장소 `tests/.tmp/synthetic-repos/<pid>/`, `<pid>-outside/` 포함)
- 금지: §15.7, step 1 함수 동작, identity·판정·CLI(step 5), 실제 저장소의 비runtime 경로에 symlink·FIFO 생성, 합성 저장소에서 init/add/commit 외 Git 변경(`git mv` 포함), 권한 변경

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step2`
2. `scope-snapshot.mjs`에 step 2 API(`scanProject`, `hashPath`, `takeCurrent` with `root`) 추가. git·fs 주입 가능, Git 읽기만, 링크를 따라가거나 읽지 않음, 기록 대상마다 `checkPath` 후에만 `readRegular`.
3. `synthetic-repo.js`: `makeSyntheticRepo()` → `{ dir, outside, git(args), cleanup() }`. `git`은 `init -q`, `add -A`/정확한 경로 add, `-c user.name=t -c user.email=t@example.invalid commit -q -m <msg>`만 허용하고 그 밖 인자는 throw. `designBlock(marker)`: 설계 블록 추출 규칙으로 S·C 본문 반환(문서 읽기만). `runPython(args, { cwd, input })`·`runNode(args, { cwd })`: timeout 10초 subprocess.
4. `scope-snapshot-state.spec.js` (node 전용, desktop-dark만)
   - `hashPath`(가짜 fs): 일반 파일 sha256, missing null, 디렉터리 → `non-regular:`, symlink → `symlink:` throw. 가짜 fs 기록에 symlink 경로의 `readFileSync`·`statSync`·`readlinkSync`·`realpathSync`·open 없음
   - `scanProject`(가짜 fs): SKIP 디렉터리 미진입, SKIP 디렉터리 엔트리 자체 symlink는 보고, 결과 정렬
   - 합성 저장소(실제 git): `.gitignore`(`tests/fixtures/local.json`, `tests/.tmp/`), `tracked.txt`, `tests/specs/a.spec.js`를 Node `fs`로 작성 → `add -A` → commit. `tracked.txt` 수정, ignore된 `tests/fixtures/local.json`과 runtime `tests/.tmp/x` 작성 → `takeCurrent(null, { root: dir })`의 `unsafe` `[]`, `files`에 `.gitignore`, `tracked.txt`(수정 후 hash), `tests/specs/a.spec.js`, `tests/fixtures/local.json`이 각 sha256으로 있고 `tests/.tmp/x`는 없음
   - 합성 rename(`git mv` 금지): `fs.renameSync(a.spec.js → b.spec.js)` 후 `add -A` → status에 `R ` + `tests/specs/b.spec.js` + origPath `tests/specs/a.spec.js`. 앞 상태를 start로 넘긴 `takeCurrent(start, { root })`의 `xy`에 두 경로 `R `, `files`에 b는 sha256, a는 null(실제로 없음)
   - 합성 runtime 내부 링크: `tests/node_modules/.bin/x` symlink는 `unsafe`에 없음
   - parity(실제 저장소 읽기 전용): `python3 -I tests/scripts/start-snapshot.py parity-<pid>` 결과를 `loadStartSnapshot`으로 읽을 수 있고 `xy`·`files`가 같은 시점 `takeCurrent(null)`과 같고 `unsafe` `[]`. 끝나면 삭제
   - 모든 테스트 finally에서 `cleanup()`, 함수는 입력을 바꾸지 않는다

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-state.spec.js scope-snapshot-schema.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step2` (마지막은 `reused`)
2. 범위 gate: `python3 -I - step2 'tests/scripts/scope-snapshot.mjs,tests/helpers/synthetic-repo.js,tests/specs/scope-snapshot-state.spec.js' 'tests/helpers/synthetic-repo.js,tests/specs/scope-snapshot-state.spec.js' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
