# Step 6 — section-order-layout

- 예상 시간: 20분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~5 completed

## 공통: 시작 전 필수 확인 (read-first)

1. `README.md`를 읽는다. `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서 두 개를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` — §6 최종 표, §7 예외, §9
3. index.json에서 step 0~5가 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드를 확인한다.
   - `index.html`의 섹션 블록, nav, `.scroll-hint` href
   - `js/main.js`의 스크롤스파이 배열, skillsGrid 렌더링
   - `tests/fixtures/content-exceptions.json`의 final 값
5. `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`는 읽기 전용이다. 문서 변경은 하네스만 한다.
6. main 직접 변경, merge, deploy는 금지다.

## 허용 파일 (exact)

- `index.html`
- `css/style.css`
- `js/main.js`
- `tests/specs/layout.spec.js`

## 수정 금지

- `js/data.js`, `css/themes.css`
- tests/fixtures 전부, 기존 spec
- 섹션 표에 없는 문구 변경

## 작업 (TDD)

### 1. 테스트 먼저 작성

`tests/specs/layout.spec.js`를 작성한다. 6개 project에서 실행한다.

- 순서
  - `main > section`의 id 순서가 hero, career, projects, strengths, about, contact다.
  - nav href 순서가 `#career`, `#projects`, `#strengths`, `#about`, `#contact`이고, 라벨은 Career, Projects, Strengths, About, Contact다.
- 섹션 표 일치
  - 각 섹션의 `.section-kicker`와 `h2.section-title`이 §6 표와 정확히 같다.
  - `#about h3.subsection-title`이 1개이고 텍스트는 기술 스택이다.
  - `#skillsGrid`가 `#about` 안에 있고, skill-group 제목은 h4다.
  - `#contactActions`와 `.contact-card`가 `#contact` 안에 있다.
  - `.scroll-hint`의 href가 `#career`다.
- 레이아웃
  - `scrollWidth <= innerWidth`(가로 스크롤 없음).
  - 열 수를 offsetLeft 고유값 개수로 센다. `#projectGrid`, `#strengthsGrid`, `#heroFeatured` 모두 1280에서 3, 768에서 2, 375에서 1이다.
  - 375에서 모든 `.timeline-highlights li`가 visible이다.
- 스크롤스파이
  - desktop에서 `#about` 링크를 클릭하면 500ms 안에 그 링크가 `.active`가 된다.
- heading
  - level 건너뜀이 없고, h1은 1개다.

### 2. `index.html`

- 섹션 블록을 §6 표 순서대로 옮긴다. 내부 문구는 그대로 둔다.
- kicker 번호를 새 순서대로 다시 매긴다.
- 기존 Stack & Contact 섹션을 분리한다.
  - about 끝에 `h3.subsection-title` 기술 스택과 `#skillsGrid`를 둔다.
  - `section#contact`에는 kicker `05 — Contact`, h2 연락처, `.contact-card`를 둔다.
- nav 순서와 `.scroll-hint` href를 바꾼다.
- `section-alt`는 projects와 about에 붙인다.

### 3. `js/main.js`

- 스크롤스파이 배열을 career, projects, strengths, about, contact 순서로 바꾼다.
- skill-group 제목을 h4로 바꾼다.

### 4. `css/style.css`

- 섹션 세로 여백을 통일한다.
- Career: 데스크톱은 2열(기간 | 내용), 720px 이하는 1열.
- 그리드: 3열, 1024px 이하 2열, 720px 이하 1열.
- `.subsection-title` 스타일을 추가한다.
- 기존 토큰만 쓴다.

## 완료 기준 (AC)

`npm --prefix tests test && npm --prefix tests run verify-scope` → 모두 통과한다.

- content.spec는 kickers와 titles를 final로 판정한다.
- 나머지 정적 본문은 base와 같아야 한다.
