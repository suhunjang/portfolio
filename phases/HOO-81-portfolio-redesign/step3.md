# Step 3 — interaction-regression

- 예상 시간: 18분
- 실행 횟수: 테스트 1~2회(각 웹서버 1회), verify-scope 1회
- 선행 step: 0~2 completed

## 공통: 시작 전 필수 확인 (read-first)

1. `README.md`를 읽는다. `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서 두 개를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` — §3(모달, lightbox, 메뉴, reveal, typing 구조), §11
3. index.json에서 step 0~2가 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드를 확인한다.
   - `js/main.js`의 `openProjectModal`, `closeProjectModal`, `openLightbox`, `closeLightbox`
   - projectGrid의 click/keydown 위임, Esc 핸들러
   - `THEME_KEY`, 메뉴 토글, 스크롤스파이 배열, reveal
   - Motion-O(PROJECTS[0])의 `detail.shots`
5. `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`는 읽기 전용이다. 문서 변경은 하네스만 한다.
6. main 직접 변경, merge, deploy는 금지다.

## 허용 파일 (exact)

- `tests/specs/interaction.spec.js`
- `tests/specs/first-visit.spec.js`
- `tests/helpers/modal.js`

## 수정 금지

- `tests/` 밖의 모든 파일(사이트 포함)
- 기존 tests 파일

## 작업

### 1. `tests/helpers/modal.js`

다음 함수를 만든다.
- `openFirstProjectByClick(page)`: 첫 프로젝트를 클릭으로 열고 trigger locator를 반환한다.
- `openFirstProjectByEnter(page)`: 첫 프로젝트를 Enter로 열고 trigger locator를 반환한다.
- `closeVia(page, how)`: how는 button, backdrop, esc 중 하나다. backdrop은 `.modal-backdrop`의 position {x:5, y:5}를 클릭한다.
- `expectFocused(locator)`

셀렉터는 `[data-project]`와 `#projectModal`처럼 이후 step에서도 유지되는 것만 쓴다.

### 2. `tests/specs/interaction.spec.js` (6개 project 전부)

- 테마
  - `#themeToggle`을 누르면 `data-theme`이 반대 값이 된다.
  - 새로고침 후에도 유지되고, localStorage THEME_KEY와 일치한다.
- 모달 (첫 `.project-card.has-detail`)
  - click으로 연 뒤 button, backdrop, esc 각 경로로 닫는다. 경로마다 `#projectModal`이 hidden이고 포커스가 trigger 카드로 돌아와야 한다.
  - focus 후 Enter로 열고 esc로 닫을 때도 포커스가 trigger로 복귀한다.
  - `#modalTitle`이 해당 title과 같다.
  - 열면 `body.modal-open`이 붙고, 닫으면 해제된다.
- lightbox (Motion-O 모달)
  - `.shot-zoom`을 누르면 `.lightbox`가 보인다.
  - Esc 1회에 lightbox만 닫히고 포커스가 그 `.shot-zoom`으로 돌아온다.
  - Esc 2회째에 모달이 닫히고 포커스가 카드로 돌아온다.
- 메뉴 (mobile project만, 나머지는 skip)
  - `#menuToggle`을 누르면 `aria-expanded=true`이고 `#navLinks`가 visible이다.
  - `.nav-link`를 누르면 `aria-expanded=false`가 된다.
- 스크롤스파이 (desktop만)
  - nav의 `#projects` 링크를 클릭하면 500ms 뒤 해당 링크가 `.active`다.
- typing
  - 1.5초 안에 `#typed`가 비어 있지 않다.
- reduced motion (`browser.newContext({ reducedMotion: reduce })`)
  - 모든 `.reveal`에 `.in`이 붙어 있다.
  - `#typed`가 `PROFILE.roles[0]`과 같다.
- 콘솔
  - 각 테스트의 collectConsoleErrors 결과가 0건이다.

### 3. `tests/specs/first-visit.spec.js` (desktop-dark에서만 실행)

- storage가 없는 `browser.newContext({ colorScheme: light })`에서 `data-theme=light`이고 THEME_KEY가 null이다.
- colorScheme이 dark면 `data-theme=dark`다.

## 완료 기준 (AC)

`npm --prefix tests test && npm --prefix tests run verify-scope` → BASE 사이트에서 모두 통과한다.
