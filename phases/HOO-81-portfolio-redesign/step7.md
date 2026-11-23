# Step 7 — focus-trap

- 예상 시간: 18분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~6 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침 `CLAUDE.md`(하네스 계약 포함)와 `README.md`를 읽는다. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서 두 개를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.2
3. index.json에서 step 0~6이 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드를 확인한다.
   - `openProjectModal(projectIndex, triggerElement)`, `closeProjectModal`
   - `ensureLightbox`의 Tab 고정 리스너
   - `openLightbox`, `closeLightbox`
   - `:focus-visible` CSS
5. 다음은 읽기 전용이다.
   - `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`
   - 하네스 managed 파일: `scripts/**`, `.claude/**`, `.codex/**`, `templates/**`, `harness-manifest.json`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. git add·commit·push는 하네스만 한다. main 직접 변경, merge, deploy는 금지다.

## tracked source 허용 파일 (exact)

- `js/main.js`
- `css/style.css` (`:focus-visible` 규칙만)
- `tests/specs/focus.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`
- `tests/test-results/**`
- `tests/playwright-report/**`

## 수정 금지

- `index.html`, `js/data.js`, `css/themes.css`
- fixtures (axe-baseline 포함. axe 해소는 step 8에서 한다)
- 기존 spec

## 작업 (TDD)

### 1. `tests/specs/focus.spec.js`를 먼저 작성한다

6개 project에서 실행한다.

- 모달 트랩: 대표 카드 1번으로 연다. Tab 20회와 Shift+Tab 20회 동안 activeElement가 `#projectModal .modal-dialog` 안에 머문다.
- lightbox 중첩 (Motion-O)
  - `.shot-zoom`으로 lightbox를 연다.
  - Tab과 Shift+Tab 각 10회 동안 activeElement가 `.lightbox` 안에 머문다.
  - Esc를 누르면 activeElement가 해당 `.shot-zoom`이 된다.
  - 이어서 Tab 20회 동안 activeElement가 모달 안에 머문다. 모달 trap이 재개됐는지 확인하는 단계다.
  - Esc를 한 번 더 누르면 포커스가 trigger 카드로 돌아온다.
- 닫기 버튼이나 backdrop으로 닫아도 포커스가 trigger로 돌아온다.
- 키보드 도달
  - Tab만으로 `#themeToggle`, 첫 `.nav-link`(desktop), 첫 `[data-featured-card]`, 첫 `.project-card.has-detail`에 도달할 수 있다.
  - 도달한 각 요소의 outline-style이 none이 아니다.

### 2. `js/main.js`

`trapFocus(container, { returnFocusTo } = {}): () => void`를 구현한다.

- 모듈 스코프에 `trapStack`을 둔다.
- document keydown Tab 핸들러는 1개만 등록하고, 스택 최상위 container 안에서만 포커스를 순환시킨다.
- container 안의 포커스 가능 요소가 1개뿐이면 그 요소에 고정한다.
- 반환하는 `release()`는 스택에서 제거하고, returnFocusTo로 포커스를 옮기고, 직전 trap을 재개한다. 중복 호출은 무시한다.

모달과 lightbox에 연결한다.

- openProjectModal 끝: `releaseModalTrap = trapFocus(dialog, { returnFocusTo: lastFocused })`
- closeProjectModal: closeLightbox → 모달 숨김 → `releaseModalTrap()` 순서로 실행한다. 기존 포커스 복귀 코드와 중복되지 않게 정리한다.
- openLightbox: `releaseLightboxTrap = trapFocus(lightbox, { returnFocusTo: btn })`
- closeLightbox: release를 호출한다.
- ensureLightbox의 기존 Tab 고정 리스너는 제거한다.

## 완료 기준 (AC)

- `npm --prefix tests test && npm --prefix tests run verify-scope`가 모두 통과한다.
- axe에서 baseline에 없는 새 key가 0건이다.
