# Step 6 — section-order-layout

- 예상 시간: 20분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~5 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(하네스 계약 포함), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §6, §7, §9
3. index.json에서 step 0~5가 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드를 확인한다.
   - 섹션 블록, nav, `.scroll-hint`
   - 스크롤스파이 배열, skillsGrid
   - `.timeline-item` / `.timeline-period` / `.timeline-card` 구조
   - content-exceptions의 final 값
5. 다음은 읽기 전용이다.
   - `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`
   - 하네스 managed 파일: `scripts/**`, `.claude/**`, `.codex/**`, `templates/**`, `harness-manifest.json`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. git add·commit·push는 하네스만 한다. main 직접 변경, merge, deploy는 금지다.

## tracked source 허용 파일 (exact)

- `index.html`
- `css/style.css`
- `js/main.js`
- `tests/specs/layout.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`
- `tests/test-results/**`
- `tests/playwright-report/**`

## 수정 금지

- `js/data.js`, `css/themes.css`
- fixtures 전부, 기존 spec
- 섹션 표 밖의 문구

## 작업 (TDD)

### 1. `tests/specs/layout.spec.js`를 먼저 작성한다

6개 project에서 실행한다.

- 순서
  - `main > section` id 순서: hero, career, projects, strengths, about, contact
  - nav href 순서: `#career`, `#projects`, `#strengths`, `#about`, `#contact`. 라벨은 Career, Projects, Strengths, About, Contact
- 섹션 표
  - 각 섹션의 kicker와 h2가 §6 표와 정확히 같다.
  - `#about h3.subsection-title`(기술 스택)이 1개다.
  - `#skillsGrid`가 `#about` 안에 있고, 그 안의 제목은 h4다.
  - `.contact-card`와 `#contactActions`가 `#contact` 안에 있다.
  - `.scroll-hint`의 href가 `#career`다.
- 레이아웃 좌표
  - `scrollWidth <= innerWidth`
  - offsetLeft 고유값으로 센 열 수: `#projectGrid`, `#strengthsGrid`, `#heroFeatured` 모두 1280=3, 768=2, 375=1
  - STATS (`#heroStats li`의 rect)
    - 375: left 고유값 2개, top 고유값 2개 (2×2)
    - 768·1280: left 고유값 4개, top 고유값 1개 (오차 2px 허용)
  - Career (첫 `.timeline-item`의 period·card rect)
    - 375: `card.top >= period.bottom - 1` (세로 배치)
    - 768·1280: `card.left >= period.right - 1`이고 `abs(card.top - period.top) < 24` (가로 배치)
  - 375에서 모든 `.timeline-highlights li`가 visible이다.
- 스크롤스파이: desktop에서 nav의 `#about`을 클릭하면 `.active`가 된다.
- heading: 레벨 건너뜀이 없고 h1은 1개다.

### 2. `index.html`

- §6 표 순서대로 섹션을 옮긴다. 문구는 그대로 둔다.
- kicker 번호를 다시 매긴다.
- Stack &amp; Contact 섹션을 분리한다.
  - about 끝에 `h3.subsection-title` 기술 스택과 `#skillsGrid`를 둔다.
  - `section#contact`에는 kicker `05 — Contact`, h2 연락처, `.contact-card`를 둔다.
- nav 순서와 `.scroll-hint` href를 바꾼다.
- projects와 about에 `section-alt`를 붙인다.

### 3. `js/main.js`

- 스크롤스파이 배열: career, projects, strengths, about, contact
- skill-group 제목을 h4로 바꾼다.

### 4. `css/style.css`

- 섹션 여백을 통일한다.
- Career는 721px 이상에서 2열(기간 | 내용), 720px 이하에서 1열로 둔다.
- 그리드는 3열, 1024px 이하 2열, 720px 이하 1열로 둔다.
- `.subsection-title` 스타일을 추가한다.

## 완료 기준 (AC)

- `npm --prefix tests test && npm --prefix tests run verify-scope`가 모두 통과한다.
- content.spec가 final로 판정된다.
