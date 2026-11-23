# Step 0 — tests-env-setup

- 예상 시간: 12분
- 실행 횟수: 설치 1회, 브라우저 설치 1회, 테스트 1회(웹서버 기동 포함)
- 선행 step: 없음

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침 `README.md`를 읽는다. 루트나 하위 폴더에 `CLAUDE.md` 또는 `AGENTS.md`가 있으면 함께 읽는다. BASE에는 없다.
2. 설계 문서 두 개를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`: 시각 톤, 토큰, Space Grotesk 제약
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md`: 이번 설계. 특히 §3, §11
3. `phases/HOO-81-portfolio-redesign/index.json`에서 선행 step 상태를 확인한다. 이 step은 선행 step이 없다.
4. 현재 코드에서 다음을 확인한다.
   - 빌드 도구가 없다.
   - `js/main.js` 상단의 `THEME_KEY` 값
   - 루트에 `package.json`이 없다.
5. `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`는 읽기 전용이다. 문서 변경은 하네스만 한다.
6. 기준 commit(BASE)은 `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`다.
7. main 직접 변경, merge, deploy, force push는 금지다.

## 허용 파일 (exact)

- `tests/package.json`
- `tests/package-lock.json`
- `tests/.gitignore`
- `tests/playwright.config.js`
- `tests/helpers/theme.js`
- `tests/specs/smoke.spec.js`

## 수정 금지

- `tests/` 밖의 모든 파일

## 작업

1. `tests/package.json`을 만든다.
   - `private: true`, `type: module`
   - devDependencies: `@playwright/test`, `@axe-core/playwright`
   - scripts:
     - `test`: `PLAYWRIGHT_BROWSERS_PATH=./.pw-browsers playwright test`
     - `browsers:install`: `PLAYWRIGHT_BROWSERS_PATH=./.pw-browsers playwright install chromium`
   - `npm --prefix tests install --cache tests/.npm-cache`를 실행해 lockfile을 만든다.
   - `verify-scope`, `verify-scope:selftest`, `fixtures` script는 step 1과 step 2에서 추가한다.
2. `tests/.gitignore`에 다음을 넣는다.
   - `node_modules/`
   - `.pw-browsers/`
   - `.npm-cache/`
   - `test-results/`
   - `playwright-report/`
   - `screenshots/`
3. `npm --prefix tests run browsers:install`을 실행한다.
   - 브라우저는 `tests/.pw-browsers` 안에만 설치된다.
   - 홈 디렉터리 캐시는 쓰지 않는다.
4. `tests/playwright.config.js`를 만든다.
   - testDir: `./specs`
   - webServer
     - command: `python3 -m http.server 4173 --bind 127.0.0.1`
     - cwd: 설정 파일 기준 `..`(저장소 루트)
     - url: `http://127.0.0.1:4173/index.html`
     - reuseExistingServer: true
   - use.baseURL: `http://127.0.0.1:4173`
   - projects 6개. 각각 `colorScheme`과 `metadata.theme`에 dark/light를 지정한다.
     - `mobile-dark`, `mobile-light`: 375×812
     - `tablet-dark`, `tablet-light`: 768×1024
     - `desktop-dark`, `desktop-light`: 1280×800
   - retries: 0
5. `tests/helpers/theme.js`를 만든다.
   - `test.extend`로 page fixture를 확장한다. `addInitScript`로 `localStorage.setItem(THEME_KEY, project 테마)`를 실행한다.
   - THEME_KEY는 main.js에서 확인한 실제 문자열을 쓴다.
   - `test`와 `expect`를 export한다.
   - `collectConsoleErrors(page)`를 export한다.
     - pageerror와 console.error를 모은다.
     - fonts.googleapis.com, fonts.gstatic.com 출처는 제외한다.
6. `tests/specs/smoke.spec.js`를 만든다.
   - `/index.html`을 연다.
   - `#heroName`이 `장수훈`이다.
   - `html[data-theme]`가 project 테마와 같다.
   - 콘솔 에러가 0건이다.

## 완료 기준 (AC)

- `npm --prefix tests test` → 6개 project 모두 통과
- `git status --porcelain`에 tests/ 밖 변경이 없다. step 1부터는 verify-scope가 이 확인을 자동화한다.
