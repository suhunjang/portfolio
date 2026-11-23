# Step 1 — tests-browser-smoke

- 예상 시간: 14분
- 실행 횟수: 시작 status 저장 1회, snapshot 저장 1회, 브라우저 설치 1회, smoke spec 2회, 전체 테스트 1회, snapshot 검사 1회
- 선행 step: 0 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §3(테마), §11.4, §11.7
3. index.json에서 step 0이 completed인지 확인한다. 아니면 중단한다.
4. `THEME_KEY`, `playwright.config.js`, `scope-snapshot.mjs`를 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log, `-w` 없는 hash-object)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/helpers/theme.js`
- `tests/specs/smoke.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.pw-browsers/**`, `tests/.npm-cache/**`
- `tests/.tmp/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖의 모든 파일
- step 0에서 만든 tests 파일

## 작업 (순서 고정)

1. 시작 status 저장: `mkdir -p tests/.tmp && git status --porcelain=v1 -z --untracked-files=all > tests/.tmp/step1-status-before.z`
2. snapshot 저장: `sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --save tests/.tmp/step1-scope-before.json --status-raw tests/.tmp/step1-status-before.z`
3. 브라우저 설치: `sh tests/scripts/with-env.sh npm --prefix tests run browsers:install`
4. `theme.js`
   - fixture는 `THEME_KEY`가 null일 때만 테마를 주입한다.
   - `collectConsoleErrors`를 §11.4 계약대로 구현한다.
5. `smoke.spec.js` (6개 project)
   - collect를 goto보다 먼저 호출한다.
   - heroName과 테마를 확인한다.
   - finish 결과의 두 배열이 빈 배열인지 확인한다.
   - 비동기 throw를 일으키면 pageErrors가 1건 잡히는지 확인한다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- smoke.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/step1-scope-before.json --allow tests/helpers/theme.js,tests/specs/smoke.spec.js` → 모두 exit 0 (smoke는 6개 project 모두 통과)
