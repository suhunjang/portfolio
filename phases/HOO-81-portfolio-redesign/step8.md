# Step 8 — print-pdf

- 예상 시간: 15분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~7 completed

## 공통: 시작 전 필수 확인 (read-first)

1. `README.md`를 읽는다. `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서 두 개를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §10
3. index.json에서 step 0~7이 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드를 확인한다.
   - `css/style.css`의 `@media print` 블록: 숨김 대상, `#typed`, `#aboutSummary`, reveal 처리
   - step 5·6에서 추가된 `#heroFeatured`, `.subsection-title`, `#contact`
5. `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`는 읽기 전용이다. 문서 변경은 하네스만 한다.
6. main 직접 변경, merge, deploy는 금지다.

## 허용 파일 (exact)

- `css/style.css` (`@media print` 블록만)
- `tests/specs/print.spec.js`

## 수정 금지

- `index.html`, `js/*`, `css/themes.css`
- 기존 tests

## 작업 (TDD)

### 1. 테스트 먼저 작성

`tests/specs/print.spec.js`를 작성한다. desktop-dark와 desktop-light에서만 실행하고, 나머지 project는 skip한다.

시나리오 A — 새 페이지

스크롤하지 않고 기본 모션 상태(reveal 미진입)에서 `emulateMedia({ media: print })`를 적용한다.

- 다음 요소가 visibility visible이고 opacity 1이다.
  - `#heroName`, `#heroTagline`, `#heroStats`, `#heroFeatured`
  - 각 섹션의 `.section-title`
- display가 none이 아닌 모든 `.reveal`이 다음을 만족한다.
  - opacity 1, visibility visible
  - textContent.trim()이 비어 있지 않거나, img 또는 svg를 포함한다.
- `.theme-toggle`, `.menu-toggle`, `.scroll-hint`, `#projectModal`, `.lightbox`가 display none이다.
- `page.pdf({ format: A4 })` 결과가 다음을 만족한다.
  - 10240바이트를 넘는다.
  - `/Type /Page`가 1회 이상 나온다.

시나리오 B — 오버레이가 열린 상태

Motion-O 모달과 lightbox를 연 뒤 print를 에뮬레이트한다.

- `#projectModal`과 `.lightbox`가 display none이다.
- 시나리오 A의 본문 가시성 검사를 통과한다.
- PDF가 10240바이트를 넘는다.

### 2. `@media print` 수정

- `.reveal`: opacity 1, transform none, visibility visible
- `#heroFeatured`: 인쇄에 포함하고, 그리드를 단순화한다.
- `.modal`, `.lightbox`, `.theme-toggle`, `.menu-toggle`, `.scroll-hint`, `.navbar`: display none !important
- `body.modal-open`: 스크롤 잠금을 해제한다.
- 기존 `#typed`, `#aboutSummary` 숨김은 유지한다.

## 완료 기준 (AC)

`npm --prefix tests test && npm --prefix tests run verify-scope` → 모두 통과
