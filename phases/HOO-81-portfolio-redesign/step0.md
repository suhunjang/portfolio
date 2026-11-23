# Step 0 — tests-env-setup

- 예상 시간: 14분
- 실행 횟수: 의존성 설치 1회, 브라우저 설치 1회, 테스트 1회(웹서버 1회)
- 선행 step: 없음

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다.
   - `CLAUDE.md` (하네스 계약 블록 포함)
   - `README.md`
   - 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md`의 §3, §11.1~§11.4
3. `phases/HOO-81-portfolio-redesign/index.json`을 확인한다. 이 step은 선행 step이 없다.
4. 현재 코드를 확인한다.
   - `js/main.js` 상단의 `THEME_KEY`
   - 루트에 package.json이 없는지
   - `tests/`가 아직 없는지
5. 다음은 빌더 read-only다. 문서·계획 변경은 하네스만 한다.
   - `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`
   - 하네스 managed 파일: `scripts/**`, `.claude/**`, `.codex/**`, `templates/**`, `harness-manifest.json`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. git checkout·add·commit·push는 하네스만 한다. 빌더는 working tree만 수정한다. main 직접 변경, merge, deploy는 금지다.
7. BASE = `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`
8. 공통 실행 계약(설계 §11.2): 이 step에서 `tests/scripts/with-env.sh`를 가장 먼저 만든다. 이후 npm·node·playwright 명령은 모두 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/scripts/with-env.sh`
- `tests/package.json`
- `tests/package-lock.json`
- `tests/.gitignore`
- `tests/playwright.config.js`
- `tests/helpers/theme.js`
- `tests/specs/smoke.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- 설치: `tests/node_modules/**`, `tests/.npm-cache/**`(npm 로그 포함), `tests/.pw-browsers/**`
- 실행: `tests/.tmp/**`, `tests/test-results/**`, `tests/playwright-report/**`
- 그 밖의 경로에는 쓰지 않는다. 홈의 `~/.npm`, `~/Library/Caches`, 시스템 tmp도 포함된다.

## 수정 금지

- `tests/` 밖의 모든 파일

## 작업

### 1. `tests/scripts/with-env.sh`

설계 §11.2 내용을 그대로 옮긴다.
- `set -eu`
- 스크립트 위치에서 `REPO_ROOT` 절대경로를 구한다.
- `mkdir -p`로 `$REPO_ROOT/tests/.tmp`와 `$REPO_ROOT/tests/.npm-cache`를 만든다.
- 다음을 export한다.
  - `TMPDIR=$REPO_ROOT/tests/.tmp`
  - `npm_config_cache=$REPO_ROOT/tests/.npm-cache`
  - `PLAYWRIGHT_BROWSERS_PATH=$REPO_ROOT/tests/.pw-browsers`
- `cd $REPO_ROOT` 후 `exec "$@"`

### 2. `tests/.gitignore`

정확히 다음 7줄만 넣는다.
- `node_modules/`
- `.npm-cache/`
- `.pw-browsers/`
- `.tmp/`
- `test-results/`
- `playwright-report/`
- `screenshots/`

### 3. `tests/package.json`

- `private: true`, `type: module`
- devDependencies: `@playwright/test`, `@axe-core/playwright`
- scripts
  - `test`: `playwright test`
  - `browsers:install`: `playwright install chromium`
- 환경 변수는 package.json에 넣지 않는다. 래퍼가 제공한다.

### 4. 설치

- `sh tests/scripts/with-env.sh npm --prefix tests install`로 lockfile을 만든다.
- `sh tests/scripts/with-env.sh npm --prefix tests run browsers:install`

### 5. `tests/playwright.config.js`

- testDir `./specs`, reporter list, retries 0, outputDir `./test-results`
- webServer
  - command: `python3 -m http.server 4173 --bind 127.0.0.1`
  - cwd: `..`
  - url: `http://127.0.0.1:4173/index.html`
  - reuseExistingServer: true
- baseURL: `http://127.0.0.1:4173`
- projects 6개 (각각 `colorScheme`과 `metadata.theme` 지정)
  - `mobile-dark`, `mobile-light`: 375×812
  - `tablet-dark`, `tablet-light`: 768×1024
  - `desktop-dark`, `desktop-light`: 1280×800

### 6. `tests/helpers/theme.js`

- `test.extend`로 page fixture를 확장한다.
  - `addInitScript`에서 `localStorage.getItem(THEME_KEY) === null`일 때만 project 테마를 저장한다.
  - 이미 저장된 값은 덮어쓰지 않는다.
- `test`, `expect`, `collectConsoleErrors(page)`를 export한다. `collectConsoleErrors`는 Google Fonts 관련 에러를 제외한다.
- 최초 방문 검사(step 3)에서는 이 fixture를 쓰지 않는다.

### 7. `tests/specs/smoke.spec.js`

- `#heroName`이 장수훈이다.
- `data-theme`이 project 테마와 같다.
- 콘솔 에러가 0건이다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test`가 6개 project 모두에서 통과한다.
- `git status --porcelain --untracked-files=all` 출력에 `tests/` 밖 변경이 없고, runtime 경로도 나오지 않는다.
