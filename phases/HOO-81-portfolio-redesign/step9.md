# Step 9 — print-pdf

- 예상 시간: 15분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~8 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(하네스 계약 포함), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §10
3. index.json에서 step 0~8이 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드를 확인한다.
   - `@media print` 블록
   - `ensureLightbox`: 새 페이지에는 `.lightbox`가 없다.
   - `#heroFeatured`, `.subsection-title`, `#contact`
5. 다음은 읽기 전용이다.
   - `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`
   - 하네스 managed 파일: `scripts/**`, `.claude/**`, `.codex/**`, `templates/**`, `harness-manifest.json`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. git add·commit·push는 하네스만 한다. main 직접 변경, merge, deploy는 금지다.

## tracked source 허용 파일 (exact)

- `css/style.css` (`@media print` 블록만)
- `tests/specs/print.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`
- `tests/test-results/**`
- `tests/playwright-report/**`

## 수정 금지

- `index.html`, `js/*`, `css/themes.css`
- 기존 tests

## 작업 (TDD)

### 1. `tests/specs/print.spec.js` 작성

desktop-dark와 desktop-light에서만 실행하고, 다른 project는 skip한다.

시나리오 A — 새 페이지, 스크롤 없음, 기본 모션

`emulateMedia({ media: print })`를 적용한 뒤 다음을 확인한다.

- 다음 요소의 visibility가 visible이고 opacity가 1이다.
  - `#heroName`, `#heroTagline`, `#heroStats`, `#heroFeatured`
  - 각 섹션의 `.section-title`
- display가 none이 아닌 모든 `.reveal`이 다음을 만족한다.
  - opacity 1, visibility visible
  - textContent가 비어 있지 않거나 img 또는 svg를 포함한다.
- `.theme-toggle`, `.menu-toggle`, `.scroll-hint`, `#projectModal`이 display none이다.
- `.lightbox`는 count가 0이거나, 있으면 모두 display none이다.
- `page.pdf({ format: A4 })` 결과가 10240바이트를 넘고, `/Type /Page`가 1회 이상 나온다.

시나리오 B — 모달과 lightbox를 연 상태

1. screen 미디어에서 Motion-O 모달과 lightbox를 연다.
2. `.lightbox`가 count 1이고 visible인지 먼저 확인한다.
3. print로 전환한다.
4. 다음을 확인한다.
   - `.lightbox`와 `#projectModal`이 display none이다.
   - 시나리오 A의 본문 가시성 검사를 통과한다.
   - PDF가 10240바이트를 넘는다.

### 2. `@media print` 수정

- `.reveal`: opacity 1, transform none, visibility visible
- `#heroFeatured`: 인쇄에 포함하고 그리드는 단순하게 바꾼다.
- `.modal`, `.lightbox`, `.theme-toggle`, `.menu-toggle`, `.scroll-hint`, `.navbar`: display none !important
- `body.modal-open`의 스크롤 잠금을 해제한다.
- 기존 `#typed`, `#aboutSummary` 숨김은 유지한다.

## 완료 기준 (AC)

- `npm --prefix tests test && npm --prefix tests run verify-scope`가 모두 통과한다.
