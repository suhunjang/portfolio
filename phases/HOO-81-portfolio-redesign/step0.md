# Step 0 — test-harness-baseline

설계: `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §5.4, §5.6

## 목표

사이트 코드를 바꾸기 전에 기존 기능을 고정하는 회귀 테스트를 만든다. 이 테스트는 현재 코드에서 모두 통과해야 한다.

## 변경 허용 파일

- `tests/**` 만. 사이트 파일(`index.html`, `css/`, `js/`)은 수정 금지.

## 작업

1. `tests/package.json`을 만든다.
   - `private: true`
   - `scripts.test = playwright test`
   - devDependencies: `@playwright/test`, `@axe-core/playwright`
   - `npm --prefix tests install`로 `tests/package-lock.json`을 생성한다.
   - `npx --prefix tests playwright install chromium`으로 브라우저를 설치한다.
2. `tests/playwright.config.js`를 만든다.
   - testDir는 `./specs`, baseURL은 `http://127.0.0.1:4173`이다.
   - webServer 명령은 `python3 -m http.server 4173 --bind 127.0.0.1`이고 cwd는 저장소 루트(`..`)다. `reuseExistingServer: true`.
   - projects: chromium × viewport 375×812, 768×1024, 1280×800
3. `tests/.gitignore`에 `node_modules/`, `test-results/`, `playwright-report/`를 넣는다.
4. `tests/specs/baseline.spec.js`에 다음을 테스트한다.
   - 콘텐츠 보존: 페이지의 `STATS`, `CAREER`, `PROJECTS`, `STRENGTHS`, `SKILLS` 전역 길이와 렌더링된 요소 수가 일치하는지, 프로젝트 카드 제목이 `PROJECTS[i].title`과 일치하는지 확인한다.
   - 테마:
     - 토글을 누르면 `html[data-theme]`가 바뀐다.
     - 새로고침 후에도 `localStorage`의 값이 유지된다.
     - `colorScheme: light` 컨텍스트에서 첫 방문하면 light가 적용된다.
   - 메뉴(375px 전용):
     - `#menuToggle` 클릭 시 `aria-expanded`가 true가 되고 `#navLinks`가 보인다.
     - 링크를 클릭하면 메뉴가 닫힌다.
   - 모달:
     - 첫 프로젝트 카드를 활성화하면 `#projectModal`이 보이고 `#modalTitle`이 존재한다.
     - Esc를 누르면 닫히고 포커스가 원래 카드로 돌아간다.
     - backdrop 클릭으로도 닫힌다.
   - lightbox: 갤러리 이미지가 있는 프로젝트(Motion-O)의 모달에서 이미지 버튼을 누르면 `.lightbox`가 열린다. Esc를 한 번 누르면 lightbox만 닫히고, 두 번째 Esc에 모달이 닫힌다.
   - 모션:
     - `reducedMotion: reduce`일 때 `.reveal` 요소가 모두 보인다(opacity 1).
     - 기본 설정에서는 `#typed`에 텍스트가 채워진다.
   - 콘솔: `pageerror`가 없고, fonts.googleapis.com / fonts.gstatic.com 외의 console error가 0건이다.
   - 접근성: `@axe-core/playwright`로 dark·light 두 테마를 검사해 serious/critical 위반을 기록한다. baseline에 이미 위반이 있으면 해당 rule id를 `tests/specs/axe-known.json`에 기록하고 테스트는 통과시킨다. 이 목록은 Step 3에서 비운다.

## 완료 기준

- `npm --prefix tests test`가 현재 사이트 코드에서 3개 viewport 모두 통과한다.
- `git diff --stat`에 `tests/` 밖 변경이 없다.

## 검증 명령

- `npm --prefix tests install`
- `npx --prefix tests playwright install chromium`
- `npm --prefix tests test`
