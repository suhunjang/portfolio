# 포트폴리오 레이아웃·구조 리디자인 설계 (HOO-81)

- 날짜: 2026-11-23
- 브랜치: `feat/HOO-81/portfolio-redesign` (base `main`)
- 기준 commit(BASE): `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`
- 선행 시각 설계: `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md` (적용 완료, 계속 유효)
- 합의 메시지
  - Q1: Discord 1574196542901059632
  - Q2: 1574197289084387379
  - Q3~Q5: 1574197696334405756 (추천안 일괄 확정)
- 리뷰 반영 이력
  - 1차 Astra review `1432c5274b33`: 12개 보완 (승인 1574220980048634010)
  - 2차 `570513f95a2f`: 7건
  - 3차 `9e8c69018dc0`: 4건
  - 4차 `8014bc034fb4` (plan commit 984c10af): 3건
  - 사용자 결정, 콘텐츠, 비목표는 바뀌지 않았다.

## 1. 의도

2026-07-29 작업에서 색·서체·여백을 경영자의 절제 톤으로 정리했다. 그때 레이아웃 구조는 범위 밖이었다.

이번 작업은 그 톤을 유지하면서 구조를 다시 짠다. 목표는 채용·영입 의사결정자(임원 채용 담당자, 헤드헌터, 대표)가 30초 안에 다음 세 가지를 파악하는 것이다.
1. COO·CTO 포지셔닝
2. 핵심 지표
3. 대표 프로젝트라는 근거

## 2. 목표 / 비목표 / 실패 조건

### 목표
- 1280×800 초기 viewport에 이름, tagline, 핵심 지표(STATS 4개), 대표 프로젝트 3개의 제목이 모두 보이게 한다.
- 섹션을 근거 우선 순서로 재배치한다.
- 섹션 리듬, 카드, 타임라인, 모바일 배치를 재구성한다.
- 기존 기능과 콘텐츠가 보존됨을 자동 테스트와 범위 검사로 증명한다.

### 비목표
- 색·서체 재설계
- 사이트 빌드 도구 도입
- 신규 기능
- 배포, merge, main 직접 변경

### 실패 조건 (기술적으로 동작해도 실패로 본다)
- 콘텐츠 문구·수치·경력 사실을 바꾸거나 새로 만든다. 단 §7의 예외는 허용한다.
- 비어 있는 email·phone·social을 채운다.
- 기존 기능이 회귀한다.
- axe serious/critical 위반이 남는다.
- 그라데이션이나 글로우 같은 장식을 추가한다.

## 3. 현재 코드 사실 (read-first 대상)

### 저장소 지침
- BASE에는 `README.md`만 있다.
- 현재 checkout에는 하네스가 설치한 `CLAUDE.md`(하네스 계약 블록)와 하네스 managed 파일이 있다.
- 빌더는 `CLAUDE.md`를 반드시 읽고 따른다.
  - git checkout·add·commit은 하네스만 한다.
  - managed 파일은 수정하지 않는다.

### 데이터 (`js/data.js`)
- 전역 const: `PROFILE`, `STATS`(4), `CAREER`, `VIS_ACCENT`, `makeVisual`, `PROJECTS`(13개, 전부 `detail` 있음), `STRENGTHS`(6), `SKILLS`
- `PROFILE.tagline`은 BASE에서 렌더링되지 않는다.
- email·phone·social.*은 빈 문자열이다.
- 대표 프로젝트 원본 index: Motion AD=1, VigoRight (의료 AI/VR)=5, Lost Energy Intel=7

### 렌더링 (`js/main.js`)
- `setText(id, value)`로 텍스트를 채운다.
- data로 렌더링하는 영역:
  - `#heroStats`
  - `#strengthsGrid`
  - `#timeline` (`.timeline-item` > `.timeline-period` + `.timeline-card`)
  - `#projectGrid`
  - `#skillsGrid`
  - `#contactActions`
- 프로젝트 카드: `article.project-card.has-detail[data-project=idx][tabindex=0][role=button]`

### 모달
- `openProjectModal(idx)`는 `lastFocused = document.activeElement`를 저장한 뒤 닫기 버튼에 포커스한다.
- 여는 경로: `#projectGrid`의 click 위임과 keydown 위임
- 닫는 경로: `[data-modal-close]` click, document의 Esc
  - Esc는 lightbox가 열려 있으면 lightbox를 먼저 닫는다.
- `closeProjectModal()` 순서: lightbox 닫기 → 모달 숨김 → `lastFocused`로 포커스 복귀

### lightbox
- `ensureLightbox()`가 처음 호출될 때만 `.lightbox`를 만든다. 새 페이지에는 `.lightbox`가 없다.
- `openLightbox(btn)`과 `closeLightbox()`는 닫을 때 opener로 포커스를 돌려준다.
- lightbox에는 Tab을 닫기 버튼에 고정하는 리스너가 있다. 모달에는 포커스 트랩이 없다.

### 기타
- 스크롤스파이: id 배열(about, strengths, career, projects, contact) 하드코딩 + IntersectionObserver(rootMargin -45%/-50%)
- reveal: IntersectionObserver로 `.in`을 붙인다. reduced-motion이면 즉시 붙인다.
- typing: `runTyping`. reduced-motion이면 `roles[0]`을 고정 표시한다.
- 테마: localStorage `THEME_KEY`. 저장값이 없으면 시스템 설정을 따른다.
- 메뉴: `#menuToggle`, `#navLinks.open`, `aria-expanded`
- 인쇄: `css/style.css`의 `@media print`
- Google Fonts의 Space Grotesk 링크는 제거 금지다. data.js의 SVG가 이 서체를 하드코딩한다.

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
3. `p.hero-tagline#heroTagline` (신규. `setText`로 `PROFILE.tagline`을 노출)
4. `h2.hero-role` (`#typed`, 보조 크기)
5. `#heroSummary`
6. `.hero-cta`: `.btn-primary` 프로젝트 보기, `.btn-ghost` 연락하기
7. `ul#heroStats`
8. `div#heroFeatured`

### 함수 계약

`renderFeaturedProjects(): void`
- `PROJECTS`를 원본 순서로 돌며 `featured === true`인 항목만 렌더링한다.
- 카드 마크업: `<button type=button class=featured-card data-featured-card data-project={원본 idx}>`
  - 내부: `h3.featured-title`(`p.title`), `p.featured-blurb`(`p.blurb`)
- 새 문자열을 하드코딩하지 않는다.
- 그리드 렌더링 직후, 모달 리스너 등록 전에 호출한다.

`openProjectModal(projectIndex, triggerElement = document.activeElement): void`
- `lastFocused = triggerElement`로 저장한다.
- projectGrid에서는 `openProjectModal(idx, card)`로 호출한다.
- `#heroFeatured`에도 click 위임을 둔다. 카드가 네이티브 button이므로 Enter·Space도 click으로 처리된다.

`closeProjectModal(): void`
- 버튼, backdrop, Esc 모든 경로에서 `lastFocused`로 포커스를 복귀한다.

### data.js 변경
- index 1, 5, 7 객체에서 `title:` 바로 다음 줄에 `featured: true,`를 넣는다. 총 3줄이다.
- 이 3줄 외의 data.js 변경은 금지한다.

### 첫 화면 측정 (1280×800, scrollY=0)
- 측정 대상: `#heroName`, `#heroTagline`, `#heroStats`, `.featured-title` 3개(각각)
- 각 rect가 y >= 0이고 bottom <= 800이어야 한다.
- 이를 위해 히어로의 세로 여백, 요약 폭, 카드 높이를 조정한다. 콘텐츠는 줄이지 않는다.

## 6. 섹션 구조 (Q4) — 최종 표

| 순서 | section id | class | kicker | heading |
|---|---|---|---|---|
| 1 | hero | hero | 없음 | h1 `#heroName` |
| 2 | career | section | `01 — Career` | h2 경력 &amp; 창업 |
| 3 | projects | section section-alt | `02 — Projects` | h2 프로젝트 &amp; 제품 |
| 4 | strengths | section | `03 — Strengths` | h2 업무상 강점 (section-sub 유지) |
| 5 | about | section section-alt | `04 — About` | h2 소개 |
| 6 | contact | section | `05 — Contact` | h2 연락처 |

### 섹션 내부
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

허용하는 차이는 아래뿐이다.
1. index 1, 5, 7의 `featured: true`
2. `.section-kicker` 집합: 아래 둘 중 정확히 하나와 같아야 한다.
   - BASE: 01 — About, 02 — Strengths, 03 — Career, 04 — Projects, 05 — Stack &amp; Contact
   - FINAL: 01 — Career, 02 — Projects, 03 — Strengths, 04 — About, 05 — Contact
3. `.section-title` 집합: 아래 둘 중 하나와 같아야 한다.
   - BASE: 소개, 업무상 강점, 경력 &amp; 창업, 프로젝트 &amp; 제품, 기술 스택 &amp; 연락처
   - FINAL: 경력 &amp; 창업, 프로젝트 &amp; 제품, 업무상 강점, 소개, 연락처
   - FINAL이면 `h3.subsection-title` 기술 스택이 정확히 1개 있어야 한다.
4. nav와 섹션 순서. 라벨 집합은 같아야 한다.
5. skill-group 제목의 heading level
6. step 8(§8.3)에서 axe 위반 대상 요소에 한정한 aria-*, role, alt, lang, tabindex, for 속성 변경. 텍스트는 바꾸지 않는다.

그 밖의 정적 본문은 BASE와 같아야 한다. 대상:
- title, meta description
- nav 라벨, hero-eyebrow, CTA 라벨, section-sub
- about의 정적 p, points, meta dt
- contact의 h3·p, footer

## 8. 접근성

### 8.1 axe
- 기준: wcag2a·wcag2aa에서 serious/critical 위반 0건
- 검사 범위 10개
  - page: 3 viewport × 2 테마 = 6
  - 모달을 연 상태 × dark/light
  - lightbox를 연 상태 × dark/light

### 8.2 포커스 트랩 (step 7)

함수 계약: `trapFocus(container: HTMLElement, options?: { returnFocusTo?: HTMLElement }): () => void`
- 호출하면 모듈 trap 스택에 push한다.
- 최상위 trap만 Tab/Shift+Tab 순환을 처리한다. 그 아래 trap은 일시정지 상태가 된다.
- 반환되는 `release()`:
  - 스택에서 제거하고, `returnFocusTo`로 포커스를 옮기고, 직전 trap을 재개한다.
  - 중복 호출은 무시한다.

적용
- 모달: 열 때 push(returnFocusTo=trigger), 닫을 때 release
- lightbox: 열 때 push(returnFocusTo=`.shot-zoom`). 이때 모달 trap은 일시정지된다. 닫으면 이미지 트리거로 포커스가 돌아가고 모달 trap이 재개된다.
- 기존 lightbox의 Tab 고정 리스너는 제거한다.

그 밖에
- `:focus-visible` outline을 유지한다.
- h1은 1개, heading level은 건너뛰지 않는다.

### 8.3 axe 기준선과 해소 (step 4 → step 8)

#### 실행 모드

수집 모드 (`AXE_COLLECT=1`)
- step 4에서 최초 기준선을 만들 때만 쓴다.
- 실제 `tests/fixtures/axe-baseline.json`을 로드하지 않는다.
- 실제 fixture의 스키마 검사와 회귀 판정을 건너뛴다. 합성 스키마 검사만 실행한다.
- 각 scenario×project 결과를 기록만 한다.

일반 모드 (기본)
- 실제 fixture를 로드한다.
- 실제 fixture 스키마 검사, target 단위 회귀 판정, 합성 스키마 검사를 모두 실행한다.

#### 수집 절차 (step 4)
1. `tests/.tmp/axe-collected/`를 초기화한다.
2. scenario×project마다 `tests/.tmp/axe-collected/{scenario}-{project}.json`에 따로 기록한다. 위반이 없으면 `[]`를 쓴다.
3. 병합한다. 먼저 파일이 정확히 10개인지 검증하고, 누락이나 여분이 있으면 exit 1로 끝낸다.
   - page × 6 project
   - modal × desktop-dark·desktop-light
   - lightbox × desktop-dark·desktop-light
4. target별로 분류해 fixture를 생성한다.
5. 일반 모드로 실행해 실제 fixture 스키마와 회귀 판정을 통과시킨다.

#### fixture 스키마 (`tests/fixtures/axe-baseline.json`, 배열)
- `key`: `{scenario}:{project}:{ruleId}`
- `scenario`, `project`, `ruleId`, `impact`
- `targets`: axe node target selector 문자열 배열
- `fixes`: target별 배열. 원소는 `{ target, fixKind, fixFiles }`이다.
  - `target`은 `targets`의 원소다.
  - `targets`의 원소마다 fix가 정확히 1개 있다.
  - `fixKind`: css-token, css-rule, js-render, static-markup, text-change 중 하나
  - `fixFiles`: index.html, css/style.css, css/themes.css, js/main.js의 부분집합. text-change이면 빈 배열
- `fixFiles` (항목 수준): `fixes[].fixFiles`의 합집합과 정확히 같아야 한다.

#### target별 분류 규칙
- color-contrast
  - target 색이 `var(--토큰)`에서 오면 css-token(`css/themes.css`)
  - 그렇지 않으면 css-rule(`css/style.css`)
- target이 JS 렌더 영역 안에 있으면 js-render(`js/main.js`)
  - 영역: `#heroStats`, `#heroFeatured`, `#timeline`, `#projectGrid`, `#strengthsGrid`, `#skillsGrid`, `#contactActions`, `#modalBody`, `.lightbox`
- `index.html` 정적 요소의 속성 문제는 static-markup(`index.html`)
- 문구를 바꿔야만 해결되면 text-change
- 한 color-contrast 항목 안에서 target마다 css-token과 css-rule이 섞일 수 있다. 이때 항목 `fixFiles`는 두 파일의 합집합이다.

#### 스키마 검증 (`tests/helpers/axe.js`의 `validateBaseline`)
합성 사례는 모든 모드에서 실행한다.
- 통과해야 하는 사례: 혼합 color-contrast
- 거부해야 하는 사례:
  - 항목 fixFiles가 합집합과 다름
  - target 누락
  - targets에 없는 target
  - text-change인데 fixFiles가 비어 있지 않음
  - 알 수 없는 fixKind

실제 fixture 검사는 일반 모드에서만 실행한다.

#### 회귀 판정 (일반 모드, step 4~7)
- 이번 실행에서 나온 위반마다 다음을 모두 만족해야 한다.
  - key가 fixture에 있다.
  - 그 위반의 각 target이 해당 항목의 `targets`에 있고, 대응하는 `fixes` 원소가 있다.
- 새 key나 새 target이 나오면 실패한다. 그 변경을 도입한 step에서 해결해야 한다.
- fixture에 있지만 이번에 사라진 key나 target은 허용한다.

#### 해소 (step 8)
- 허용 소스: step 시작 시점 fixture 항목들의 `fixFiles` 합집합 + `tests/fixtures/axe-baseline.json`
- target 단위로, 각 fixKind에 맞게 수정한다.
- `index.html`은 대상 요소의 §7-6 속성 변경만 허용한다. 요소 추가·삭제·이동과 텍스트 변경은 금지한다.
- text-change가 있거나 구조 변경이 필요하면 중단하고 보고한다. 하네스가 담당 구현 step(5 또는 6)을 재개한다.
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
- 가로 스크롤이 없어야 한다.

## 10. 인쇄와 PDF

공통 검사
- 히어로, 대표 카드, 본문 섹션: visibility visible, opacity 1
- 표시되는 `.reveal`: 내용이 비어 있지 않아야 한다.
- `.theme-toggle`, `.menu-toggle`, `.scroll-hint`, `#projectModal`: display none

시나리오
- A (새 페이지, 스크롤 없음): `.lightbox`가 없거나, 있으면 display none
- B (오버레이 열림)
  1. Motion-O 모달과 lightbox를 실제로 연다.
  2. screen 미디어에서 `.lightbox`가 존재하고 보이는지 먼저 확인한다.
  3. print로 전환한 뒤 `.lightbox`와 `#projectModal`이 display none인지 확인한다.

PDF: 10KB를 넘고 1페이지 이상이어야 한다.

## 11. 검증 체계 (Q5)

### 11.1 tracked source와 runtime 경로 분리

테스트 도구는 `tests/` 안에만 둔다. 루트 package.json은 금지한다.

tracked source 허용
- 사이트: `index.html`, `css/style.css`, `css/themes.css`, `js/main.js`, `js/data.js`
- tests: `tests/package.json`, `tests/package-lock.json`, `tests/.gitignore`, `tests/playwright.config.js`, `tests/helpers/**`, `tests/specs/**`, `tests/fixtures/**`, `tests/scripts/**`

runtime 쓰기 경로 (추적 금지)
- 설치(step 0): `tests/node_modules/**`, `tests/.npm-cache/**`, `tests/.pw-browsers/**`
- 실행(모든 step): `tests/.tmp/**`(axe 수집 포함), `tests/test-results/**`, `tests/playwright-report/**`
- step 10: `tests/screenshots/**`

`tests/.gitignore`는 runtime 디렉터리 7개만 담는 명시적 허용 파일이다. 내용은 정확히 다음 7줄이다.
- `node_modules/`
- `.npm-cache/`
- `.pw-browsers/`
- `.tmp/`
- `test-results/`
- `playwright-report/`
- `screenshots/`

### 11.2 공통 실행 계약 (`tests/scripts/with-env.sh`)

npm·node·playwright 명령은 모두 이 래퍼를 통해 실행한다. 설치, 테스트, verify-scope, axe CLI, 모든 step의 AC 명령, 하네스 testCommand가 여기에 해당한다.

래퍼는 외부 npm 프로세스가 시작되기 전에 환경을 정한다. package.json script 내부 설정에 의존하지 않는다.

```
#!/bin/sh
set -eu
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
mkdir -p "$REPO_ROOT/tests/.tmp" "$REPO_ROOT/tests/.npm-cache"
export TMPDIR="$REPO_ROOT/tests/.tmp"
export npm_config_cache="$REPO_ROOT/tests/.npm-cache"
export PLAYWRIGHT_BROWSERS_PATH="$REPO_ROOT/tests/.pw-browsers"
cd "$REPO_ROOT"
exec "$@"
```

- 경로는 저장소 루트 기준 절대경로다. `tests/.tmp`와 `tests/.npm-cache`는 설치 전에 만든다.
- npm 로그는 `npm_config_cache/_logs`에 쌓이므로 runtime 경로 밖에 쓰지 않는다.
- 사용법: `sh tests/scripts/with-env.sh <명령...>`
  - 예: `sh tests/scripts/with-env.sh npm --prefix tests test`
- 하네스 testCommand: `sh tests/scripts/with-env.sh npm --prefix tests test`

### 11.3 tests/package.json

- devDependencies: `@playwright/test`, `@axe-core/playwright`
- scripts (환경 변수는 래퍼가 제공한다)
  - `test`: `playwright test`
  - `browsers:install`: `playwright install chromium`
  - `verify-scope`: `node scripts/verify-scope.mjs`
  - `verify-scope:selftest`: `node scripts/verify-scope.mjs --self-test`
  - `fixtures`: `node scripts/make-fixtures.mjs`
- 설치: `sh tests/scripts/with-env.sh npm --prefix tests ci` (lock이 없으면 `install`)

### 11.4 Playwright

- webServer: `python3 -m http.server 4173 --bind 127.0.0.1`, cwd는 저장소 루트, reuseExistingServer true
- reporter: list
- projects 6개: {mobile 375×812, tablet 768×1024, desktop 1280×800} × {dark, light}
  - 이름 형식: `mobile-dark`
  - 각 project에 `colorScheme`과 `metadata.theme`을 지정한다.
- 테마 fixture (`tests/helpers/theme.js`)
  - `addInitScript`는 `localStorage.getItem(THEME_KEY) === null`일 때만 project 테마를 주입한다.
  - 따라서 테마를 바꾼 뒤 reload해도 바꾼 값이 유지된다.
- 최초 방문 검사 (`first-visit.spec.js`)
  - fixture를 쓰지 않고 `@playwright/test`의 기본 test를 import한다.
  - storage가 없는 별도 `browser.newContext({ colorScheme })`에서 light와 dark를 각각 확인한다.
- 스크롤스파이 검사
  - `page.locator(.nav-link[href=#id])`를 클릭한 뒤 `await expect(locator).toHaveClass(/active/)` 재시도 assertion으로 확인한다.
  - 고정 대기는 쓰지 않는다.
- 콘솔: pageerror 0건, Google Fonts 도메인 외 console.error 0건

### 11.5 범위 검사 (`tests/scripts/verify-scope.mjs`)

BASE 대비 세 층을 각각 독립적으로 검사한다.
- committed: `git diff --name-only BASE HEAD`
- index: `git diff --cached --name-only BASE`
- working tree: `git diff --name-only BASE` + `git ls-files --others --exclude-standard`

경로 규칙
- 빌더 허용 경로(§11.1의 tracked source): 세 층 모두 허용한다.
- 하네스 소유 경로
  - 대상: `CLAUDE.md`, `harness-manifest.json`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`, `scripts/**`, `.claude/**`, `.codex/**`, `templates/**`, 이 설계 문서
  - committed 층에서는 면제한다.
  - 커밋되지 않은 변경은 위반이다: index↔HEAD 차이, working tree↔HEAD 차이, untracked 파일.
- 하네스 런타임 경로 `.harness/**`, `.venv/**`, `phases/HOO-81-portfolio-redesign/**`: 모든 층에서 면제한다.
- 그 밖의 경로는 모든 층에서 위반이다.

내용 규칙
- `js/data.js`
  - BASE→HEAD, BASE→index, BASE→working tree, index→working tree 네 구간을 각각 검사한다.
  - 삭제 줄은 0개여야 한다.
  - 추가 줄은 모두 trim하면 `featured: true,`여야 하고, 3개 이하여야 한다.
  - `--final`이면 BASE→working tree와 BASE→index의 추가 줄이 정확히 3개여야 한다.
- `index.html`: HEAD, index, working 세 버전 모두에 `Space+Grotesk`가 있어야 한다.
- `tests/.gitignore`: index와 working 두 버전의 줄 집합이 7줄과 정확히 같아야 한다.
- runtime 경로가 추적되면 위반이다.
- 루트 package.json이 있으면 위반이다.

출력
- 위반이 있으면 목록을 출력하고 exit 1로 끝낸다.

자체 검증
- 순수 함수 `evaluateScope(input) => string[]`를 export한다.
- `--self-test`는 12개 이상의 사례를 검증한다.
- 사례에는 stage한 금지 변경을 working tree에서만 되돌린 우회(data.js, Space Grotesk, README)가 반드시 포함된다.

### 11.6 통합 AC

- step 1 이후 모든 step: `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`
- 최종 step: 위 명령에 `--final`을 붙인다.

## 12. 변경 허용 경로와 git 경계

- index.json allowedPaths: `index.html`, `css/style.css`, `css/themes.css`, `js/main.js`, `js/data.js`, `tests/`
  - 하네스 설치 파일과 정책 파일은 넣지 않는다.
- 각 step에 tracked source 허용 파일과 runtime 쓰기 경로를 exact로 명시한다.
- `css/themes.css` 변경과 `index.html` 속성 변경은 step 8에서 fixture가 지정한 경우에만 허용한다.
- `index.html` 구조 변경은 step 5·6에서만 한다.
- 최종 step 10은 tests 보조 코드만 수정할 수 있다.
- git checkout·add·commit·push는 하네스만 한다. 빌더는 working tree만 수정한다.
- 빌더는 `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, 하네스 managed 파일을 수정하지 않는다.

## 13. Step 목록 (각 20분 이하)

| # | name | 예상 시간 |
|---|---|---|
| 0 | tests-env-setup | 14분 |
| 1 | scope-verifier | 20분 |
| 2 | content-baseline-fixture | 18분 |
| 3 | interaction-regression | 18분 |
| 4 | axe-baseline | 20분 |
| 5 | hero-featured | 20분 |
| 6 | section-order-layout | 20분 |
| 7 | focus-trap | 18분 |
| 8 | axe-remediation | 15분 |
| 9 | print-pdf | 15분 |
| 10 | final-verification | 12분 |

## 14. 빌더 재량

- 세부 시각 표현: 선행 문서의 토큰과 accent 제한 안에서 결정한다.
- CSS 클래스 구조: 이 문서에 명시한 id, data 속성, 클래스는 유지한다.
- 테스트 helper 분할
