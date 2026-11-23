# Step 9 — axe-prepare-page

- 예상 시간: 14분
- 실행 횟수: axe-prepare-page spec 2회, 전체 테스트 1회, verify-scope 1회
- 선행 step: 0~8 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §3(reveal), §8.4(공통 오류 계약, page 준비)
3. index.json에서 step 0~8이 completed인지 확인한다. 아니면 중단한다.
4. reveal의 IntersectionObserver 동작과 `.reveal`/`.in` 클래스를 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/helpers/axe-prepare.js` (신규: `PREPARE_PREFIX`, `prepareError`, `withPrepareCode`, `preparePage`만)
- `tests/specs/axe-prepare-page.spec.js` (신규)

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖 전부
- 기존 tests 파일
- modal·lightbox 준비, `prepareForAxe` (step 10·11에서 한다)

## 작업

1. `axe-prepare.js`
   - `PREPARE_PREFIX = 'prepareForAxe: '`
   - `prepareError(code, cause?)`: message `prepareForAxe: {code}`, `.code`, `.cause`
   - `withPrepareCode(code, fn)`: fn 실패를 `prepareError(code, 원인)`로 바꾼다. 이미 `prepareForAxe: `로 시작하는 오류는 그대로 전달한다.
   - `preparePage(page, { timeoutMs = 10000 } = {})`: fonts.ready + `status === 'loaded'`(`fonts-not-ready`) → 순회 스크롤(`innerHeight × 0.8`, 단계마다 2 frame) → `scrollTo(0, 0)` → 모든 `.reveal`의 `.in`·visibility·opacity를 `expect.poll`로 확인(`reveal-hidden:{n}`). `{ revealChecked, scrollSteps }` 반환
2. `axe-prepare-page.spec.js` (desktop-dark, desktop-light, mobile-dark)
   - 실제 사이트: `revealChecked === await page.locator('.reveal').count()`이고 0보다 크다, 모든 `.reveal`이 `.in`, 반환 후 `scrollY === 0`, `scrollSteps >= 1`
   - `setContent`로 `.in`이 붙지 않는 `.reveal` 1개 페이지, `timeoutMs: 500` → `prepareForAxe: reveal-hidden:1`, `err.code === 'reveal-hidden:1'`
   - `prepareError('x')`의 message·code
   - `withPrepareCode('fonts-not-ready', () => Promise.reject(new Error('boom')))` → message `prepareForAxe: fonts-not-ready`, `cause.message === 'boom'`
   - `withPrepareCode('a', () => Promise.reject(prepareError('b')))` → 코드 `b`가 그대로 유지된다.
   - 호출 전후 `data-theme`과 `matchMedia('(prefers-reduced-motion: reduce)').matches`가 같다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-prepare-page.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 모두 통과
