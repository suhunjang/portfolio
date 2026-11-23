# Step 6 — section-order-layout

- 예상 시간: 20분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~5 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(하네스 계약 포함), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md`의 §6, §7, §9, §11.3
3. index.json에서 step 0~5가 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드를 확인한다.
   - 섹션, nav, scroll-hint
   - 스크롤스파이 배열, skillsGrid
   - timeline 구조
   - content-exceptions의 final 값
5. 다음은 읽기만 하고 수정하지 않는다.
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
- fixtures, 기존 spec
- 섹션 표 밖의 문구

## 작업 (TDD)

### 1. `tests/specs/layout.spec.js` 먼저 작성

6개 project에서 실행한다.

- 섹션 순서와 표 일치
  - section id 순서: hero, career, projects, strengths, about, contact
  - nav의 href 순서와 라벨이 §6과 같다.
  - kicker와 h2가 §6 표와 정확히 일치한다.
- 섹션 내부 구성
  - `#about h3.subsection-title` 기술 스택이 1개 있다.
  - `#skillsGrid`가 `#about` 안에 있고, 그 안의 제목은 h4다.
  - contact-card와 `#contactActions`가 `#contact` 안에 있다.
  - scroll-hint의 href가 `#career`다.
- 레이아웃 좌표
  - 가로 스크롤이 없다.
  - 그리드 열 수는 offsetLeft 고유값 개수로 센다. `#projectGrid`, `#strengthsGrid`, `#heroFeatured` 모두 1280에서 3, 768에서 2, 375에서 1이다.
  - STATS
    - 375: left 고유값 2종, top 고유값 2종
    - 768·1280: left 4종, top 1종 (오차 2px 허용)
  - Career (첫 `.timeline-item` 기준)
    - 375: `card.top >= period.bottom - 1`
    - 768·1280: `card.left >= period.right - 1`이고 `abs(card.top - period.top) < 24`
  - 375에서 timeline highlights가 모두 visible이다.
- 스크롤스파이 (desktop만)
  - `const link = page.locator(.nav-link[href="#about"])`를 클릭한다.
  - `await expect(link).toHaveClass(/active/)` 재시도 assertion으로 확인한다.
  - 고정 대기는 쓰지 않는다.
- heading 레벨을 건너뛰지 않고, h1은 1개다.

### 2. `index.html`

- §6 순서대로 섹션을 옮긴다. 문구는 유지한다.
- kicker 번호를 다시 매긴다.
- Stack &amp; Contact 섹션을 둘로 나눈다.
  - about 끝에 `h3.subsection-title`과 `#skillsGrid`를 둔다.
  - `section#contact`에 kicker `05 — Contact`, h2 연락처, contact-card를 둔다.
- nav와 scroll-hint를 바꾼다.
- projects와 about에 section-alt를 적용한다.

### 3. `js/main.js`

- 스크롤스파이 배열: career, projects, strengths, about, contact
- skill-group 제목을 h4로 바꾼다.

### 4. `css/style.css`

- 섹션 여백을 통일한다.
- Career: 721px 이상은 2열, 720px 이하는 1열
- 그리드: 3열, 1024px 이하 2열, 720px 이하 1열
- `.subsection-title`

## 완료 기준 (AC)

- `npm --prefix tests test && npm --prefix tests run verify-scope`가 모두 통과한다.
- content.spec가 final로 판정된다.
