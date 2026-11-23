# Step 9 — axe-prepare-overlay

- 예상 시간: 18분
- 실행 횟수: overlay·page spec 2회, 전체 테스트 1회, verify-scope 1회
- 선행 step: 0~8 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §3(모달, lightbox), §5(같은 data-project), §7.4(modal.js `gridCard`, `findProjectWithShots`), §8.4(overlay 준비, 결합 진입점, 오류 코드)
3. index.json에서 step 0~8이 completed인지 확인한다. 아니면 중단한다.
4. `modal.js`의 `gridCard`, `modalTitle`, `findProjectWithShots`와 `axe-prepare.js`의 `preparePage`, `prepareError`, `withPrepareCode`를 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/helpers/axe-prepare.js` (추가만: `prepareOverlay`, `prepareForAxe`)
- `tests/specs/axe-prepare-overlay.spec.js` (신규)

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖 전부
- 기존 tests 파일 (`modal.js`, `axe.js`, `axe-prepare-page.spec.js` 포함 — import만 한다)
- step 8 함수의 동작

## 작업

1. `axe-prepare.js`에 추가한다.
   - `prepareOverlay(page, { scenario, projectIndex?, timeoutMs = 10000 })`
     - 클릭 대상은 정확히 `gridCard(page, N)`, 즉 `#projectGrid .project-card[data-project="N"]`. count가 1이 아니면 `project-card-not-found:{N}`
     - modal: 열림(body `modal-open`, `#projectModal` visible, opacity 1) → 제목 일치 → img·svg·text 로딩 확인 → `{ include: '#projectModal', projectIndex }`
     - lightbox: `projectIndex` 기본값 `findProjectWithShots`(null이면 `no-shots-project`) → 모달 열기 → 첫 `.shot-zoom` click → 열림·포커스·img 로딩 확인 → `{ include: '.lightbox', projectIndex }`
     - 그 밖의 scenario → `unknown-scenario`
   - `prepareForAxe(page, { scenario, projectIndex?, timeoutMs })`: scenario 검증 → `preparePage` → page면 `include: 'body'`, 그 밖에는 `prepareOverlay` 결과를 합쳐 반환
2. `axe-prepare-overlay.spec.js` (desktop-dark, desktop-light)
   - 실제 사이트
     - `prepareForAxe({ scenario: 'page' })` → `include === 'body'`, `projectIndex === null`
     - modal → `include === '#projectModal'`, body `modal-open`, 제목이 `PROJECTS[0].title`과 같다.
     - lightbox → `include === '.lightbox'`, `.lightbox img` 로딩 완료, 포커스가 lightbox 안
     - `.shot-zoom`이 없는 grid 카드 index를 `projectIndex`로 주고 lightbox → `prepareForAxe: lightbox-not-open`
     - `page.route`로 이미지 요청을 abort한 뒤 lightbox → `prepareForAxe: content-not-loaded:img`
   - 오류 코드 (desktop-dark)
     - `prepareForAxe({ scenario: 'x' })`, `prepareOverlay({ scenario: 'page' })` → `prepareForAxe: unknown-scenario`
     - `setContent`로 `.shot-zoom`이 없는 grid 카드만 있는 페이지에서 `projectIndex` 없이 lightbox → `prepareForAxe: no-shots-project`
     - `setContent`로 click 처리기가 없는 `#projectGrid .project-card[data-project="0"]`만 있는 페이지, `timeoutMs: 500` → `prepareForAxe: modal-not-open`
     - `setContent`로 grid 밖 `<button data-featured-card data-project="3">`만 있고 grid 카드는 없는 페이지 → `prepareForAxe: project-card-not-found:3`, 대표 버튼 click 수 0
   - grid 카드 클릭 범위 회귀 (합성 페이지)
     - `setContent`로 `#heroFeatured` 안 `<button data-featured-card data-project="1">`과 `#projectGrid .project-card[data-project="1"]`를 함께 둔다. 각 요소의 click 수를 `window.__clicks`에 기록한다.
     - grid 카드 click 처리기는 현행 모달 마크업(`#projectModal`과 `modalTitle`이 가리키는 제목 요소)을 최소 복제해 열고 body에 `modal-open`을 붙인다. `window.PROJECTS`는 합성 정의한다.
     - `prepareOverlay({ scenario: 'modal', projectIndex: 1 })` 성공 후 grid 카드 click 1, 대표 버튼 click 0
     - 같은 합성 구성에서 grid 카드 2개(0: shots 없음, 1: shots 있음)와 대표 버튼(`data-project="0"`)을 두고 `findProjectWithShots(page)` → 1, 대표 버튼 click 0

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-prepare-overlay.spec.js axe-prepare-page.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 모두 통과
