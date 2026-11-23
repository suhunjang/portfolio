# 포트폴리오 레이아웃·구조 리디자인 설계 (HOO-81)

- 날짜: 2026-11-23
- 브랜치: `feat/HOO-81/portfolio-redesign`, base `main`
- 기준 commit(BASE): `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`
- 선행 시각 설계(적용 완료, 계속 유효): `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
- 합의
  - Q1: Discord 1574196542901059632
  - Q2: 1574197289084387379
  - Q3~Q5: 1574197696334405756 (추천안 일괄 확정)
- 리뷰 반영
  - 1차 Astra review `1432c5274b33`: 12개 보완, 승인 1574220980048634010
  - 2차 Astra review `570513f95a2f` (record SHA256 570513f95a2f38bd…, reviewed plan commit 3b424823): 7건
- 사용자 결정·콘텐츠·비목표는 바뀌지 않았다.

## 1. 의도

2026-07-29 작업에서 색·서체·여백을 경영자의 절제 톤으로 정리했다. 그때 레이아웃 구조는 범위 밖이었다.

이번 작업은 그 톤을 유지한 채 구조를 다시 짠다. 채용·영입 의사결정자(임원 채용 담당자, 헤드헌터, 대표)가 30초 안에 다음 세 가지를 파악하게 하는 것이 목표다.
1. COO·CTO 포지셔닝
2. 핵심 지표
3. 대표 프로젝트라는 근거

## 2. 목표 / 비목표 / 실패 조건

### 목표
- 첫 화면에 이름, tagline, 핵심 지표(STATS 4개), 대표 프로젝트 3개를 담는다.
- 섹션을 근거 우선 순서로 재배치한다.
- 섹션 리듬, 카드, 타임라인, 모바일 배치를 재구성한다.
- 기존 기능과 콘텐츠 보존을 자동 테스트와 범위 검사로 증명한다.

### 비목표
- 색·서체 재설계
- 사이트 빌드 도구 도입
- 신규 기능
- 배포, merge, main 직접 변경

### 실패 조건 (기술적으로 동작해도 실패로 본다)
- 콘텐츠 문구·수치·경력 사실을 바꾸거나 창작한다(§7 예외 제외).
- 비어 있는 email·phone·social을 채운다.
- 기존 기능이 회귀한다.
- axe serious/critical 위반이 남는다.
- 그라데이션·글로우 같은 장식이 추가된다.

## 3. 현재 코드 사실 (read-first 대상)

### 저장소 지침
- BASE에는 `README.md`만 있다.
- 현재 checkout에는 하네스가 설치한 `CLAUDE.md`(하네스 계약 블록)와 하네스 managed 파일이 있다.
- 빌더는 `CLAUDE.md`를 반드시 읽고 따른다. git checkout·add·commit은 하네스만 하고, managed 파일은 직접 수정하지 않는다.

### 데이터 (`js/data.js`)
- 전역 const: `PROFILE`, `STATS`(4), `CAREER`, `VIS_ACCENT`, `makeVisual`, `PROJECTS`(13, 전부 `detail` 있음), `STRENGTHS`(6), `SKILLS`
- `PROFILE.tagline`은 BASE에서 렌더링되지 않는다.
- email·phone·social.*은 빈 문자열이다.
- 대표 원본 index: Motion AD=1, VigoRight (의료 AI/VR)=5, Lost Energy Intel=7

### 렌더링 (`js/main.js`)
- `setText(id, value)`로 텍스트를 채운다.
- data 렌더 대상
  - `#heroStats`, `#strengthsGrid`
  - `#timeline` (`.timeline-item` > `.timeline-period` + `.timeline-card`)
  - `#projectGrid`, `#skillsGrid`, `#contactActions`
- 프로젝트 카드: `article.project-card.has-detail[data-project=idx][tabindex=0][role=button]`

### 모달
- `openProjectModal(idx)`는 `lastFocused = document.activeElement`를 저장한 뒤 닫기 버튼에 포커스한다.
- 열기: `#projectGrid` click 위임(`[data-project]`)과 keydown 위임(Enter/Space)
- 닫기: `[data-modal-close]`(`.modal-backdrop`, `.modal-close`) click, document Esc. Esc는 lightbox가 열려 있으면 lightbox를 먼저 닫는다.
- `closeProjectModal()` 순서: lightbox 닫기 → 모달 숨김 → `lastFocused` 복귀

### lightbox
- `ensureLightbox()`는 최초 호출 때만 body에 `.lightbox`를 만든다. 새 페이지에는 `.lightbox`가 존재하지 않는다.
- `openLightbox(btn)` / `closeLightbox()`: 닫을 때 opener로 포커스를 복귀한다.
- lightbox에는 Tab을 닫기 버튼에 고정하는 리스너가 있다. 모달에는 포커스 트랩이 없다.

### 기타
- 스크롤스파이: id 배열(about, strengths, career, projects, contact) 하드코딩 + IntersectionObserver
- reveal: IntersectionObserver로 `.in`을 붙인다. reduced-motion이면 즉시 붙인다.
- typing: `runTyping`. reduced-motion이면 `roles[0]`로 고정한다.
- 테마: localStorage `THEME_KEY`. 저장값이 없으면 시스템 설정을 따른다.
- 메뉴: `#menuToggle`, `#navLinks.open`, `aria-expanded`
- 인쇄: `css/style.css`의 `@media print`
- Google Fonts의 Space Grotesk 링크는 제거 금지다. data.js SVG가 이 서체를 하드코딩한다.

## 4. 접근 방식

| 안 | 내용 | 판단 |
|---|---|---|
| A (선택) | 절제 톤 유지 + 레이아웃·구조 재구성 | Q1에서 선택 |
| B | 시각 방향 전면 교체 | 선행 작업을 되돌림 |
| C | 마감만 다듬기 | 체감 변화 부족 |

## 5. 첫 화면과 대표 프로젝트 (Q2, Q3)

### 히어로 DOM 순서
1. `.hero-eyebrow` (비중 축소)
2. `h1#heroName`
3. `p.hero-tagline#heroTagline` (신규, `setText`로 `PROFILE.tagline` 노출)
4. `h2.hero-role` (`#typed`, 보조 크기)
5. `#heroSummary`
6. `.hero-cta`: `.btn-primary` 프로젝트 보기, `.btn-ghost` 연락하기
7. `ul#heroStats`
8. `div#heroFeatured`

### 함수 계약

`renderFeaturedProjects(): void`
- `PROJECTS`를 원본 순서로 돌며 `featured === true`인 항목을 렌더링한다.
- 카드 마크업: `<button type=button class=featured-card data-featured-card data-project={원본 idx}>`
  - 안에 `h3.featured-title`(`p.title`), `p.featured-blurb`(`p.blurb`)를 둔다.
- 새 문자열을 하드코딩하지 않는다.
- 호출 위치: 그리드 렌더링 직후, 모달 리스너 등록 전

`openProjectModal(projectIndex, triggerElement = document.activeElement): void`
- `lastFocused = triggerElement`
- projectGrid 호출부는 `openProjectModal(idx, card)`로 바꾼다.
- `#heroFeatured`에도 click 위임을 둔다. 네이티브 button이므로 Enter·Space도 click으로 처리된다.

`closeProjectModal(): void`
- 버튼·backdrop·Esc 모든 경로에서 `lastFocused`로 포커스를 복귀한다.

### data.js 변경
- index 1, 5, 7 객체의 `title:` 바로 다음 줄에 `featured: true,`를 넣는다. 총 3줄이다.
- 그 밖의 data.js 변경은 금지다.

### 측정 (1280×800, scrollY=0)
- `#heroName`, `#heroTagline`, `#heroStats`: 각각 y >= 0, bottom <= 800
- `.featured-title` 3개: 각각 bottom <= 1200

## 6. 섹션 구조 (Q4) — 최종 표

| 순서 | section id | class | kicker | heading |
|---|---|---|---|---|
| 1 | hero | hero | 없음 | h1 `#heroName` |
| 2 | career | section | `01 — Career` | h2 경력 &amp; 창업 |
| 3 | projects | section section-alt | `02 — Projects` | h2 프로젝트 &amp; 제품 |
| 4 | strengths | section | `03 — Strengths` | h2 업무상 강점 (section-sub 유지) |
| 5 | about | section section-alt | `04 — About` | h2 소개 |
| 6 | contact | section | `05 — Contact` | h2 연락처 |

### 섹션 세부
- about: 본문 다음에 `h3.subsection-title` 기술 스택과 `#skillsGrid`를 둔다. skill-group 제목은 h4로 바꾼다.
- contact: `.contact-card`를 둔다. h3 함께 만들어요와 문구는 유지한다.

### 탐색
- nav 순서: Career, Projects, Strengths, About, Contact (라벨 유지)
- 스크롤스파이 배열: career, projects, strengths, about, contact
- `.scroll-hint` href: `#career`

## 7. 콘텐츠 보존과 예외

기준은 두 가지다.
- BASE `js/data.js`를 평가한 JSON 전체
- BASE `index.html`의 정적 본문

허용되는 차이는 아래뿐이다.

1. index 1, 5, 7의 `featured: true`
2. `.section-kicker` 집합: 아래 둘 중 정확히 하나와 같아야 한다.
   - BASE: 01 — About, 02 — Strengths, 03 — Career, 04 — Projects, 05 — Stack &amp; Contact
   - FINAL: 01 — Career, 02 — Projects, 03 — Strengths, 04 — About, 05 — Contact
3. `.section-title` 집합: 아래 둘 중 하나와 같아야 한다.
   - BASE: 소개, 업무상 강점, 경력 &amp; 창업, 프로젝트 &amp; 제품, 기술 스택 &amp; 연락처
   - FINAL: 경력 &amp; 창업, 프로젝트 &amp; 제품, 업무상 강점, 소개, 연락처
   - FINAL이면 `h3.subsection-title` 기술 스택이 정확히 1개 있어야 한다.
4. nav와 섹션의 순서. 라벨 집합은 같아야 한다.
5. skill-group 제목의 heading level
6. 접근성 해소 step(§8.3)에서 axe 위반 대상 요소에 한정한 속성 변경: aria-*, role, alt, lang, tabindex, for. 텍스트는 바꾸지 않는다.

그 밖의 정적 본문은 BASE와 같아야 한다.
- title, meta description
- nav 라벨, hero-eyebrow, CTA 라벨, section-sub
- about 정적 p·points·meta dt
- contact h3·p, footer

## 8. 접근성

### 8.1 axe
- 기준: wcag2a, wcag2aa의 serious/critical 위반 0건
- 대상
  - 6개 조합의 페이지
  - 열린 모달 × dark/light
  - 열린 lightbox × dark/light

### 8.2 포커스 트랩 (step 7)

함수 계약: `trapFocus(container: HTMLElement, options?: { returnFocusTo?: HTMLElement }): () => void`
- 모듈 trap 스택에 push한다.
- 최상위 trap만 Tab/Shift+Tab 순환을 처리한다. 그 아래 trap은 일시정지 상태다.
- 반환되는 `release()`
  - 스택에서 제거한다.
  - `returnFocusTo`로 포커스를 옮긴다.
  - 직전 trap을 재개한다.
  - 중복 호출은 무시한다.

적용
- 모달: 열 때 push(returnFocusTo = trigger), 닫을 때 release
- lightbox: 열 때 push(returnFocusTo = `.shot-zoom`). 이때 모달 trap은 일시정지된다.
  - 닫으면 이미지 트리거로 포커스가 돌아가고 모달 trap이 재개된다.
- 기존 lightbox Tab 고정 리스너는 제거한다.

그 밖에
- `:focus-visible` outline을 유지한다.
- h1은 1개, heading level 건너뜀은 없어야 한다.

### 8.3 axe 기준선과 해소 (step 4 → step 8)

step 4는 BASE의 위반을 `tests/fixtures/axe-baseline.json`에 기록한다. 항목 필드:
- `key`: `{scenario}:{project}:{ruleId}`
- `scenario`, `project`, `ruleId`, `impact`
- `targets`: axe node target selector 배열
- `fixKind`: css-token / css-rule / js-render / static-markup / text-change
- `fixFiles`: index.html, css/style.css, css/themes.css, js/main.js 중 일부. text-change이면 빈 배열

분류 규칙
- color-contrast
  - 색이 `var(--토큰)`에서 오면 css-token → `css/themes.css`
  - 아니면 css-rule → `css/style.css`
- 대상이 JS 렌더 영역 안에 있으면 js-render → `js/main.js`
  - JS 렌더 영역: `#heroStats`, `#heroFeatured`, `#timeline`, `#projectGrid`, `#strengthsGrid`, `#skillsGrid`, `#contactActions`, `#modalBody`, `.lightbox`
- `index.html` 정적 요소의 속성 문제는 static-markup → `index.html`
- 문구를 바꿔야만 해결되면 text-change

step 4~7의 axe.spec
- fixture에 없는 key가 나오면 실패한다.
- fixture에 있지만 사라진 key는 허용한다.

step 8 규칙
- 허용 소스: 시작 시점 fixture `fixFiles`의 합집합 + `tests/fixtures/axe-baseline.json`
- `index.html`은 대상 요소에 대한 §7-6 속성 변경만 허용한다. 요소 추가·삭제·이동과 텍스트 변경은 금지다.
- text-change 항목이 있거나 구조 변경이 필요하면 중단하고 보고한다. 하네스가 담당 구현 step(5 또는 6)을 재개한다.
- 해소가 끝나면 fixture는 `[]`이다.

## 9. 반응형

| 대상 | 375 | 768 | 1280 |
|---|---|---|---|
| `#heroStats` | 2×2 (left 2종, top 2종) | 4열 1행 | 4열 1행 |
| `#heroFeatured` | 1열 | 2열 | 3열 |
| `#projectGrid` | 1열 | 2열 | 3열 |
| `#strengthsGrid` | 1열 | 2열 | 3열 |
| Career `.timeline-item` | 세로 (card.top >= period.bottom - 1) | 가로 (card.left >= period.right - 1, top 차이 < 24px) | 가로 |

- Career는 720px 이하에서 1열이다. highlights는 항상 펼친다.
- 가로 스크롤은 없어야 한다.

## 10. 인쇄와 PDF

공통 검사
- 히어로, 대표 카드, 본문 섹션: visibility visible, opacity 1
- 표시되는 `.reveal`: 내용이 비어 있지 않아야 한다.
- `.theme-toggle`, `.menu-toggle`, `.scroll-hint`, `#projectModal`: display none

시나리오
- A (새 페이지, 스크롤 없음): `.lightbox`가 없거나, 있으면 display none
- B
  1. Motion-O 모달과 lightbox를 실제로 연다.
  2. screen에서 `.lightbox`가 존재하고 보이는지 먼저 확인한다.
  3. print로 전환해 `.lightbox`와 `#projectModal`이 display none인지 확인한다.

PDF는 10KB를 넘고 1페이지 이상이어야 한다.

## 11. 검증 체계 (Q5)

### 11.1 tracked source와 runtime 경로 분리

테스트 도구는 `tests/` 안에만 둔다. 루트 package.json은 금지다.

tracked source 허용 — 사이트
- `index.html`, `css/style.css`, `css/themes.css`, `js/main.js`, `js/data.js`

tracked source 허용 — tests
- `tests/package.json`, `tests/package-lock.json`, `tests/.gitignore`, `tests/playwright.config.js`
- `tests/helpers/**`, `tests/specs/**`, `tests/fixtures/**`, `tests/scripts/**`

runtime 쓰기 경로 (추적 금지)
- 설치, step 0: `tests/node_modules/**`, `tests/.npm-cache/**`, `tests/.pw-browsers/**`
- 실행, 모든 step: `tests/.tmp/**`, `tests/test-results/**`, `tests/playwright-report/**`
- step 10: `tests/screenshots/**`

`tests/.gitignore`는 위 runtime 디렉터리 7개만 담는 명시적 허용 파일이다. 내용은 정확히 다음 7줄이다.
- `node_modules/`
- `.npm-cache/`
- `.pw-browsers/`
- `.tmp/`
- `test-results/`
- `playwright-report/`
- `screenshots/`

### 11.2 tests/package.json

- devDependencies: `@playwright/test`, `@axe-core/playwright`
- scripts
  - `test`: `mkdir -p .tmp && TMPDIR=$PWD/.tmp PLAYWRIGHT_BROWSERS_PATH=./.pw-browsers playwright test`
  - `browsers:install`: `mkdir -p .tmp && TMPDIR=$PWD/.tmp PLAYWRIGHT_BROWSERS_PATH=./.pw-browsers playwright install chromium`
  - `verify-scope`: `node scripts/verify-scope.mjs`
  - `verify-scope:selftest`: `node scripts/verify-scope.mjs --self-test`
  - `fixtures`: `node scripts/make-fixtures.mjs`
- 설치: `npm --prefix tests ci --cache tests/.npm-cache` (lock이 없을 때는 install)

### 11.3 Playwright

- webServer: `python3 -m http.server 4173 --bind 127.0.0.1`, cwd는 저장소 루트, reuseExistingServer true
- reporter: list (html 리포트는 만들지 않는다)
- projects 6개: {mobile 375×812, tablet 768×1024, desktop 1280×800} × {dark, light}
  - 이름 형식은 `mobile-dark`. 각 project에 `colorScheme`과 `metadata.theme`을 지정한다.
- 테마 fixture `tests/helpers/theme.js`
  - `addInitScript`는 `localStorage.getItem(THEME_KEY) === null`일 때만 project 테마를 넣는다.
  - 따라서 테마를 바꾼 뒤 reload해도 바꾼 값이 유지된다.
- 최초 방문 검사 `first-visit.spec.js`
  - 위 fixture를 쓰지 않는다. `@playwright/test`의 기본 test를 import한다.
  - storage 없는 별도 `browser.newContext({ colorScheme })`에서 light와 dark를 각각 확인한다.
- 콘솔
  - pageerror 0건
  - Google Fonts 도메인 외 console.error 0건

### 11.4 범위 검사 `tests/scripts/verify-scope.mjs`

BASE 대비 세 층을 각각 독립적으로 검사한다.
- committed: `git diff --name-only BASE HEAD`
- index: `git diff --cached --name-only BASE`
- working tree: `git diff --name-only BASE` + `git ls-files --others --exclude-standard`

경로 규칙
- 빌더 허용 경로: §11.1 tracked source. 세 층 모두 허용한다.
- 하네스 소유 경로
  - 목록: `CLAUDE.md`, `harness-manifest.json`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`, `scripts/**`, `.claude/**`, `.codex/**`, `templates/**`, 이 설계 문서
  - committed 층에서는 면제한다.
  - index와 HEAD의 차이, working tree와 HEAD의 차이, untracked로 나타나면 위반이다. 빌더의 미커밋 수정을 잡기 위한 규칙이다.
- 하네스 런타임 경로: `.harness/**`, `.venv/**`, `phases/HOO-81-portfolio-redesign/**`. 모든 층에서 면제한다.
- 그 밖의 경로는 모든 층에서 위반이다.
  - 예: 다른 `docs/**`, `README.md`, `assets/**`, `.nojekyll`, `AGENTS.md`, 루트 `package.json`, 그 밖의 `css/`·`js/` 파일, tests 허용 목록 밖 파일

내용 규칙
- `js/data.js`
  - BASE→HEAD, BASE→index, BASE→working tree, index→working tree 네 구간의 diff(unified=0)를 각각 검사한다.
  - 삭제 줄은 0개여야 한다.
  - 추가 줄은 모두 trim했을 때 `featured: true,`여야 하고, 3개 이하여야 한다.
  - `--final`이면 BASE→working tree와 BASE→index의 추가 줄이 정확히 3개여야 한다.
- `index.html`: HEAD blob, index blob(`git show :index.html`), working 파일 각각의 fonts.googleapis.com 링크에 `Space+Grotesk`가 있어야 한다.
- `tests/.gitignore`: index blob과 working 파일 각각에서 공백·주석 줄을 뺀 줄 집합이 §11.1의 7줄과 정확히 같아야 한다.
- runtime 경로가 `git ls-files`(index)나 `git ls-tree -r --name-only HEAD`에 추적되어 있으면 위반이다.
- 루트 package.json이 존재하면 위반이다.

출력
- 위반이 있으면 목록을 출력하고 exit 1로 끝낸다.

자기 검증
- 순수 함수 `evaluateScope(input) => string[]`를 export한다.
- `--self-test`는 12개 이상의 사례를 검증한다. 다음 우회 사례를 반드시 포함한다.
  - data.js 금지 변경을 stage한 뒤 working tree만 되돌린 경우
  - Space Grotesk 제거를 stage한 뒤 working tree만 되돌린 경우
  - README 변경을 stage한 뒤 working tree만 되돌린 경우

### 11.5 통합 AC

- step 1 이후 모든 step: `npm --prefix tests test && npm --prefix tests run verify-scope`
- 최종 step: `--final`

## 12. 변경 허용 경로와 git 경계

- index.json allowedPaths: `index.html`, `css/style.css`, `css/themes.css`, `js/main.js`, `js/data.js`, `tests/`
  - 하네스 설치 파일과 정책 파일은 넣지 않는다.
- step마다 tracked source 허용 파일과 runtime 쓰기 경로를 exact로 명시한다.
- `css/themes.css`와 `index.html` 속성 변경은 step 8에서 fixture가 지정한 경우에만 허용한다.
  - `index.html` 구조 변경은 step 5·6에서만 한다.
- 최종 step 10은 tests 보조 코드만 수정할 수 있다.
- git checkout·add·commit·push는 하네스만 한다. 빌더는 working tree만 수정한다.
- 빌더는 `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, 하네스 managed 파일을 수정하지 않는다.

## 13. Step 목록 (각 20분 이하)

| # | name | 예상 시간 |
|---|---|---|
| 0 | tests-env-setup | 12분 |
| 1 | scope-verifier | 20분 |
| 2 | content-baseline-fixture | 18분 |
| 3 | interaction-regression | 18분 |
| 4 | axe-baseline | 15분 |
| 5 | hero-featured | 20분 |
| 6 | section-order-layout | 20분 |
| 7 | focus-trap | 18분 |
| 8 | axe-remediation | 15분 |
| 9 | print-pdf | 15분 |
| 10 | final-verification | 12분 |

## 14. 빌더 재량

- 세부 시각 표현. 선행 문서의 토큰과 accent 제한은 지킨다.
- CSS 클래스 구조. 명시된 id, data 속성, 클래스는 유지한다.
- 테스트 helper를 나누는 방식
