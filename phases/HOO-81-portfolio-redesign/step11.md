# Step 11 — axe-prepare-lightbox

- 예상 시간: 18분
- 실행 횟수: lightbox·modal·page spec 2회, 전체 테스트 1회, verify-scope 1회
- 선행 step: 0~10 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §3(lightbox), §7.4(`findProjectWithShots`), §8.4(lightbox 준비·결합 진입점, 오류 코드, 합성 fixture 규칙)
3. index.json에서 step 0~10이 completed인지 확인한다. 아니면 중단한다.
4. `modal.js`의 `findProjectWithShots`, `closeVia`와 `axe-prepare.js`의 `preparePage`, `prepareModal`, `assertContentLoaded`를 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/helpers/axe-prepare.js` (추가만: `assertContentLoaded`의 img·svg 검사, `prepareLightbox`, `prepareOverlay`, `prepareForAxe`)
- `tests/specs/axe-prepare-lightbox.spec.js` (신규)

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖 전부
- 기존 tests 파일 (`modal.js`, `axe.js`, `axe-prepare-page.spec.js`, `axe-prepare-modal.spec.js` 포함 — import만 한다)
- step 9·10 함수의 기존 동작 (text 검사, grid 범위)

## 작업

1. `axe-prepare.js`에 추가한다.
   - `assertContentLoaded`: img `complete && naturalWidth > 0`(`content-not-loaded:img`), svg bounding box width·height > 0(`content-not-loaded:svg`) 검사를 추가한다.
   - `prepareLightbox(page, { projectIndex?, timeoutMs = 10000 } = {})`: 기본 index는 `findProjectWithShots`(null → `no-shots-project`) → `prepareModal` → 첫 `.shot-zoom` click(없거나 열리지 않으면 `lightbox-not-open`) → 열림·포커스 확인 → `assertContentLoaded(.lightbox)` → `{ include: '.lightbox', projectIndex }`
   - `prepareOverlay(page, { scenario, ... })`: modal/lightbox 분기, 그 밖 `unknown-scenario`
   - `prepareForAxe(page, { scenario, projectIndex?, timeoutMs })`: scenario 검증 → `preparePage` → page면 `include: 'body'`, 그 밖에는 `prepareOverlay` 결과를 합쳐 반환
2. `axe-prepare-lightbox.spec.js` (desktop-dark, desktop-light)
   - 실제 사이트
     - `prepareForAxe({ scenario: 'page' })` → `include === 'body'`, `projectIndex === null`
     - `prepareForAxe({ scenario: 'modal' })` → `include === '#projectModal'`
     - `prepareForAxe({ scenario: 'lightbox' })` → `include === '.lightbox'`, `.lightbox img` 로딩 완료, 포커스가 lightbox 안
     - `.shot-zoom`이 없는 grid 카드 index를 `projectIndex`로 주고 lightbox → `prepareForAxe: lightbox-not-open`
     - `page.route`로 이미지 요청을 abort한 뒤 lightbox → `prepareForAxe: content-not-loaded:img`
   - `unknown-scenario`: `prepareForAxe({ scenario: 'x' })`, `prepareOverlay({ scenario: 'page' })` → `prepareForAxe: unknown-scenario`
   - `findProjectWithShots` 탐색 (동작 모달 fixture, §8.4 규칙: 제목, 비어 있지 않은 본문, `[data-modal-close]`, grid 카드 click handler와 닫기 handler 모두 제공)
     - no-shots: grid 카드 2개(0, 1) 모두 `.shot-zoom` 없음 + grid 밖 대표 버튼(`data-project="0"`)
       - `findProjectWithShots(page)` → null, `__opens === 2`, `__closes === 2`, 끝난 뒤 `modal-open` 없음, 대표 버튼 click 0
       - `prepareForAxe({ scenario: 'lightbox' })` → `prepareForAxe: no-shots-project` (모든 카드를 정상적으로 열고 닫은 뒤에만 이 코드가 난다는 것을 위 카운터로 함께 확인)
     - shots 있음: grid 카드 0(shots 없음), 1(`.shot-zoom` 있음) + 대표 버튼(`data-project="1"`) → `findProjectWithShots(page)` → 1, `__opens === 2`, `__closes === 2`, 대표 버튼 click 0
   - 이미지·SVG 오류 fixture (동작 모달 fixture)
     - 모달 본문에 존재하지 않는 src의 img → `prepareModal` 결과가 `prepareForAxe: content-not-loaded:img`
     - 모달 본문에 width·height 0인 svg → `prepareForAxe: content-not-loaded:svg`

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-prepare-lightbox.spec.js axe-prepare-modal.spec.js axe-prepare-page.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 모두 통과
