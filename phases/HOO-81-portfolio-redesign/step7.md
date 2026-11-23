# Step 7 — focus-accessibility

- 예상 시간: 20분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~6 completed

## 공통: 시작 전 필수 확인 (read-first)

1. `README.md`를 읽는다. `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서 두 개를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md` (대비를 조정해도 톤 유지)
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8 trapFocus 계약
3. index.json에서 step 0~6이 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드를 확인한다.
   - `openProjectModal`(trigger 인자)과 `closeProjectModal`
   - `ensureLightbox`의 Tab 고정 리스너
   - `openLightbox`와 `closeLightbox`
   - `:focus-visible` CSS
   - `tests/fixtures/axe-known.json`
5. `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`는 읽기 전용이다. 문서 변경은 하네스만 한다.
6. main 직접 변경, merge, deploy는 금지다.

## 허용 파일 (exact)

- `js/main.js`
- `css/style.css`
- `css/themes.css` (대비 토큰의 명도 값만)
- `tests/specs/focus.spec.js`
- `tests/fixtures/axe-known.json` (`[]`로 비우는 것만)

## 수정 금지

- `index.html`, `js/data.js`
- 기존 spec과 다른 fixture
- `css/themes.css`의 토큰 이름이나 구조

## 작업 (TDD)

### 1. 테스트 먼저 작성

`tests/specs/focus.spec.js`를 작성한다. 6개 project에서 실행한다.

- 모달 트랩
  - 대표 카드 1번으로 모달을 연다.
  - Tab 20회, Shift+Tab 20회 동안 activeElement가 항상 `#projectModal .modal-dialog` 안에 있다.
- lightbox 중첩
  - Motion-O 모달에서 `.shot-zoom`을 연다.
  - Tab과 Shift+Tab 각 10회 동안 activeElement가 `.lightbox` 안에 있다.
  - Esc를 누르면 activeElement가 그 `.shot-zoom`이다.
  - 이어서 Tab 20회 동안 activeElement가 모달 안에 있다.
  - 다시 Esc를 누르면 포커스가 trigger 카드로 돌아간다.
- 닫기 버튼이나 backdrop으로 닫아도 포커스가 trigger로 돌아간다.
- 키보드 도달
  - Tab만으로 `#themeToggle`, 첫 `.nav-link`(desktop), 첫 `[data-featured-card]`, 첫 `.project-card.has-detail`에 도달할 수 있다.
  - 도달한 요소의 computed outline-style이 none이 아니다.

### 2. `js/main.js`

`trapFocus(container, { returnFocusTo } = {}): () => void`를 구현한다.

- 모듈 스코프에 `trapStack`을 둔다.
- document keydown Tab 핸들러는 1개만 두고, 스택 최상위 container 안에서만 포커스를 순환시킨다.
- container 안에 포커스 가능한 요소가 1개뿐이면 그 요소에 포커스를 고정한다.
- 반환하는 `release()`는 다음 순서로 동작한다.
  1. 스택에서 자기 trap을 제거한다.
  2. `returnFocusTo`로 포커스를 옮긴다.
  3. 직전 trap이 다시 최상위가 되어 재개된다.
- `release()`를 중복 호출하면 무시한다.

모달과 lightbox에 연결한다.

- 모달
  - openProjectModal 끝에서 `releaseModalTrap = trapFocus(dialog, { returnFocusTo: lastFocused })`를 저장한다.
  - closeProjectModal은 closeLightbox → 숨김 → `releaseModalTrap()` 순서로 동작한다.
  - 기존 lastFocused 복귀 코드와 중복되지 않게 정리한다.
- lightbox
  - openLightbox에서 `releaseLightboxTrap = trapFocus(lightbox, { returnFocusTo: btn })`를 저장한다.
  - closeLightbox에서 `releaseLightboxTrap()`을 호출한다.
- ensureLightbox의 기존 Tab 고정 리스너를 제거한다.

### 3. axe 위반 해소

- `tests/fixtures/axe-known.json`을 `[]`로 만든다.
- 남은 위반은 CSS 명도 조정과 main.js 속성 수정으로 해결한다.
- 문구를 바꿔야만 해결되는 위반이면 중단하고 보고한다.

## 완료 기준 (AC)

`npm --prefix tests test && npm --prefix tests run verify-scope`가 모두 통과한다.

- axe.spec의 page, modal, lightbox 시나리오를 두 테마로 검사해 serious/critical 위반이 0건이다.
- known 목록은 비어 있다.
