# 포트폴리오 레이아웃·구조 리디자인 설계 (HOO-81)

- 날짜: 2026-11-23
- 브랜치: `feat/HOO-81/portfolio-redesign`, base `main`
- 기준 commit(BASE): `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`
- 선행 시각 설계(적용 완료, 계속 유효): `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
- 합의
  - Q1: Discord 1574196542901059632
  - Q2: 1574197289084387379
  - Q3~Q5: 1574197696334405756 (추천안 일괄 확정)
- 개정 근거: Astra plan review `20261123T002320234153Z-1432c5274b33`의 findings 11건 반영. 진행 승인: 1574220980048634010. 사용자 결정은 바뀌지 않았다.

## 1. 의도

2026-07-29 작업에서 색·서체·여백을 경영자의 절제 톤으로 정리했다. 그때 레이아웃 구조는 범위 밖이었다.

이번 작업은 그 톤을 유지한 채 구조를 다시 짠다. 목적은 채용·영입 의사결정자(임원 채용 담당자, 헤드헌터, 대표)가 30초 안에 다음 세 가지를 파악하게 하는 것이다.
1. COO·CTO 포지셔닝
2. 핵심 지표
3. 대표 프로젝트라는 근거

## 2. 목표 / 비목표 / 실패 조건

### 목표
- 첫 화면에 이름, tagline, 핵심 지표(STATS 4개), 대표 프로젝트 3개를 담는다.
- 섹션을 근거 우선 순서로 재배치한다.
- 섹션 리듬, 카드, 타임라인, 모바일 배치를 재구성한다.
- 기존 기능과 콘텐츠를 보존하고, 이를 자동 테스트와 범위 검사로 증명한다.

### 비목표
- 색·서체 재설계. 선행 문서의 토큰을 그대로 쓴다.
- 사이트에 빌드 도구 도입.
- 신규 기능.
- 배포, merge, main 직접 변경.

### 실패 조건 (기술적으로 동작해도 실패로 본다)
- 콘텐츠 문구·수치·경력 사실이 바뀌거나 창작된다. 단 §7의 예외는 허용한다.
- 비어 있는 email, phone, social 값이 채워진다.
- 기존 기능이 하나라도 회귀한다.
- axe serious/critical 위반이 남는다.
- 그라데이션이나 글로우 같은 장식이 추가된다.

## 3. 현재 코드 사실 (BASE 기준, 각 step의 read-first 대상)

### 저장소 지침
- `README.md`만 있다. BASE에는 저장소 안에 `CLAUDE.md`와 `AGENTS.md`가 없다.
- `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`는 빌더에게 read-only다. 문서 변경은 하네스만 한다.

### 데이터 (`js/data.js`)
- 전역 const: `PROFILE`, `STATS`(4개), `CAREER`, `VIS_ACCENT`, `makeVisual`, `PROJECTS`(13개, 모두 `detail` 있음), `STRENGTHS`(6개), `SKILLS`.
- `PROFILE.tagline`은 정의돼 있지만 BASE에서는 렌더링되지 않는다.
- `PROFILE.email`, `phone`, `social.*`은 빈 문자열이다.
- 대표 프로젝트의 원본 index는 다음과 같다.
  - Motion AD = 1
  - VigoRight (의료 AI/VR) = 5
  - Lost Energy Intel = 7

### 렌더링 (`js/main.js`)
- `setText(id, value)`로 텍스트를 채운다.
- data로 렌더링하는 영역: `#heroStats`, `#strengthsGrid`, `#timeline`, `#projectGrid`, `#skillsGrid`, `#contactActions`.
- 프로젝트 카드는 `article.project-card.has-detail[data-project=idx][tabindex=0][role=button]`이고, 안에 `.project-more` 버튼이 있다.

### 프로젝트 모달
- 열기: `openProjectModal(idx)`가 내부에서 `lastFocused = document.activeElement`를 저장하고 닫기 버튼에 포커스한다.
- 열기 경로: `#projectGrid`의 click 위임(`[data-project]`)과 keydown 위임(Enter·Space, `.project-card.has-detail`).
- 닫기 경로:
  - `#projectModal` click에서 `[data-modal-close]`(`.modal-backdrop`, `.modal-close`)
  - document keydown Esc. lightbox가 열려 있으면 lightbox부터 닫는다.
- `closeProjectModal()`의 동작 순서는 lightbox 닫기 → 모달 숨김 → `lastFocused` 복귀다.

### lightbox
- `ensureLightbox()`가 body에 `.lightbox[role=dialog][aria-modal=true]`를 만든다.
- `openLightbox(btn)`은 `.shot-zoom` 버튼에서 열고 `lightboxOpener`를 저장한다.
- `closeLightbox()`는 opener로 포커스를 복귀한다.
- lightbox에는 Tab을 닫기 버튼에 고정하는 리스너가 있다. 프로젝트 모달에는 포커스 트랩이 없다.

### 그 밖의 동작
- 스크롤스파이: `["about","strengths","career","projects","contact"]` 배열이 하드코딩돼 있다. IntersectionObserver로 `.nav-link.active`를 토글한다.
- reveal: `.reveal`에 IntersectionObserver로 `.in`을 붙인다. reduced-motion이면 즉시 붙인다.
- typing: `runTyping`이 문구를 돌린다. reduced-motion이면 `roles[0]`을 고정한다.
- 테마: localStorage `THEME_KEY`에 저장한다. 최초 방문 시 시스템 설정을 따른다.
- 메뉴: `#menuToggle`, `#navLinks.open`, `aria-expanded`로 동작하고, 링크를 클릭하면 닫힌다.
- 인쇄: `css/style.css`의 `@media print`.
- Google Fonts 링크의 Space Grotesk는 제거 금지다. data.js의 SVG가 이 서체를 하드코딩한다.

## 4. 접근 방식

| 안 | 내용 | 판단 |
|---|---|---|
| A (선택) | 절제 톤 유지 + 레이아웃·구조 재구성 | Q1에서 선택 |
| B | 시각 방향 전면 교체 | 선행 작업을 되돌리게 되어 기각 |
| C | 마감만 다듬기 | 체감 변화가 부족해 기각 |

## 5. 첫 화면과 대표 프로젝트 (Q2, Q3)

### 히어로 DOM 순서
1. `.hero-eyebrow` — 유지하되 시각 비중을 줄인다.
2. `h1#heroName`
3. `p.hero-tagline#heroTagline` — 신규 요소. `setText("heroTagline", PROFILE.tagline)`으로 기존 데이터를 노출할 뿐 새 문구가 아니다.
4. `h2.hero-role` (`#typed`) — 보조 크기.
5. `#heroSummary`
6. `.hero-cta` — 주 버튼 `.btn-primary`는 프로젝트 보기, 보조 `.btn-ghost`는 연락하기.
7. `ul#heroStats`
8. `div#heroFeatured`

### 함수 계약
- `renderFeaturedProjects(): void`
  - `PROJECTS`를 원본 순서로 돌며 `featured === true`인 항목만 `#heroFeatured`에 렌더링한다.
  - 카드: `<button type=button class=featured-card data-featured-card data-project={원본 idx}>`. 안에 `h3.featured-title`(`p.title`)와 `p.featured-blurb`(`p.blurb`)를 둔다.
  - 새 문자열을 하드코딩하지 않는다.
  - 호출 위치: 프로젝트 그리드 렌더링 직후, 모달 리스너 등록 전.
- `openProjectModal(projectIndex, triggerElement = document.activeElement): void`
  - `lastFocused = triggerElement`로 저장한다. 나머지 동작은 BASE와 같다.
  - `#projectGrid` 위임 호출부는 `openProjectModal(idx, card)`로 바꾼다.
  - `#heroFeatured`에도 click 위임을 둔다. 네이티브 button이라 Enter와 Space도 click으로 처리된다.
- `closeProjectModal(): void` — 닫기 버튼, backdrop, Esc 모든 경로에서 `lastFocused`로 포커스를 복귀한다.

### data.js 변경
- index 1, 5, 7 객체에서 `title:` 줄 바로 다음에 `featured: true,` 한 줄씩, 총 3줄을 추가한다.
- 그 밖의 data.js 변경은 금지한다.

### 측정 기준 (1280×800, scrollY=0)
- `#heroName`, `#heroTagline`, `#heroStats`: 각각 rect.y >= 0, rect.bottom <= 800.
- `.featured-title` 3개: 각각 rect.bottom <= 1200.

## 6. 섹션 구조 (Q4) — 최종 표

| 순서 | section id | class | kicker | heading |
|---|---|---|---|---|
| 1 | hero | hero | 없음 | h1 `#heroName` |
| 2 | career | section | `01 — Career` | h2 경력 &amp; 창업 |
| 3 | projects | section section-alt | `02 — Projects` | h2 프로젝트 &amp; 제품 |
| 4 | strengths | section | `03 — Strengths` | h2 업무상 강점 (section-sub 유지) |
| 5 | about | section section-alt | `04 — About` | h2 소개 |
| 6 | contact | section | `05 — Contact` | h2 연락처 |

### 섹션 내부 배치
- about
  - 본문(`.about-grid`) 다음에 `h3.subsection-title` 기술 스택과 `#skillsGrid`를 둔다.
  - skill-group 제목은 h3에서 h4로 내린다.
- contact
  - `.contact-card`를 둔다. h3 함께 만들어요와 문구는 유지한다.

### 내비게이션
- `#navLinks` 순서: Career, Projects, Strengths, About, Contact. 라벨은 유지한다.
- 스크롤스파이 배열: `["career","projects","strengths","about","contact"]`.
- `.scroll-hint`의 href: `#career`.

## 7. 콘텐츠 보존 규칙과 예외

### 기준
- BASE `js/data.js`를 평가한 JSON 전체.
- BASE `index.html`의 정적 본문.

### 허용되는 차이
1. index 1, 5, 7 객체에만 `featured: true` 추가.
2. `.section-kicker` 집합은 다음 둘 중 정확히 하나와 같아야 한다.
   - BASE: 01 — About, 02 — Strengths, 03 — Career, 04 — Projects, 05 — Stack &amp; Contact
   - FINAL: 01 — Career, 02 — Projects, 03 — Strengths, 04 — About, 05 — Contact
3. `.section-title` 집합은 다음 둘 중 하나와 같아야 한다.
   - BASE: 소개, 업무상 강점, 경력 &amp; 창업, 프로젝트 &amp; 제품, 기술 스택 &amp; 연락처
   - FINAL: 경력 &amp; 창업, 프로젝트 &amp; 제품, 업무상 강점, 소개, 연락처
   - FINAL이면 `h3.subsection-title` 기술 스택이 정확히 1개 있어야 한다.
4. nav와 섹션의 순서. 라벨 집합은 같아야 한다.
5. skill-group 제목의 heading level(h3 → h4). 텍스트는 같아야 한다.

### 그 밖에 BASE와 동일해야 하는 정적 본문
- `title`, meta description
- nav 라벨, `.hero-eyebrow`, CTA 라벨, `.section-sub`
- about의 정적 p, `.about-points li`, `.about-meta dt`
- contact의 h3와 p
- footer 정적 텍스트

## 8. 접근성

### axe 검사
- serious/critical 위반 0건.
- 대상: 6개 조합 페이지, 열린 모달 × dark/light, 열린 lightbox × dark/light.

### 포커스 트랩 계약
- `trapFocus(container: HTMLElement, options?: { returnFocusTo?: HTMLElement }): () => void`
  - 호출하면 모듈 내부 trap 스택에 push한다.
  - 최상위 trap만 Tab과 Shift+Tab을 순환 처리하고, 그 아래 trap은 일시정지 상태가 된다.
  - 반환되는 `release()`는 다음 순서로 동작한다: 스택에서 제거 → `returnFocusTo`에 포커스 → 직전 trap 재개.
  - `release()`를 두 번 호출해도 안전해야 한다.
- 모달: 열 때 `trapFocus(dialog, { returnFocusTo: trigger })`를 걸고, 닫을 때 release한다.
- lightbox: 열 때 `trapFocus(lightbox, { returnFocusTo: 해당 .shot-zoom })`를 건다. 그동안 모달 trap은 일시정지된다.
  - 닫으면 이미지 트리거로 포커스가 복귀하고 모달 trap이 재개된다.
  - 기존 Tab 고정 리스너는 제거한다.

### 그 밖의 기준
- `:focus-visible` outline을 유지한다.
- h1은 1개만 두고, heading level을 건너뛰지 않는다.
- WCAG AA 대비를 지킨다. 부족하면 `css/themes.css`의 토큰 명도만 조정한다.

## 9. 반응형

| 대상 | 375 | 768 | 1280 |
|---|---|---|---|
| `#heroStats` | 2×2 | 4열 | 4열 |
| `#heroFeatured` | 1열 | 2열 | 3열 |
| `#projectGrid` | 1열 | 2열 | 3열 |
| `#strengthsGrid` | 1열 | 2열 | 3열 |

- Career: 데스크톱은 2열(기간 | 내용), 720px 이하는 1열. highlights는 항상 펼쳐 둔다.
- 모든 viewport에서 가로 스크롤이 없어야 한다.

## 10. 인쇄와 PDF

검사 상태는 두 가지다: 스크롤하지 않은 새 페이지, 그리고 모달과 lightbox가 열린 상태.
- 히어로, 대표 카드, 본문 섹션: visibility visible, opacity 1.
- 표시되는 `.reveal`: 내용이 비어 있지 않아야 한다.
- `.modal`, `.lightbox`, `.theme-toggle`, `.menu-toggle`, `.scroll-hint`: display none.
- `page.pdf()` 결과: 10KB 초과, 1페이지 이상.

## 11. 검증 체계 (Q5)

### 테스트 도구 위치
- 테스트 도구는 `tests/` 안에만 둔다. 루트에 package.json을 만들지 않는다.

### tests/package.json
- devDependencies: `@playwright/test`, `@axe-core/playwright`
- scripts
  - `test`: `PLAYWRIGHT_BROWSERS_PATH=./.pw-browsers playwright test`
  - `browsers:install`: `PLAYWRIGHT_BROWSERS_PATH=./.pw-browsers playwright install chromium`
  - `verify-scope`: `node scripts/verify-scope.mjs`
  - `verify-scope:selftest`: `node scripts/verify-scope.mjs --self-test`
  - `fixtures`: `node scripts/make-fixtures.mjs`
- npm --prefix는 cwd를 tests/로 잡는다. 따라서 브라우저는 `tests/.pw-browsers`, npm 캐시는 `tests/.npm-cache`에 설치되고, sandbox에서 쓰기 가능한 경로만 쓴다.
- 설치 순서: `npm --prefix tests ci --cache tests/.npm-cache` (최초에는 install) → `npm --prefix tests run browsers:install`

### Playwright 설정
- `tests/playwright.config.js`
  - webServer: `python3 -m http.server 4173 --bind 127.0.0.1`, cwd는 저장소 루트, reuseExistingServer true.
  - baseURL: `http://127.0.0.1:4173`
- projects 6개: {mobile 375×812, tablet 768×1024, desktop 1280×800} × {dark, light}.
  - 이름 형식은 `mobile-dark`처럼 쓴다.
  - 각각 `colorScheme`과 `metadata.theme`을 지정한다.
- 테마 고정: `tests/helpers/theme.js`의 fixture가 `addInitScript`로 `THEME_KEY`에 project 테마를 넣는다.
- 최초 방문: 저장값 없는 별도 context(`browser.newContext({ colorScheme })`)에서 light와 dark를 각각 검사한다.
- 콘솔: pageerror 0건. fonts.googleapis.com, fonts.gstatic.com을 제외한 console.error 0건.

### 범위 검사 (`tests/scripts/verify-scope.mjs`)
- BASE `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d` 대비 변경을 모두 합쳐 검사한다.
  - 커밋 + unstaged: `git diff --name-only BASE`
  - staged: `git diff --cached --name-only BASE`
  - untracked: `git ls-files --others --exclude-standard`
- 아래 위반이 하나라도 있으면 exit 1로 끝나고 위반 목록을 출력한다.
  - 빌더 허용 파일 밖의 변경. 허용 파일은 `index.html`, `css/style.css`, `css/themes.css`, `js/main.js`, `js/data.js`, 그리고 `tests/` 하위(gitignore 제외)뿐이다.
  - 하네스 면제 경로 밖의 문서 변경. 면제 경로는 정확히 세 가지다: 이 설계 문서, `phases/HOO-81-portfolio-redesign/**`, `.harness/**`. 그 밖의 `docs/**`, `CLAUDE.md`, `AGENTS.md`, `README.md`, `assets/**`, `.nojekyll`, 루트 `package.json`이 바뀌면 위반이다.
  - `js/data.js` 규칙 위반. diff(unified=0, BASE 대비 working tree)에 삭제 줄이 없어야 하고, 추가 줄은 모두 trim 결과가 `featured: true,`이며 3개 이하여야 한다. `--final`이면 정확히 3개여야 한다.
  - `index.html`의 Google Fonts 링크에 `Space+Grotesk`가 없음.
- 순수 함수 `evaluateScope(input) => string[]`를 export한다.
- `--self-test`는 내장 위반 케이스 8개 이상이 모두 검출되는지 확인한다.

### 통합 AC
- step 2 이후 모든 step: `npm --prefix tests test && npm --prefix tests run verify-scope`
- 최종 step: `verify-scope -- --final`

## 12. 변경 허용 경로

- 전체 허용 경로: `index.html`, `css/style.css`, `css/themes.css`, `js/main.js`, `js/data.js`, `tests/`
- step별 허용 파일은 각 step 문서에 정확히 적는다.
  - `css/themes.css`는 step 7(대비 토큰)에서만 수정할 수 있다.
  - 최종 step 9는 tests 보조 코드만 수정할 수 있다. 사이트 결함이 나오면 해당 구현 step을 다시 연다.

## 13. 빌더 재량

- 대표 카드와 각 섹션의 세부 시각 표현. 선행 문서의 토큰과 accent 사용처 제한은 따른다.
- CSS 클래스 구조. 단 이 문서에 명시한 id, data 속성, 클래스는 유지한다.
- 테스트 helper를 나누는 방식.
