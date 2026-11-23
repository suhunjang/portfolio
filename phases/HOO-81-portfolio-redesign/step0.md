# Step 0 — tests-env-setup

- 예상 시간: 14분
- 실행 횟수: 의존성 설치 1회, 브라우저 설치 1회, 테스트 1회
- 선행 step: 없음

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §3, §11.1~§11.4
3. `phases/HOO-81-portfolio-redesign/index.json`을 확인한다. 이 step은 선행 step이 없다.
4. 현재 코드에서 다음을 확인한다.
   - `js/main.js`의 `THEME_KEY`
   - 루트 package.json이 없음
   - `tests/`가 없음
5. 빌더는 다음을 읽기만 하고 수정하지 않는다: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - 하네스만 실행:
     - Git 상태를 바꾸는 명령(checkout, switch, add, commit, push, reset, stash, merge, rebase, tag 등)
     - Harness 운영 명령(`harness --project-root . ...`)
   - 빌더와 검증 스크립트도 사용 가능: 검증용 Git 읽기 명령(`git rev-parse`, `git diff`, `git show`, `git ls-files`, `git ls-tree`, `git status`, `git log`)
   - 금지: main 직접 변경, merge, deploy
7. BASE = `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`
8. 공통 실행 계약: 이 step에서 `tests/scripts/with-env.sh`를 가장 먼저 만든다. 이후 npm·node·playwright는 모두 이 래퍼로 실행한다.

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
2. `tests/.gitignore`: §11.1의 7줄을 같은 순서로 쓰고, 끝에 개행 1개를 둔다.
3. `tests/package.json`
   - `private: true`, `type: module`
   - devDependencies: `@playwright/test`, `@axe-core/playwright`
   - scripts: `test`는 `playwright test`, `browsers:install`은 `playwright install chromium`
4. 설치
   - `sh tests/scripts/with-env.sh npm --prefix tests install`
   - `sh tests/scripts/with-env.sh npm --prefix tests run browsers:install`
5. `playwright.config.js`
   - testDir `./specs`, reporter list, retries 0, outputDir `./test-results`
   - webServer: `python3 -m http.server 4173 --bind 127.0.0.1`, cwd `..`, reuseExistingServer
   - baseURL: `http://127.0.0.1:4173`
   - projects 6개 (각각 `colorScheme`, `metadata.theme` 지정)
     - `mobile-dark`, `mobile-light`: 375×812
     - `tablet-dark`, `tablet-light`: 768×1024
     - `desktop-dark`, `desktop-light`: 1280×800
6. `tests/helpers/theme.js`
   - `test.extend` fixture: `addInitScript`가 `THEME_KEY`가 null일 때만 project 테마를 저장한다.
   - `collectConsoleErrors(page): ErrorCollector`를 설계 §11.4 계약 그대로 구현한다.
     - 호출 즉시 listener를 등록한다.
     - pageerror는 빠짐없이 수집한다.
     - console.error는 location url의 hostname이 정확히 fonts.googleapis.com 또는 fonts.gstatic.com일 때만 제외한다.
     - `finish()`는 `Promise<{ pageErrors, consoleErrors }>`를 반환한다.
     - 필드는 `ErrorRecord { kind, message, url, line, column }`로 고정한다.
   - export: `test`, `expect`, `collectConsoleErrors`
7. `tests/specs/smoke.spec.js`
   - `const c = collectConsoleErrors(page)`를 `goto`보다 먼저 호출한다.
   - `goto` 후 확인한다.
     - `#heroName`이 장수훈이다.
     - `data-theme`이 project 테마와 같다.
   - `const r = await c.finish()` 후 `pageErrors`와 `consoleErrors`가 모두 `[]`이다.
   - collector 자체 검증: `page.evaluate`로 `setTimeout(() => { throw new Error('x') })`를 실행하면 `pageErrors`에 1건이 기록된다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test`가 6개 project 모두에서 통과한다.
- `git status --porcelain --untracked-files=all` 출력에 `tests/` 밖 변경이 없고, runtime 경로도 나타나지 않는다.
