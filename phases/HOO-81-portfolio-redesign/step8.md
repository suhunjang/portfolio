# Step 8 — axe-prepare

- 예상 시간: 18분
- 실행 횟수: axe-prepare spec 2회, 전체 테스트 1회, verify-scope 1회
- 선행 step: 0~7 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §3(reveal, 모달, lightbox), §7.4(modal.js), §8.1, §8.4(prepareForAxe 계약)
3. index.json에서 step 0~7이 completed인지 확인한다. 아니면 중단한다.
4. `tests/helpers/modal.js`의 `modalTitle`, `findProjectWithShots`와 reveal 동작을 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/helpers/axe-prepare.js` (신규)
- `tests/specs/axe-prepare.spec.js` (신규)

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖 전부
- 기존 tests 파일 (`modal.js`, `axe.js` 포함 — import만 한다)

## 작업

1. `axe-prepare.js`에 §8.4 `prepareForAxe(page, { scenario, projectIndex?, timeoutMs = 10000 })`를 구현한다.
   - 공통: fonts.ready + `status === 'loaded'` → 순회 스크롤(`innerHeight × 0.8` 간격, 단계마다 2 frame) → `scrollTo(0, 0)` → 모든 `.reveal`의 `.in`·visibility·opacity를 `expect.poll`로 확인
   - modal·lightbox: 열림·표시·콘텐츠 로딩 assertion 후 `include` 반환
   - 실패는 모두 `prepareForAxe: {code}` 메시지로 reject한다.
2. `axe-prepare.spec.js` (desktop-dark, desktop-light, mobile-dark)
   - page: `include === 'body'`, `revealChecked === await page.locator('.reveal').count()`이고 0보다 크다, 모든 `.reveal`이 `.in`, 반환 후 `scrollY === 0`, `scrollSteps >= 1`
   - modal (desktop): `include === '#projectModal'`, body `modal-open`, 제목이 `PROJECTS[0].title`과 같다.
   - lightbox (desktop): `include === '.lightbox'`, `.lightbox img`가 로딩 완료, 포커스가 lightbox 안에 있다.
   - 오류 계약 (desktop-dark)
     - `scenario: 'x'` → `prepareForAxe: unknown-scenario`
     - `setContent`로 `.in`이 붙지 않는 `.reveal` 1개 페이지, `timeoutMs: 500` → `prepareForAxe: reveal-hidden:1`
     - `page.route`로 이미지 요청을 abort한 뒤 lightbox → `prepareForAxe: content-not-loaded:img`
     - 실제 사이트에서 `.shot-zoom`이 없는 프로젝트 index를 `projectIndex`로 주고 lightbox → `prepareForAxe: lightbox-not-open`
     - `setContent`로 프로젝트 카드와 `.shot-zoom`이 전혀 없는 페이지에서 `projectIndex` 없이 lightbox → `prepareForAxe: no-shots-project`
     - `setContent`로 click 처리기가 없는 `[data-project="0"]` 카드만 있는 페이지에서 modal, `timeoutMs: 500` → `prepareForAxe: modal-not-open`
   - 준비 helper가 테마와 reduced-motion 설정을 바꾸지 않는다(호출 전후 `data-theme`, `matchMedia('(prefers-reduced-motion: reduce)').matches` 동일).

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-prepare.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 모두 통과
