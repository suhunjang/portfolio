# Step 1 — scope-snapshot-tool

- 예상 시간: 19분
- 실행 횟수: 시작 snapshot 1회, scope-snapshot spec 2회, 전체 테스트 1회, 범위 gate 1회
- 선행 step: 0 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §11.1, §11.5(하네스 런타임 면제), §11.7 전체 (S, C, 비교 도구 계약)
3. index.json에서 step 0이 completed인지 확인한다. 아니면 중단한다.
4. `tests/scripts/start-snapshot.py`, `with-env.sh`, `playwright.config.js`를 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령(init 포함)과 Harness 운영 명령은 하네스만 실행한다. 합성 테스트는 가짜 git·fs 주입으로만 한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log, `-w` 없는 hash-object)과 §11.7 시작 snapshot 명령은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.
8. 범위 gate(§11.7): 이 step의 첫 동작은 `python3 -I tests/scripts/start-snapshot.py tests/.tmp/start-snapshot-step1.json`이다. 어떤 파일도 쓰기 전에 실행한다.

## tracked source 허용 파일 (exact)

- `tests/scripts/scope-snapshot.mjs` (신규)
- `tests/specs/scope-snapshot.spec.js` (신규)

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**` (시작 snapshot 포함), `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖의 모든 파일
- step 0에서 만든 tests 파일 (`start-snapshot.py` 포함)
- `tests/.tmp/start-snapshot-step1.json` (생성 후 다시 쓰지 않는다)

## 작업 (순서 고정)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py tests/.tmp/start-snapshot-step1.json`
2. `scope-snapshot.mjs`: §11.7 비교 도구 계약(`RUNTIME_PREFIXES`, `EXEMPT_PREFIXES`, `GUARDED_PATHS`, `STATUS_ARGS`, `LS_FILES_ARGS`, `parseStatusZ`, `statusXyMap`, `loadStartSnapshot`, `hashPath`, `walkTests`, `takeCurrent`, `diffAgainstStart`, `classifyChanges`, `checkRuntimeVisible`, `checkSnapshotFirst`, `evaluateGate`, CLI `--check`)을 구현한다. git 실행 함수와 fs는 주입할 수 있게 하고 Git 읽기 명령만 쓴다. 시작 snapshot 파일을 만들거나 고치는 기능은 두지 않는다. 판정 규칙·위반 문자열·순서는 §11.7 C와 같다.
3. `scope-snapshot.spec.js` (node 전용, desktop-dark에서만 실행하고 나머지 project는 `test.skip`, git·fs는 가짜 주입. 아래에서 h0·h1·h2는 서로 다른 hash)
   - `parseStatusZ`
     - ` M CLAUDE.md`, `?? docs/a.md` → xy·path 정확
     - `R  new.md` + NUL + `old.md` → `origPath === 'old.md'`, `statusXyMap`에 두 경로 모두 `R `
     - 빈 입력 → `[]`, 잘린 레코드 → throw
   - `loadStartSnapshot`: 파일 없음, 깨진 JSON, `files` 누락, `xy`와 `statusZHex` 불일치 → throw
   - tests 밖: 시작 당시 수정돼 있던 `CLAUDE.md` (시작 ` M`, h1)
     - 현재 ` M`, h1 → 위반 0
     - 원복: 현재 status에 없음, h0 → Change `{ kind: 'content-changed', xyBefore: ' M', xyAfter: null }`, `outside-tests:CLAUDE.md`
     - 삭제: 현재 ` D`, null → `{ kind: 'deleted' }`, `outside-tests:CLAUDE.md`
     - 같은 ` M`에서 h2 → `{ kind: 'content-changed', xyBefore: ' M', xyAfter: ' M' }`, `outside-tests:CLAUDE.md`
   - tests 안: 시작 당시 수정돼 있던 기존 `tests/playwright.config.js` (시작 ` M`, h1, allow에 없음)
     - 현재 ` M`, h1 → 위반 0
     - 시작·종료 모두 ` M`이고 내용만 h2 → `{ kind: 'content-changed', xyBefore: ' M', xyAfter: ' M' }`, `tests-changed:tests/playwright.config.js`
     - 삭제: 현재 ` D`, null → `{ kind: 'deleted' }`, `tests-changed:tests/playwright.config.js`
     - 원복: 현재 status에 없음, h0 → `{ kind: 'content-changed', xyAfter: null }`, `tests-changed:tests/playwright.config.js`
     - 같은 변경이라도 `allow`에 `tests/playwright.config.js`가 있으면 → 위반 0
   - tests 안: 시작 때 깨끗했던 추적 파일 `tests/helpers/theme.js`(status 없음, h) → 현재 ` M`, h' → `tests-changed:tests/helpers/theme.js`
   - tests 안: 시작 때 미추적이던 `?? tests/specs/wip.spec.js`(h1) → 현재 없음 → `tests-changed:tests/specs/wip.spec.js`
   - tests 안: git이 ignore해 status에 나오지 않는 비runtime 파일 `tests/fixtures/local.json`(walk로만 발견, h1) → h2 → `tests-changed:tests/fixtures/local.json`
   - status만 변경: `README.md` hash 같고 xy가 없음 → `M ` → `status-changed:README.md`
   - 시작 때 깨끗한 `README.md` → ` M`, h' → `outside-tests:README.md`
   - 새 `?? docs/x.md` → `outside-tests:docs/x.md`
   - 새 `?? .harness/runtime/a.json`, `phases/HOO-81-portfolio-redesign/step3.md` hash 변경 → 위반 0 (런타임 면제)
   - `.harness/policy.json`, `.harness/harness.lock.json` hash 변경 → 각각 `outside-tests:`
   - 새 `?? tests/node_modules/x/index.js` → `runtime-visible:tests/node_modules/x/index.js`, RUNTIME 경로는 `files`에 들어가지 않는다.
   - 새 `?? tests/specs/scope-snapshot.spec.js`(allow) → 위반 0, 새 `?? tests/specs/other.spec.js` → `tests-changed:tests/specs/other.spec.js`
   - 새 `R  tests/x.js` + 원래 경로 `README.md`, README null → `outside-tests:README.md`와 `tests-changed:tests/x.js`
   - `checkSnapshotFirst`: 시작 기록에 `tests/scripts/scope-snapshot.mjs`가 있으면 `snapshot-not-first:tests/scripts/scope-snapshot.mjs`, 없으면 `[]`
   - `takeCurrent`: 시작 `files`의 경로는 현재 status·ls-files·walk에 없어도 모두 다시 hash된다(결과 null).
   - `evaluateGate` 순서: snapshot-not-first → 경로 오름차순 변경 위반 → runtime-visible
   - 모든 함수가 입력을 변경하지 않는다.
   - parity (실제 저장소, 읽기 전용): `python3 -I tests/scripts/start-snapshot.py tests/.tmp/start-snapshot-parity-<pid>.json` 결과의 `xy`·`files`가 같은 시점의 `takeCurrent({ xy: {}, files: {}, entries: [] })` 결과와 같다. 끝나면 파일을 지운다.
   - CLI subprocess: 없는 start 파일 → exit 1, 깨진 JSON → exit 1, 방금 만든 parity snapshot + `--allow ''` → exit 0

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step1.json --allow tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot.spec.js --require-absent tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot.spec.js` → 모두 exit 0
- 마지막 명령은 시작 snapshot이 도구보다 늦게 만들어졌거나, 허용 파일 밖의 tests 안팎 경로가 변경·삭제·원복·status 변경되었거나, runtime 경로가 노출되면 exit 1이다.
