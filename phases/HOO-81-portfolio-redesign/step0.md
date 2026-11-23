# Step 0 — tests-env-setup

- 예상 시간: 14분
- 실행 횟수: 의존성 설치 1회, 브라우저 설치 1회, 테스트 1회(웹서버 1회)
- 선행 step: 없음

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다.
   - `CLAUDE.md` (중앙 Harness 계약 블록)
   - `README.md`
   - 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 그것도 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md`의 §3, §11.1~§11.4
3. `phases/HOO-81-portfolio-redesign/index.json`을 확인한다. 이 step은 선행 step이 없다.
4. 현재 코드를 확인한다.
   - `js/main.js`의 `THEME_KEY`
   - 루트에 package.json이 없는지
   - `tests/`가 아직 없는지
5. 빌더는 다음 경로를 읽기만 한다. 수정은 하네스만 한다.
   - `CLAUDE.md`, `docs/**`, `phases/**`
   - `.harness/**`(lock·policy·state)
   - `.claude/**`, `.codex/**`
   - `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. git checkout·add·commit·push와 Harness 운영 명령(`harness --project-root . ...`)은 하네스만 실행한다. 빌더는 working tree만 수정한다. main 직접 변경, merge, deploy는 금지다.
7. BASE = `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`
8. 공통 실행 계약(§11.2): 이 step에서 `tests/scripts/with-env.sh`를 가장 먼저 만든다. 이후 npm·node·playwright 명령은 모두 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/scripts/with-env.sh`
- `tests/package.json`
- `tests/package-lock.json`
- `tests/.gitignore`
- `tests/playwright.config.js`
- `tests/helpers/theme.js`
- `tests/specs/smoke.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- 설치: `tests/node_modules/**`, `tests/.npm-cache/**`, `tests/.pw-browsers/**`
- 실행: `tests/.tmp/**`, `tests/test-results/**`, `tests/playwright-report/**`
- 그 밖의 경로에는 쓰지 않는다. 홈 디렉터리 캐시와 시스템 tmp도 포함된다.

## 수정 금지

- `tests/` 밖의 모든 파일

## 작업

1. `tests/scripts/with-env.sh`: §11.2 내용을 그대로 옮긴다.
2. `tests/.gitignore`: 아래 7줄을 이 순서로 쓰고 파일 끝에 개행 1개를 둔다. 빈 줄, 주석, 중복 줄은 넣지 않는다.
   - `node_modules/`
   - `.npm-cache/`
   - `.pw-browsers/`
   - `.tmp/`
   - `test-results/`
   - `playwright-report/`
   - `screenshots/`
3. `tests/package.json`
   - `private: true`, `type: module`
   - devDependencies: `@playwright/test`, `@axe-core/playwright`
   - scripts: `test`는 `playwright test`, `browsers:install`은 `playwright install chromium`
4. 의존성과 브라우저를 설치한다.
   - `sh tests/scripts/with-env.sh npm --prefix tests install`
   - `sh tests/scripts/with-env.sh npm --prefix tests run browsers:install`
5. `tests/playwright.config.js`
   - testDir `./specs`, reporter list, retries 0, outputDir `./test-results`
   - webServer: `python3 -m http.server 4173 --bind 127.0.0.1`, cwd `..`, url `http://127.0.0.1:4173/index.html`, reuseExistingServer true
   - baseURL `http://127.0.0.1:4173`
   - projects 6개(각각 `colorScheme`, `metadata.theme` 지정)
     - `mobile-dark`, `mobile-light`: 375×812
     - `tablet-dark`, `tablet-light`: 768×1024
     - `desktop-dark`, `desktop-light`: 1280×800
6. `tests/helpers/theme.js`
   - `test.extend`로 fixture를 만든다. `addInitScript`는 `localStorage.getItem(THEME_KEY) === null`일 때만 project 테마를 저장한다.
   - `test`, `expect`, `collectConsoleErrors(page)`를 export한다. `collectConsoleErrors`는 Google Fonts 관련 에러를 제외한다.
   - 최초 방문 검사에서는 이 fixture를 쓰지 않는다.
7. `tests/specs/smoke.spec.js`
   - `#heroName`이 장수훈이다.
   - `data-theme`이 project 테마와 같다.
   - 콘솔 에러가 0건이다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test`가 6개 project 모두 통과한다.
- `git status --porcelain --untracked-files=all` 결과에 `tests/` 밖 변경이 없고, runtime 경로도 나타나지 않는다.
