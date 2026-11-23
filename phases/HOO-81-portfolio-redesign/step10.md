# Step 10 — axe-prepare-modal

- 예상 시간: 17분
- 실행 횟수: modal·page spec 2회, 전체 테스트 1회, verify-scope 1회
- 선행 step: 0~9 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §3(모달 마크업), §5(같은 data-project), §7.4(modal.js `gridCard`, `modalTitle`), §8.4(콘텐츠 로딩 검사, modal 준비, 오류 코드, 합성 fixture 규칙)
3. index.json에서 step 0~9가 completed인지 확인한다. 아니면 중단한다.
4. `modal.js`의 `gridCard`, `modalTitle`, `closeVia`와 `axe-prepare.js`의 `prepareError`, `withPrepareCode`를 확인한다. 현행 `#modalBody` 렌더 구조(`#modalTitle`, `.modal-blurb`, `.modal-section`)와 `.modal-close` 위치를 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/helpers/axe-prepare.js` (추가만: `MODAL_ROOT`, `MODAL_BODY_TEXT`, `assertContentLoaded`, `prepareModal`)
- `tests/specs/axe-prepare-modal.spec.js` (신규)

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖 전부
- 기존 tests 파일 (`modal.js`, `axe.js`, `axe-prepare-page.spec.js` 포함 — import만 한다)
- step 9 함수의 동작
- lightbox 준비, `prepareOverlay`, `prepareForAxe` (step 11에서 한다)

## 작업

1. `axe-prepare.js`에 추가한다.
   - `MODAL_ROOT = '#projectModal'`
   - `MODAL_BODY_TEXT = '#modalBody .modal-blurb, #modalBody .modal-section'` (제목 `#modalTitle`과 닫기 버튼 `.modal-close` 제외)
   - `assertContentLoaded(locator, timeoutMs, { textLocator = null } = {})` — §8.4 계약 그대로: locator 안 img(`content-not-loaded:img`)·svg(`content-not-loaded:svg`) 검사, textLocator가 있으면 비어 있지 않은 텍스트 검사(`content-not-loaded:text`), null이면 텍스트 검사 생략
   - `prepareModal(page, { projectIndex = 0, timeoutMs = 10000 } = {})`
     - `gridCard(page, N)` count가 1이 아니면 `project-card-not-found:{N}`
     - grid 카드 click → body `modal-open`, `#projectModal` visible·opacity 1 (`modal-not-open`)
     - `modalTitle(page)` 텍스트 = `norm(PROJECTS[N].title)` (`modal-not-open`)
     - `assertContentLoaded(page.locator(MODAL_ROOT), timeoutMs, { textLocator: page.locator(MODAL_BODY_TEXT) })`
     - `{ include: '#projectModal', projectIndex: N }` 반환
2. `axe-prepare-modal.spec.js` (desktop-dark, desktop-light)
   - 실제 사이트: `prepareModal(page)` → `include === '#projectModal'`, body `modal-open`, 제목이 `PROJECTS[0].title`과 같고, `MODAL_BODY_TEXT` 텍스트가 비어 있지 않다.
   - grid 범위·중복 data-project (동작 모달 fixture, §8.4 규칙)
     - `#heroFeatured` 안 `<button data-featured-card data-project="1">`과 `#projectGrid .project-card[data-project="1"]`를 함께 둔다.
     - `prepareModal({ projectIndex: 1 })` 성공, grid 카드 click 1, 대표 버튼 click 0, `__opens === 1`
   - `project-card-not-found`: grid 밖 `<button data-featured-card data-project="3">`만 있는 fixture → `prepareForAxe: project-card-not-found:3`, 대표 버튼 click 0
   - `modal-not-open`: click handler가 없는 `#projectGrid .project-card[data-project="0"]`만 있는 별도 fixture, `timeoutMs: 500` → `prepareForAxe: modal-not-open`
   - `content-not-loaded:text`: 동작 모달 fixture에서 handler가 `#modalTitle`은 정상 제목으로 채우고 `.modal-blurb`는 빈 문자열, `.modal-section`은 0개로 둔다. `timeoutMs: 500` → 제목 검사는 통과하고 `prepareForAxe: content-not-loaded:text`로 실패한다.
   - `assertContentLoaded` 단위
     - 텍스트 없는 `div` + `textLocator: null` → 통과 (텍스트 검사 생략)
     - 같은 `div`를 `textLocator`로 주면 → `prepareForAxe: content-not-loaded:text`

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-prepare-modal.spec.js axe-prepare-page.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 모두 통과
