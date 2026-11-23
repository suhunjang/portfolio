# Step 0 — tests-env-bootstrap

- 예상 시간: 18분
- 실행 횟수: 시작 status 저장 1회, snapshot 저장 1회, npm install 1회, scope-snapshot spec 2회, 전체 테스트 1회, snapshot 검사 1회
- 선행 step: 없음

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §3, §11.1~§11.4, §11.7
3. index.json을 확인한다. 이 step은 선행 step이 없다.
4. 다음을 확인한다: 루트 package.json 없음, `tests/` 없음
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - 하네스 전용: Git 상태를 바꾸는 명령(init, checkout, switch, add, commit, push, reset, stash, merge, rebase, tag 등), Harness 운영 명령(`harness --project-root . ...`)
   - 허용: 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log, `-w` 없는 hash-object)
   - 금지: main 직접 변경, merge, deploy
7. BASE = `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`
8. 공통 실행 계약: `tests/scripts/with-env.sh`를 만든 뒤 npm·node·playwright는 모두 이 래퍼를 거쳐 실행한다.

## tracked source 허용 파일 (exact)

- `tests/scripts/with-env.sh`
- `tests/scripts/scope-snapshot.mjs`
- `tests/package.json`
- `tests/package-lock.json`
- `tests/.gitignore`
- `tests/playwright.config.js`
- `tests/specs/scope-snapshot.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/node_modules/**`, `tests/.npm-cache/**`
- `tests/.tmp/**` (snapshot 파일 포함), `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖의 모든 파일

## 작업 (순서 고정)

1. 시작 status 저장 — 어떤 파일보다 먼저 실행한다.
   - `mkdir -p tests/.tmp && git status --porcelain=v1 -z --untracked-files=all > tests/.tmp/step0-status-before.z`
2. `with-env.sh`: §11.2 내용을 그대로 쓴다.
3. `scope-snapshot.mjs`: §11.7 계약(`STATUS_ARGS`, `parseStatusZ`, `takeSnapshot`, `diffSnapshots`, `classifyChanges`, CLI `--save`/`--check`)을 구현한다. git 실행 함수는 주입할 수 있게 하고 Git 읽기 명령만 쓴다.
4. snapshot 저장 — tests 밖 파일을 건드리기 전에 실행한다.
   - `sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --save tests/.tmp/step0-scope-before.json --status-raw tests/.tmp/step0-status-before.z`
5. `tests/.gitignore`: §11.1의 7줄을 쓰고 끝에 개행 1개를 둔다.
6. `tests/package.json`: `private`, `type: module`, devDependencies 2개, scripts `test`와 `browsers:install`
7. 설치: `sh tests/scripts/with-env.sh npm --prefix tests install`
8. `playwright.config.js`
   - testDir `./specs`, reporter list, retries 0, outputDir `./test-results`
   - webServer: `python3 -m http.server 4173 --bind 127.0.0.1`, cwd `..`, reuseExistingServer
   - baseURL `http://127.0.0.1:4173`
   - projects 6개. 각각 `colorScheme`과 `metadata.theme`을 지정한다.
     - mobile-dark/light: 375×812
     - tablet-dark/light: 768×1024
     - desktop-dark/light: 1280×800
9. `scope-snapshot.spec.js` (브라우저 page fixture를 쓰지 않는 node 전용 테스트, desktop-dark에서만 실행하고 나머지 project는 `test.skip`)
   - `parseStatusZ`
     - ` M CLAUDE.md`, `?? docs/a.md` → xy·path 정확
     - `R  new.md` + NUL + `old.md` → `origPath === 'old.md'`
     - 빈 입력 → `[]`, 잘린 레코드 → throw
   - `takeSnapshot` (가짜 git 주입): tests 밖 경로만 hash-object가 호출되고 tests 안 경로는 호출되지 않는다. 사라진 파일은 null
   - `diffSnapshots` + `classifyChanges` (allow = 이 step의 허용 파일 목록)
     - 기존 ` M CLAUDE.md`, 해시 동일 → 위반 0 (시작 전 Harness 변경 허용)
     - 기존 ` M CLAUDE.md`, 해시 변경 → `outside-tests:CLAUDE.md`
     - 새 `?? docs/x.md` → `outside-tests:docs/x.md`
     - 새 `?? .harness/runtime/a.json`, 기존 `phases/HOO-81-portfolio-redesign/step3.md` 해시 변경 → 위반 0 (런타임 면제)
     - 새 ` M .harness/policy.json`, 새 ` M .harness/harness.lock.json` → 각각 `outside-tests:`
     - 새 `?? tests/node_modules/x/index.js` → `runtime-visible:`
     - 새 `?? tests/specs/scope-snapshot.spec.js` → 위반 0, 새 `?? tests/specs/other.spec.js` → `unexpected-tests:`
     - before에만 있던 항목이 사라짐 → 위반 0
     - before ` M README.md` → after `MM README.md` → `outside-tests:README.md`
     - 새 `R  tests/x.js` + 원래 경로 `README.md` → `outside-tests:README.md`와 `unexpected-tests:tests/x.js`
     - 두 입력이 변경되지 않는다.
   - CLI subprocess: `--check`에 없는 before 파일 → exit 1, 깨진 JSON → exit 1

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/step0-scope-before.json --allow tests/scripts/with-env.sh,tests/scripts/scope-snapshot.mjs,tests/package.json,tests/package-lock.json,tests/.gitignore,tests/playwright.config.js,tests/specs/scope-snapshot.spec.js` → 모두 exit 0
- 마지막 명령은 시작 snapshot 이후 tests 밖 새 변경, tests 안 runtime 경로 노출, 허용 목록 밖 tests 파일이 있으면 exit 1이다.
