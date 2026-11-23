# Step 0 — tests-env-setup

- 예상 시간: 14분
- 실행 횟수: 설치 1회, 브라우저 설치 1회, 테스트 1회
- 선행 step: 없음

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §3, §11.1~§11.4
3. index.json을 확인한다. 이 step은 선행 step이 없다.
4. 다음을 확인한다: `THEME_KEY`, 루트 package.json 없음, `tests/` 없음
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - 하네스 전용: Git 상태를 바꾸는 명령(init, checkout, switch, add, commit, push, reset, stash, merge, rebase, tag 등), Harness 운영 명령(`harness --project-root . ...`)
   - 허용: 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)
   - 금지: main 직접 변경, merge, deploy
7. BASE = `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`
8. 공통 실행 계약: 이 step에서 `tests/scripts/with-env.sh`를 가장 먼저 만든다. 이후 npm·node·playwright는 모두 이 래퍼를 거쳐 실행한다.

## tracked source 허용 파일 (exact)

- `tests/scripts/with-env.sh`
- `tests/package.json`
- `tests/package-lock.json`
- `tests/.gitignore`
- `tests/playwright.config.js`
- `tests/helpers/theme.js`
- `tests/specs/smoke.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/node_modules/**`, `tests/.npm-cache/**`, `tests/.pw-browsers/**`
- `tests/.tmp/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖의 모든 파일

## 작업

1. `with-env.sh`: §11.2 내용을 그대로 쓴다.
2. `tests/.gitignore`: §11.1의 7줄을 쓰고 끝에 개행 1개를 둔다.
3. `tests/package.json`: `private`, `type: module`, devDependencies 2개, scripts `test`와 `browsers:install`
4. 설치
   - `sh tests/scripts/with-env.sh npm --prefix tests install`
   - `sh tests/scripts/with-env.sh npm --prefix tests run browsers:install`
5. `playwright.config.js`
   - testDir `./specs`, reporter list, retries 0, outputDir `./test-results`
   - webServer: `python3 -m http.server 4173 --bind 127.0.0.1`, cwd `..`, reuseExistingServer
   - baseURL `http://127.0.0.1:4173`
   - projects 6개. 각각 `colorScheme`과 `metadata.theme`을 지정한다.
     - mobile-dark/light: 375×812
     - tablet-dark/light: 768×1024
     - desktop-dark/light: 1280×800
6. `theme.js`
   - fixture는 `THEME_KEY`가 null일 때만 테마를 주입한다.
   - `collectConsoleErrors`를 §11.4 계약대로 구현한다.
7. `smoke.spec.js`
   - collect를 goto보다 먼저 호출한다.
   - heroName과 테마를 확인한다.
   - finish 결과의 두 배열이 빈 배열인지 확인한다.
   - 비동기 throw를 일으키면 pageErrors가 1건 잡히는지 확인한다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test`가 6개 project 모두에서 통과한다.
- `git status --porcelain --untracked-files=all`에 tests/ 밖 변경과 runtime 경로가 나타나지 않는다.
