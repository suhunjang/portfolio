# Step 0 — tests-env-setup

- 예상 시간: 12분
- 실행 횟수: 의존성 설치 1회, 브라우저 설치 1회, 테스트 1회(웹서버 1회)
- 선행 step: 없음

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다.
   - `CLAUDE.md` (하네스 계약 블록 포함)
   - `README.md`
   - 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` (§3, §11.1~§11.3)
3. `phases/HOO-81-portfolio-redesign/index.json`을 확인한다. 이 step은 선행 step이 없다.
4. 현재 코드에서 다음을 확인한다.
   - `js/main.js` 상단의 `THEME_KEY`
   - 루트에 package.json이 없음
   - `tests/`가 아직 없음
5. 빌더 read-only 경로 (문서와 계획 변경은 하네스만 한다)
   - `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`
   - 하네스 managed 파일: `scripts/**`, `.claude/**`, `.codex/**`, `templates/**`, `harness-manifest.json`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. git checkout·add·commit·push는 하네스만 한다. 빌더는 working tree만 수정한다. main 직접 변경, merge, deploy는 금지다.
7. BASE = `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`

## tracked source 허용 파일 (exact)

- `tests/package.json`
- `tests/package-lock.json`
- `tests/.gitignore`
- `tests/playwright.config.js`
- `tests/helpers/theme.js`
- `tests/specs/smoke.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- 설치: `tests/node_modules/**`, `tests/.npm-cache/**`, `tests/.pw-browsers/**`
- 실행: `tests/.tmp/**`, `tests/test-results/**`, `tests/playwright-report/**`
- 이 밖의 경로(홈 디렉터리 캐시, 시스템 tmp 포함)에는 쓰지 않는다.

## 수정 금지

- `tests/` 밖의 모든 파일

## 작업

1. `tests/.gitignore`를 만든다. 정확히 아래 7줄만 넣고 다른 줄은 넣지 않는다.
   - `node_modules/`
   - `.npm-cache/`
   - `.pw-browsers/`
   - `.tmp/`
   - `test-results/`
   - `playwright-report/`
   - `screenshots/`
2. `tests/package.json`을 만든다.
   - `private: true`, `type: module`
   - devDependencies: `@playwright/test`, `@axe-core/playwright`
   - scripts
     - `test`: `mkdir -p .tmp && TMPDIR=$PWD/.tmp PLAYWRIGHT_BROWSERS_PATH=./.pw-browsers playwright test`
     - `browsers:install`: `mkdir -p .tmp && TMPDIR=$PWD/.tmp PLAYWRIGHT_BROWSERS_PATH=./.pw-browsers playwright install chromium`
   - `npm --prefix tests install --cache tests/.npm-cache`로 lockfile을 만든다.
3. `npm --prefix tests run browsers:install`을 실행한다. 브라우저는 `tests/.pw-browsers`에 설치된다.
4. `tests/playwright.config.js`를 만든다.
   - testDir `./specs`, reporter list, retries 0, outputDir `./test-results`
   - webServer
     - command: `python3 -m http.server 4173 --bind 127.0.0.1`
     - cwd: 설정 파일 기준 `..`
     - url: `http://127.0.0.1:4173/index.html`
     - reuseExistingServer: true
   - use.baseURL: `http://127.0.0.1:4173`
   - projects (각각 `colorScheme`과 `metadata.theme` 지정)
     - `mobile-dark`, `mobile-light`: 375×812
     - `tablet-dark`, `tablet-light`: 768×1024
     - `desktop-dark`, `desktop-light`: 1280×800
5. `tests/helpers/theme.js`를 만든다.
   - `test.extend`로 page fixture를 만든다.
     - `addInitScript` 안에서 `localStorage.getItem(THEME_KEY) === null`일 때만 `localStorage.setItem(THEME_KEY, project 테마)`를 실행한다.
     - 이미 저장된 값은 덮어쓰지 않으므로, 테마 변경 후 reload해도 값이 유지된다.
   - THEME_KEY는 main.js의 실제 문자열을 쓴다.
   - `test`, `expect`를 export한다.
   - `collectConsoleErrors(page)`를 export한다.
     - pageerror와 console.error를 모은다.
     - fonts.googleapis.com, fonts.gstatic.com에서 온 것은 제외한다.
   - 이 fixture는 최초 방문 검사(step 3의 `first-visit.spec.js`)에서는 쓰지 않는다.
6. `tests/specs/smoke.spec.js`를 만든다.
   - `#heroName`이 장수훈이다.
   - `html[data-theme]`가 project 테마와 같다.
   - 콘솔 에러가 0건이다.

## 완료 기준 (AC)

- `npm --prefix tests test`가 6개 project 모두에서 통과한다.
- `git status --porcelain --untracked-files=all`에 `tests/` 밖 변경이 없다.
- 같은 출력에 runtime 경로가 나오지 않는다(gitignore 적용).
