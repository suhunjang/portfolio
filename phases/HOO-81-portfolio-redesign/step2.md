# Step 2 — content-baseline-fixture

- 예상 시간: 20분
- 실행 횟수: fixture 생성 1회, 테스트 1회(웹서버 1회), verify-scope 1회
- 선행 step: 0, 1 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 그것도 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §3, §6, §7 (특히 §7.3 helper 계약)
3. index.json에서 step 0과 1이 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드를 확인한다.
   - data.js의 전역 const
   - index.html 정적 본문 셀렉터: `.nav-link`, `.hero-eyebrow`, `.hero-cta .btn`, `.section-kicker`, `.section-title`, `.section-sub`, `.about-text p`, `.about-points li`, `.about-meta dt`, `.contact-text`, `.footer-note`, `.footer-top`
5. 빌더 read-only 경로
   - `CLAUDE.md`, `docs/**`, `phases/**`
   - `.harness/**`, `.claude/**`, `.codex/**`
   - `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. git과 Harness 운영 명령은 하네스만 실행한다. main 직접 변경, merge, deploy는 금지다.
7. BASE = `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`
8. 공통 실행 계약: npm과 node 명령은 모두 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/scripts/make-fixtures.mjs`
- `tests/fixtures/baseline-data.json`
- `tests/fixtures/baseline-index.html`
- `tests/fixtures/content-exceptions.json`
- `tests/helpers/content.js`
- `tests/specs/content.spec.js`
- `tests/package.json` (`fixtures` script 추가만)

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`
- `tests/.npm-cache/**`
- `tests/test-results/**`
- `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖 전부
- 위 목록 외의 tests 파일

## 작업

1. `make-fixtures.mjs`
   - `git show BASE:js/data.js` 끝에 `;({PROFILE,STATS,CAREER,VIS_ACCENT,PROJECTS,STRENGTHS,SKILLS})`를 붙여 `vm.runInNewContext`로 평가한다.
   - 결과를 JSON 왕복한 뒤 `baseline-data.json`에 2칸 들여쓰기로 저장한다.
   - `git show BASE:index.html`을 `baseline-index.html`에 저장한다.
   - `fixtures` script를 추가한다.
2. `content-exceptions.json`: §7.2 값을 넣는다. 배열은 DOM 순서다.
   - `kickers.base`, `kickers.final`
   - `titles.base`, `titles.final`
   - `featured.indexes`: [1, 5, 7]
   - `subsectionTitleFinal`: 기술 스택
3. `tests/helpers/content.js`: §7.3 계약을 그대로 구현한다.
   - `export function norm(s): string`
     - `String(s).replace(/\s+/g, ' ').trim()`
   - `export async function readLiveData(page): Promise<BaselineData>`
     - `page.evaluate`로 `{ PROFILE, STATS, CAREER, VIS_ACCENT, PROJECTS, STRENGTHS, SKILLS }`를 `JSON.parse(JSON.stringify(...))`해 반환한다.
     - 배열 순서는 원본 그대로다.
   - `export function normalizeFeatured(data): BaselineData`
     - 입력을 변경하지 않는다. `structuredClone(data)` 사본에서 작업한다.
     - `content-exceptions.json`의 `featured.indexes`에 해당하는 index에서 `featured === true`만 `delete`한다.
     - 그 밖의 index에 `featured` 속성이 있거나, 값이 `true`가 아니면 throw한다.
   - `export async function extractStatic(page): Promise<StaticContent>`
     - 모든 문자열에 `norm`을 적용한다.
     - 필드: `title`, `metaDescription`, `navLabels`(기본 `.sort()`), `heroEyebrow`, `ctaLabels`, `kickers`, `sectionTitles`, `sectionSubs`, `aboutParagraphs`(`.about-text p:not([id])`), `aboutPoints`, `aboutMetaTerms`, `contactHeading`, `contactText`, `footerNote`, `footerTop`
     - `navLabels`를 제외한 배열은 DOM 순서다.
   - JSDoc으로 `BaselineData`와 `StaticContent` typedef를 선언한다.
4. `tests/specs/content.spec.js` (6개 project)
   - `normalizeFeatured`
     - 호출 후 입력 객체가 변하지 않았다. 호출 전에 만든 deep copy와 비교한다.
     - 금지 index에 featured가 있는 합성 데이터를 넣으면 throw한다.
   - 데이터: `normalizeFeatured(await readLiveData(page))`가 `baseline-data.json`과 deep-equal이다.
   - featured는 없거나 정확히 1, 5, 7이다.
   - email, phone, social이 빈 문자열이다.
   - 정적 본문
     - baseline-index.html을 `javaScriptEnabled: false` 상태에서 `setContent`로 연 뒤 `extractStatic` 결과를 현재 `/index.html`의 결과와 비교한다.
     - `kickers`와 `sectionTitles`는 base 또는 final 배열과 순서까지 정확히 같아야 한다.
     - final이면 `h3.subsection-title`이 1개다.
     - 나머지 필드는 같아야 한다.
   - 렌더 개수
     - `#heroStats li` 4개
     - timeline 항목 수 = CAREER 길이
     - project-card 13개
     - strengths 6개
     - `.project-title` 배열 = baseline
5. `sh tests/scripts/with-env.sh npm --prefix tests run fixtures`를 실행한다. 생성물은 working tree에 남긴다. 커밋은 하네스가 한다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`가 모두 통과한다.
