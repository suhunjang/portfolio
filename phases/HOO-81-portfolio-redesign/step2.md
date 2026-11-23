# Step 2 — content-baseline-fixture

- 예상 시간: 18분
- 실행 횟수: fixture 생성 1회, 테스트 1회(웹서버 1회), verify-scope 1회
- 선행 step: 0, 1 completed

## 공통: 시작 전 필수 확인 (read-first)

1. `README.md`를 읽는다. `CLAUDE.md` 또는 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서 두 개를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md`: §3, §6, §7
3. index.json에서 step 0과 1이 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드에서 다음을 확인한다.
   - `js/data.js`의 전역 const 목록
   - `index.html`의 정적 본문 위치: nav, hero-eyebrow, CTA, section-kicker, section-title, section-sub, about, contact, footer
5. `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`는 읽기 전용이다. 문서 변경은 하네스만 한다.
6. 기준 commit(BASE)은 `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`다.
7. main 직접 변경, merge, deploy는 금지다.

## 허용 파일 (exact)

- `tests/scripts/make-fixtures.mjs`
- `tests/fixtures/baseline-data.json`
- `tests/fixtures/baseline-index.html`
- `tests/fixtures/content-exceptions.json`
- `tests/helpers/content.js`
- `tests/specs/content.spec.js`
- `tests/package.json`: `fixtures` script 추가만 허용

## 수정 금지

- `tests/` 밖의 모든 파일
- 위 목록에 없는 기존 tests 파일

## 작업

1. `tests/scripts/make-fixtures.mjs`를 작성한다. Node 표준 라이브러리만 쓴다.
   - `git show BASE:js/data.js`의 소스 끝에 `;({PROFILE,STATS,CAREER,VIS_ACCENT,PROJECTS,STRENGTHS,SKILLS})`를 붙여 `vm.runInNewContext`로 평가한다.
   - 평가 결과를 들여쓰기 2칸 JSON으로 `tests/fixtures/baseline-data.json`에 저장한다.
   - `git show BASE:index.html`의 내용을 `tests/fixtures/baseline-index.html`에 저장한다.
   - BASE 값은 위 commit으로 고정한다.
   - `tests/package.json` scripts에 `fixtures`: `node scripts/make-fixtures.mjs`를 추가한다.
2. `tests/fixtures/content-exceptions.json`에 설계 §7의 값을 그대로 기록한다.
   - `kickers.base`, `kickers.final`
   - `titles.base`, `titles.final`
   - `featured.indexes`: [1, 5, 7]
   - `subsectionTitleFinal`: 기술 스택
3. `tests/helpers/content.js`에 다음 함수를 만든다.
   - `readLiveData(page)`: `page.evaluate`로 전역 const 값을 JSON으로 직렬화해 반환한다.
   - `normalizeFeatured(data, indexes)`: 지정 index에서 `featured === true`를 제거한다. 다른 index에 featured가 있으면 throw한다.
   - `extractStatic(page)`: 다음 정적 텍스트를 공백 정규화해 반환한다.
     - document.title, meta description
     - `.nav-link` 라벨(정렬)
     - `.hero-eyebrow`, `.hero-cta .btn` 라벨
     - `.section-kicker`, `.section-title` 배열
     - `.section-sub`
     - id가 없는 `.about-text p`, `.about-points li`, `.about-meta dt`
     - `.contact-text h3`, `.contact-text p`
     - `.footer-note`, `.footer-top`
4. `tests/specs/content.spec.js`를 작성한다. 6개 project 모두에서 실행한다.
   - 데이터 검사
     - normalizeFeatured를 적용한 live data가 baseline-data.json과 deep-equal이다.
     - featured는 0개이거나, 정확히 index 1, 5, 7에만 있다.
     - PROFILE.email, phone, social의 모든 값이 빈 문자열이다.
   - 정적 본문 검사
     - baseline-index.html을 `javaScriptEnabled: false` context에서 `page.setContent`로 열어 extractStatic을 실행한다.
     - 현재 `/index.html`에도 extractStatic을 실행해 결과를 비교한다.
     - kickers와 titles는 base 또는 final 중 정확히 하나와 같아야 한다.
     - titles가 final이면 `h3.subsection-title` 기술 스택이 정확히 1개 있어야 한다.
     - nav 라벨은 정렬 기준으로 같아야 한다.
     - 나머지 항목은 모두 같아야 한다.
   - 렌더 수 검사
     - `#heroStats li`가 4개다.
     - `#timeline > li` 개수가 CAREER 길이와 같다.
     - `#projectGrid .project-card`가 13개다.
     - strengths 카드가 6개다.
     - `.project-title` 배열이 baseline PROJECTS의 title 배열과 같다.
5. `npm --prefix tests run fixtures`로 fixture를 생성해 커밋 대상에 포함한다.

## 완료 기준 (AC)

- `npm --prefix tests test && npm --prefix tests run verify-scope` → 모두 통과
- 사이트 코드는 아직 바뀌지 않았으므로 base 상태로 판정된다.
