# Step 6 — section-order-layout

- 예상 시간: 20분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~5 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침 `CLAUDE.md`(하네스 계약 포함)와 `README.md`를 읽는다. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §6, §7, §8.3(회귀 판정), §9, §11.4
3. index.json에서 step 0~5가 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드에서 다음을 확인한다.
   - 섹션, nav, scroll-hint
   - 스크롤스파이 배열, skillsGrid
   - timeline 구조
   - content-exceptions의 final 값
5. 다음 경로는 read-only다.
   - `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`
   - 하네스 managed 파일: `scripts/**`, `.claude/**`, `.codex/**`, `templates/**`, `harness-manifest.json`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. git add·commit·push는 하네스만 한다. main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 모두 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `index.html`
- `css/style.css`
- `js/main.js`
- `tests/specs/layout.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`
- `tests/.npm-cache/**`
- `tests/test-results/**`
- `tests/playwright-report/**`

## 수정 금지

- `js/data.js`, `css/themes.css`
- fixtures, 기존 spec
- 섹션 표에 없는 문구

## 작업 (TDD)

### 1. `tests/specs/layout.spec.js` 먼저 작성

6개 project에서 실행한다.

- 구조
  - section id 순서: hero, career, projects, strengths, about, contact
  - nav의 href·라벨, kicker, h2가 §6 표와 같다.
  - `#about`에 `h3.subsection-title`이 1개 있다.
  - `#skillsGrid`가 `#about` 안에 있고, 그 안의 제목은 h4다.
  - contact-card와 `#contactActions`가 `#contact` 안에 있다.
  - scroll-hint의 href가 `#career`다.
- 레이아웃 좌표
  - 가로 스크롤이 없다.
  - 그리드 열 수 (offsetLeft 고유값 개수 기준)
    - `#projectGrid`, `#strengthsGrid`, `#heroFeatured`가 1280에서 3, 768에서 2, 375에서 1이다.
  - STATS (2px 오차 허용)
    - 375: left 2종, top 2종
    - 768/1280: left 4종, top 1종
  - Career (첫 `.timeline-item` 기준)
    - 375: `card.top >= period.bottom - 1`
    - 768/1280: `card.left >= period.right - 1`이고 `abs(card.top - period.top) < 24`
  - 375에서 highlights가 모두 visible이다.
- 스크롤스파이 (desktop만)
  - `const link = page.locator(.nav-link[href="#about"])`를 클릭한다.
  - `await expect(link).toHaveClass(/active/)`로 확인한다. 고정 대기는 쓰지 않는다.
- heading 레벨을 건너뛰지 않고, h1은 1개다.

### 2. `index.html`

- §6 순서대로 섹션을 옮긴다. 문구는 유지한다.
- kicker 번호를 새 순서에 맞게 다시 매긴다.
- 기존 Stack &amp; Contact 섹션을 분리한다.
  - about 끝에 `h3.subsection-title`과 `#skillsGrid`를 둔다.
  - `section#contact`를 새로 둔다.
- nav와 scroll-hint를 바꾼다.
- projects와 about에 section-alt를 붙인다.

### 3. `js/main.js`

- 스크롤스파이 배열을 career, projects, strengths, about, contact 순서로 바꾼다.
- skill-group 제목을 h4로 바꾼다.

### 4. `css/style.css`

- 섹션 여백을 통일한다.
- Career: 721px 이상 2열, 720px 이하 1열
- 그리드: 기본 3열, 1024px 이하 2열, 720px 이하 1열
- `.subsection-title` 스타일을 추가한다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`가 모두 통과한다.
- content.spec가 final로 판정된다.
- axe에서 baseline 밖의 새 key와 새 target이 0건이다. 섹션 이동으로 selector가 바뀌어 새 target이 생겼다면 이 step 안에서 해결한다.
