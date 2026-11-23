# Step 12 — print-pdf

- 예상 시간: 15분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~11 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §10
3. index.json에서 step 0~11이 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드에서 `@media print`와 `ensureLightbox`를 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `css/style.css` (`@media print` 블록만)
- `tests/specs/print.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `index.html`, `js/*`, `css/themes.css`
- 기존 tests
- PDF 파서 의존성 추가

## 작업 (TDD)

### 1. `print.spec.js` (desktop-dark/light)

공통 helper: `pdfPageCount(buf) = (buf.toString('latin1').match(/\/Type\s*\/Page\b/g) || []).length`
- `\b` 덕분에 `/Pages`는 세지 않는다.
- helper 자체 검증
  - 합성 `<< /Type /Pages /Count 1 >>`만 있으면 0
  - `<< /Type /Page >>`가 있으면 1
  - `/Type/Page`(공백 없음)도 1

시나리오 A: 새 페이지, print
- 본문과 `#heroFeatured`가 visible이고 opacity 1
- 보이는 `.reveal`에 내용이 있다.
- 인터랙션 요소와 `#projectModal`이 숨겨져 있다.
- `.lightbox`는 count 0이거나, 있으면 display none
- PDF가 10240바이트를 넘고 `pdfPageCount` >= 1

시나리오 B: overlay를 연 상태
- screen에서 `.lightbox`가 1개이고 visible인지 먼저 확인한다.
- print로 전환하면 `.lightbox`와 `#projectModal`이 display none
- 본문 가시성은 A와 같다.
- PDF가 10240바이트를 넘고 `pdfPageCount` >= 1

### 2. `@media print`

- reveal 요소를 보이게 한다.
- `#heroFeatured`를 포함한다.
- overlay와 인터랙션 요소를 숨긴다.
- modal-open 잠금을 해제한다.
- 기존 숨김 규칙은 유지한다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`가 모두 통과한다.
