# Step 5 — content-static-baseline

- 예상 시간: 16분
- 실행 횟수: content-static spec 2회, 전체 테스트 1회, verify-scope 1회
- 선행 step: 0~4 completed (`baseline-index.html`과 `content.js`가 있어야 한다)

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §6, §7.2, §7.3 (`StaticContent`, `extractStatic`)
3. index.json에서 step 0~4가 completed인지 확인한다. 아니면 중단한다.
4. index.html 정적 본문 셀렉터를 확인한다: `.nav-link`, `.hero-eyebrow`, `.hero-cta .btn`, `.section-kicker`, `.section-title`, `.section-sub`, `.about-text p`, `.about-points li`, `.about-meta dt`, `.contact-text`, `.footer-note`, `.footer-top`
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/fixtures/content-exceptions.json` (신규)
- `tests/helpers/content.js` (`extractStatic` 추가만)
- `tests/specs/content-static.spec.js` (신규)

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖 전부
- fixture 생성 스크립트, `baseline-data.json`, `baseline-index.html`, `content-data.spec.js`
- `content.js`의 기존 함수

## 작업

1. `content-exceptions.json`에 §7.2 값을 넣는다.
   - `kickers.base`, `kickers.final`
   - `titles.base`, `titles.final`
   - `featured.indexes` [1, 5, 7]
   - `subsectionTitleFinal`
2. `content.js`에 `extractStatic(page): Promise<StaticContent>`를 추가한다.
   - 모든 필드에 norm을 적용한다.
   - `navLabels`만 정렬하고, 나머지는 DOM 순서를 유지한다.
3. `content-static.spec.js` (6개 project, collector 고정 순서)
   - baseline-index.html을 `javaScriptEnabled: false` context에서 `setContent`로 열고 extractStatic을 실행한다. 그 결과를 현재 `/index.html`의 결과와 비교한다.
   - `kickers`와 `sectionTitles`는 base 또는 final과 순서까지 정확히 같아야 한다.
   - final이면 `h3.subsection-title` 기술 스택이 정확히 1개 있어야 한다.
   - 나머지 필드는 BASE와 같아야 한다.
   - 허용 예외 판정 함수에 대한 합성 검증
     - base 배열 → 통과
     - final 배열 → 통과
     - 두 배열이 섞인 경우 → 거부
     - 한 글자라도 다르면 → 거부

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- content-static.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 모두 통과 (전체 회귀는 6개 project 모두에서 돌린다)
