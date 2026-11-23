# 포트폴리오 레이아웃·구조 리디자인 설계 (HOO-81)

- 날짜: 2026-11-23
- 브랜치: `feat/HOO-81/portfolio-redesign` (base `main`)
- 기준 commit(BASE): `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`
- 선행 시각 설계: `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md` (적용 완료, 계속 유효)

합의 메시지
- Q1: Discord 1574196542901059632
- Q2: 1574197289084387379
- Q3~Q5: 1574197696334405756 (추천안 일괄 확정)

리뷰 반영 이력
- 1차 Astra review `1432c5274b33`: 12개 보완. 승인 1574220980048634010
- 2차 `570513f95a2f`: 7건
- 3차 `9e8c69018dc0`: 4건
- 4차 `8014bc034fb4`: 3건
- 5차 `9277e222d6c3` (중앙 Harness): 4건
- 사용자 결정·콘텐츠·비목표는 바뀌지 않았다.

Harness 실행 identity (중앙 release)
- sourceCommit: `cb179f99acbb9ad32c5dcebab01ff19df7c3f4ae`
- manifestHash: `287201c44d766b0441470953005450b40f300de2718b246eeb44fd0e3c2f900a`
- distributionVersion: 2.0.0
- 고정 위치: `.harness/harness.lock.json`

## 1. 의도

2026-07-29 작업에서 색·서체·여백을 경영자의 절제 톤으로 정리했다. 그때 레이아웃 구조는 범위 밖이었다.

이번 작업은 그 톤을 유지한 채 구조를 다시 짠다. 채용·영입 의사결정자(임원 채용 담당자, 헤드헌터, 대표)가 30초 안에 다음 세 가지를 파악하는 것이 목표다.
1. COO·CTO 포지셔닝
2. 핵심 지표
3. 대표 프로젝트라는 근거

## 2. 목표 / 비목표 / 실패 조건

### 목표
- 1280×800 초기 viewport 안에 이름, tagline, 핵심 지표(STATS 4개), 대표 프로젝트 3개의 제목을 담는다.
- 섹션을 근거 우선 순서로 재배치한다.
- 섹션 리듬, 카드, 타임라인, 모바일 배치를 재구성한다.
- 기존 기능과 콘텐츠가 보존됨을 자동 테스트와 범위 검사로 증명한다.

### 비목표
- 색·서체 재설계
- 사이트 빌드 도구 도입
- 신규 기능
- 배포, merge, main 직접 변경

### 실패 조건 (기술적으로 동작해도 실패로 본다)
- 콘텐츠 문구·수치·경력 사실을 바꾸거나 새로 만들어 넣는다. 단 §7 예외는 허용한다.
- 비어 있는 email, phone, social을 채운다.
- 기존 기능이 회귀한다.
- axe serious/critical 위반이 남는다.
- 그라데이션이나 글로우 같은 장식이 추가된다.

## 3. 현재 코드 사실 (read-first 대상)

### 저장소 지침
- BASE에는 `README.md`만 있다.
- 현재 checkout에 있는 하네스 파일:
  - `CLAUDE.md` (중앙 Harness 계약 블록)
  - `.harness/harness.lock.json`, `.harness/policy.json`, `.harness/install-state.json`
  - `.claude/`, `.codex/`, `pytest.ini`, `.python-version`, `.gitattributes`
- Harness 공통 `scripts/`, `templates/`, `harness-manifest.json`은 중앙 store로 옮겨져 이 프로젝트에 없다.
- 빌더는 `CLAUDE.md`를 반드시 읽고 따른다. git 작업과 Harness 파일 변경은 하네스만 한다.

### 데이터 (`js/data.js`)
- 전역 const: `PROFILE`, `STATS`(4), `CAREER`, `VIS_ACCENT`, `makeVisual`, `PROJECTS`(13, 모두 `detail` 있음), `STRENGTHS`(6), `SKILLS`
- `PROFILE.tagline`은 BASE에서 렌더링되지 않는다.
- `email`, `phone`, `social.*`은 빈 문자열이다.
- 대표 프로젝트의 원본 index: Motion AD=1, VigoRight (의료 AI/VR)=5, Lost Energy Intel=7

### 렌더링 (`js/main.js`)
- 텍스트 채우기: `setText(id, value)`
- data 렌더 대상: `#heroStats`, `#strengthsGrid`, `#timeline`(`.timeline-item` > `.timeline-period` + `.timeline-card`), `#projectGrid`, `#skillsGrid`, `#contactActions`
- 프로젝트 카드: `article.project-card.has-detail[data-project=idx][tabindex=0][role=button]`

### 모달
- `openProjectModal(idx)`는 `lastFocused = document.activeElement`를 저장한 뒤 닫기 버튼에 포커스한다.
- 열기: `#projectGrid`의 click/keydown 위임
- 닫기: `[data-modal-close]` click 또는 Esc. Esc는 lightbox가 열려 있으면 lightbox를 먼저 닫는다.
- `closeProjectModal()` 순서: lightbox 닫기 → 모달 숨김 → `lastFocused`로 포커스 복귀

### lightbox
- `ensureLightbox()`가 처음 호출될 때만 `.lightbox`를 만든다. 새 페이지에는 `.lightbox`가 없다.
- `openLightbox(btn)` / `closeLightbox()`: 닫으면 opener로 포커스를 돌려준다.
- lightbox에는 Tab을 닫기 버튼에 고정하는 리스너가 있다. 모달에는 포커스 트랩이 없다.

### 기타
- 스크롤스파이: id 배열(about, strengths, career, projects, contact) 하드코딩 + IntersectionObserver(rootMargin -45%/-50%)
- reveal: IntersectionObserver로 `.in`을 붙인다. reduced-motion이면 즉시 붙인다.
- typing: `runTyping`. reduced-motion이면 `roles[0]`을 고정한다.
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
3. `p.hero-tagline#heroTagline` (신규. `setText`로 `PROFILE.tagline` 노출)
4. `h2.hero-role` (`#typed`, 보조 크기)
5. `#heroSummary`
6. `.hero-cta`: `.btn-primary` 프로젝트 보기, `.btn-ghost` 연락하기
7. `ul#heroStats`
8. `div#heroFeatured`

### 대표 카드 마크업과 phrasing-content 계약

```
<button type=button class=featured-card data-featured-card data-project={원본 idx}>
  <span class=featured-title>{p.title}</span>
  <span class=featured-blurb>{p.blurb}</span>
</button>
```

- `<button>`의 내용 모델은 phrasing content다. 카드 안에는 `span`과 텍스트만 넣는다.
- 다음 요소는 카드 안에 넣지 않는다: h1~h6, p, div, ul, ol, li, section, article
- `.featured-title`과 `.featured-blurb`는 CSS에서 `display: block`으로 세로로 쌓는다.
- 클래스 이름 `.featured-title`, `.featured-blurb`는 그대로 쓴다. 스타일과 테스트에서 이 클래스가 갖는 의미도 유지한다.

### 함수 계약

`renderFeaturedProjects(): void`
- `PROJECTS`를 원본 순서로 순회하며 `featured === true`인 항목만 위 마크업으로 렌더링한다.
- 새 문자열을 하드코딩하지 않는다.
- 그리드 렌더링 직후, 모달 리스너 등록 전에 호출한다.

`openProjectModal(projectIndex, triggerElement = document.activeElement): void`
- `lastFocused = triggerElement`로 저장한다.
- projectGrid는 `openProjectModal(idx, card)`로 호출한다.
- `#heroFeatured`에는 click 위임을 둔다. 네이티브 button이라 Enter와 Space도 click으로 처리된다.

`closeProjectModal(): void`
- 버튼, backdrop, Esc 어느 경로로 닫아도 `lastFocused`로 포커스를 복귀한다.

### data.js 변경
- index 1, 5, 7 객체에서 `title:` 다음 줄에 `featured: true,`를 넣는다. 총 3줄이다.
- 그 밖의 data.js 변경은 금지다.

### 첫 화면 AC (desktop 1280×800, hero.spec.js)

검사 대상: `#heroName`, `#heroTagline`, `#heroStats`, `.featured-title` 3개. 총 6개다.

사전 조건:
- `await page.evaluate(() => document.fonts.ready)`가 완료되어 있다.
- `window.scrollY === 0`이다.

각 대상은 다음을 모두 만족해야 한다.
1. `await expect(locator).toBeVisible()`
2. boundingBox가 존재하고 width > 0, height > 0
3. 대상 자신과 `document.documentElement`까지의 모든 조상에서 computed `visibility === visible`, computed `opacity === 1`. reveal 전환 중일 수 있으므로 `expect.poll`로 재시도한다.
4. viewport 경계 안에 있다: `x >= 0`, `y >= 0`, `x + width <= 1280`, `y + height <= 800`

이 AC는 통합 AC(`npm --prefix tests test`)에 포함된 hero.spec.js로 실행한다.

조건을 맞추기 위해 히어로의 세로 여백, 요약 폭, 카드 높이를 조정할 수 있다. 콘텐츠는 줄이지 않는다.

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
- contact: `.contact-card`를 둔다. h3 함께 만들어요와 그 문구는 유지한다.

### 내비게이션
- nav 순서: Career, Projects, Strengths, About, Contact. 라벨은 유지한다.
- 스크롤스파이 배열: career, projects, strengths, about, contact
- `.scroll-hint` href: `#career`

## 7. 콘텐츠 보존과 예외

### 7.1 기준
- BASE `js/data.js`를 평가한 결과: `BaselineData`
- BASE `index.html`의 정적 본문: `StaticContent`

### 7.2 허용 예외
1. index 1, 5, 7의 `featured: true`
2. `kickers`(DOM 순서)는 아래 둘 중 정확히 하나와 같아야 한다.
   - BASE: [01 — About, 02 — Strengths, 03 — Career, 04 — Projects, 05 — Stack &amp; Contact]
   - FINAL: [01 — Career, 02 — Projects, 03 — Strengths, 04 — About, 05 — Contact]
3. `sectionTitles`(DOM 순서)는 아래 둘 중 하나와 같아야 한다.
   - BASE: [소개, 업무상 강점, 경력 &amp; 창업, 프로젝트 &amp; 제품, 기술 스택 &amp; 연락처]
   - FINAL: [경력 &amp; 창업, 프로젝트 &amp; 제품, 업무상 강점, 소개, 연락처]
   - FINAL이면 `h3.subsection-title` 기술 스택이 정확히 1개 있어야 한다.
4. nav와 섹션의 순서. 비교할 때 `navLabels`는 정렬한 상태로 비교한다.
5. skill-group 제목의 heading level
6. step 8(§8.3)에서 axe 위반 대상 요소에 한해 aria-*, role, alt, lang, tabindex, for 속성을 바꾸는 것. 텍스트는 바꾸지 않는다.

그 밖의 `StaticContent` 필드는 BASE와 같아야 한다.

### 7.3 helper 계약 (`tests/helpers/content.js`)

공백 정규화 규칙 `norm(s)`
- `String(s).replace(/\s+/g, ' ').trim()`
- JS의 `\s`는 NBSP와 줄바꿈을 포함한다.
- 모든 텍스트 추출에 이 규칙을 적용한다.

`type BaselineData`
- 필드: `{ PROFILE, STATS, CAREER, VIS_ACCENT, PROJECTS, STRENGTHS, SKILLS }`
- JSON 직렬화 결과다. 함수는 없다.
- 배열은 원본 소스 순서를 유지하고 정렬하지 않는다.
- 객체 key 순서는 비교하지 않는다(deep-equal).

`type StaticContent` (모든 문자열에 `norm` 적용)
- `title: string`: document.title
- `metaDescription: string`
- `navLabels: string[]`: `.nav-link` 텍스트. 기본 `Array.prototype.sort()`(UTF-16 코드 단위 순)로 정렬한다.
- `heroEyebrow: string`
- `ctaLabels: string[]`: `.hero-cta .btn`, DOM 순서
- `kickers: string[]`: `.section-kicker`, DOM 순서
- `sectionTitles: string[]`: `.section-title`, DOM 순서
- `sectionSubs: string[]`: `.section-sub`, DOM 순서
- `aboutParagraphs: string[]`: `.about-text p:not([id])`, DOM 순서
- `aboutPoints: string[]`: `.about-points li`, DOM 순서
- `aboutMetaTerms: string[]`: `.about-meta dt`, DOM 순서
- `contactHeading: string`: `.contact-text h3`
- `contactText: string`: `.contact-text p`
- `footerNote: string`: `.footer-note`
- `footerTop: string`: `.footer-top`

함수 시그니처
- `readLiveData(page): Promise<BaselineData>`
  - `page.evaluate`로 전역 const를 모아 JSON 왕복한 값을 반환한다.
- `normalizeFeatured(data: BaselineData): BaselineData`
  - 입력은 변경하지 않는다. `structuredClone`으로 만든 사본을 반환한다.
  - `content-exceptions.json`의 `featured.indexes`([1, 5, 7])에 해당하는 `PROJECTS[i].featured === true`만 제거한다.
  - 다른 index에 `featured`가 있거나 값이 `true`가 아니면 throw한다.
- `extractStatic(page): Promise<StaticContent>`

## 8. 접근성

### 8.1 axe
- 기준: wcag2a·wcag2aa에서 serious/critical 위반 0건
- 검사 범위는 10개다.
  - page: 6개 조합(3 viewport × 2 테마)
  - 열린 모달: dark, light
  - 열린 lightbox: dark, light

### 8.2 포커스 트랩 (step 7)

함수 계약: `trapFocus(container: HTMLElement, options?: { returnFocusTo?: HTMLElement }): () => void`
- 호출하면 trap을 모듈 스택에 push한다.
- 최상위 trap만 Tab/Shift+Tab 순환을 처리한다. 그 아래 trap은 일시정지된다.
- 반환값 `release()`는 스택에서 자신을 제거하고, `returnFocusTo`로 포커스를 옮기고, 직전 trap을 재개한다. 두 번째 호출부터는 무시한다.

적용
- 모달: 열 때 push(returnFocusTo = trigger), 닫을 때 release한다.
- lightbox: 열 때 push(returnFocusTo = `.shot-zoom`)한다. 이 동안 모달 trap은 일시정지된다. 닫으면 이미지 트리거로 포커스가 돌아가고 모달 trap이 재개된다.
- 기존 lightbox의 Tab 고정 리스너는 제거한다.

기타
- `:focus-visible` outline을 유지한다.
- h1은 1개만 두고, heading level을 건너뛰지 않는다.

### 8.3 axe 기준선과 해소 (step 4 → step 8)

#### 실행 모드
- 수집 모드(`AXE_COLLECT=1`): step 4에서 최초 기준선을 만들 때만 쓴다.
  - 실제 fixture를 로드하지 않는다.
  - 실제 fixture 스키마 검사와 회귀 판정을 건너뛴다.
  - 합성 스키마 검사만 실행하고 결과를 기록한다.
- 일반 모드(기본): 실제 fixture를 로드한다. 실제 fixture 스키마 검사, target 단위 회귀 판정, 합성 스키마 검사를 모두 실행한다.

#### 수집 절차 (step 4)
1. `tests/.tmp/axe-collected/`를 초기화한다.
2. scenario×project마다 `{scenario}-{project}.json`을 따로 기록한다. 위반이 없으면 `[]`를 기록한다.
3. 파일이 정확히 10개인지 검증한다. 맞지 않으면 exit 1로 끝낸다.
4. 파일을 병합한다.
5. target별로 분류해 fixture를 생성한다.
6. 일반 모드로 실행해 통과하는지 확인한다.

#### fixture 스키마 (`tests/fixtures/axe-baseline.json`, 배열)
항목마다 다음 필드를 둔다.
- `key`: `{scenario}:{project}:{ruleId}`
- `scenario`, `project`, `ruleId`, `impact`
- `targets`: string[]
- `fixes`: `{ target, fixKind, fixFiles }[]`. `targets`의 각 원소마다 정확히 1개 있어야 한다.
- `fixFiles`: `fixes[].fixFiles`의 합집합과 같아야 한다.

`fixKind` 값과 수정 파일:
- css-token: `css/themes.css`
- css-rule: `css/style.css`
- js-render: `js/main.js`
- static-markup: `index.html`
- text-change: fixFiles는 빈 배열

#### target별 분류 규칙
- color-contrast: 색이 `var(--토큰)`에서 오면 css-token, 아니면 css-rule
- JS 렌더 영역 안의 target은 js-render. 해당 영역: `#heroStats`, `#heroFeatured`, `#timeline`, `#projectGrid`, `#strengthsGrid`, `#skillsGrid`, `#contactActions`, `#modalBody`, `.lightbox`
- `index.html` 정적 요소의 속성 문제는 static-markup
- 문구를 바꿔야만 해결되면 text-change
- 한 항목 안에 css-token과 css-rule이 섞일 수 있다.

#### 스키마 검증 (`validateBaseline`)
- 합성 사례(모든 모드):
  - 통과해야 함: 혼합 color-contrast
  - 거부해야 함: 합집합 불일치, target 누락, targets에 없는 target, fixFiles가 비어 있지 않은 text-change, 알 수 없는 fixKind
- 실제 fixture 검증은 일반 모드에서만 한다.

#### 회귀 판정 (일반 모드, step 4~7)
- 실패: fixture에 없는 key가 나오거나, 그 위반의 target이 해당 항목의 `targets`·`fixes`에 없을 때
- 허용: fixture에 있는 key나 target이 사라진 경우
- 새로 생긴 위반은 그 변화를 도입한 step 안에서 해결한다.

#### 해소 (step 8)
- 허용 소스: fixture의 `fixFiles` 합집합 + `tests/fixtures/axe-baseline.json`
- target 단위로 수정한다.
- `index.html`은 §7.2-6의 속성 변경만 허용한다.
- text-change나 구조 변경이 필요하면 중단하고 보고한다. 하네스가 step 5나 6을 다시 연다.
- 해소가 끝나면 fixture는 `[]`이다.

## 9. 반응형

| 대상 | 375 | 768 | 1280 |
|---|---|---|---|
| `#heroStats` | 2×2 (left 2종, top 2종) | 4열 1행 | 4열 1행 |
| `#heroFeatured` | 1열 | 2열 | 3열 |
| `#projectGrid` | 1열 | 2열 | 3열 |
| `#strengthsGrid` | 1열 | 2열 | 3열 |
| Career `.timeline-item` | 세로 (card.top >= period.bottom - 1) | 가로 (card.left >= period.right - 1, top 차이 < 24px) | 가로 |

- Career는 720px 이하에서 1열이다. highlights는 항상 펼쳐 둔다.
- 가로 스크롤이 생기면 안 된다.

## 10. 인쇄와 PDF

공통 조건
- 히어로, 대표 카드, 본문 섹션: visibility visible, opacity 1
- 표시되는 `.reveal`은 내용이 비어 있지 않아야 한다.
- `.theme-toggle`, `.menu-toggle`, `.scroll-hint`, `#projectModal`: display none

시나리오 A (새 페이지)
- `.lightbox`가 없거나, 있으면 display none이다.

시나리오 B (오버레이 열림)
1. screen 미디어에서 모달과 lightbox를 연다.
2. `.lightbox`가 존재하고 보이는지 확인한다.
3. print로 전환한다.
4. `.lightbox`와 `#projectModal`이 display none인지 확인한다.

PDF는 10KB를 넘고 1페이지 이상이어야 한다.

## 11. 검증 체계 (Q5)

### 11.1 tracked source와 runtime 경로 분리

테스트 도구는 `tests/` 안에만 둔다. 루트에 package.json을 두지 않는다.

tracked source 허용 경로
- 사이트: `index.html`, `css/style.css`, `css/themes.css`, `js/main.js`, `js/data.js`
- tests 파일: `tests/package.json`, `tests/package-lock.json`, `tests/.gitignore`, `tests/playwright.config.js`
- tests 디렉터리: `tests/helpers/**`, `tests/specs/**`, `tests/fixtures/**`, `tests/scripts/**`

runtime 쓰기 경로 (추적 금지)
- 설치(step 0): `tests/node_modules/**`, `tests/.npm-cache/**`, `tests/.pw-browsers/**`
- 실행(모든 step): `tests/.tmp/**`, `tests/test-results/**`, `tests/playwright-report/**`
- step 10: `tests/screenshots/**`
- Harness의 managed·policy·lock·state 파일은 위 두 목록 어디에도 넣지 않는다.

`tests/.gitignore`는 정확히 아래 7줄을 이 순서로 담는다.

```
node_modules/
.npm-cache/
.pw-browsers/
.tmp/
test-results/
playwright-report/
screenshots/
```

- 검증할 때는 파일 끝 개행 1개만 정규화한다(있으면 제거).
- 그다음 `\n`으로 나눈 배열이 위 7줄 배열과 길이, 순서, 값까지 일치해야 한다.
- 빈 줄, 중복 줄, 주석, CRLF, 순서 변경은 모두 거부한다.

### 11.2 공통 실행 계약 (`tests/scripts/with-env.sh`)

npm·node·playwright 명령은 모두 이 래퍼를 거쳐 실행한다. 설치, 테스트, verify-scope, axe CLI, 모든 AC, 하네스 testCommand가 여기에 해당한다. 래퍼는 외부 npm 프로세스가 시작되기 전에 환경을 정한다.

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

- 사용법: `sh tests/scripts/with-env.sh <명령...>`
- 하네스 testCommand: `sh tests/scripts/with-env.sh npm --prefix tests test`

### 11.3 tests/package.json

- devDependencies: `@playwright/test`, `@axe-core/playwright`
- scripts (환경 변수는 래퍼가 정한다)
  - `test`: `playwright test`
  - `browsers:install`: `playwright install chromium`
  - `verify-scope`: `node scripts/verify-scope.mjs`
  - `verify-scope:selftest`: `node scripts/verify-scope.mjs --self-test`
  - `fixtures`: `node scripts/make-fixtures.mjs`
- 설치: `sh tests/scripts/with-env.sh npm --prefix tests ci`. lock 파일이 없으면 `install`을 쓴다.

### 11.4 Playwright

- webServer: `python3 -m http.server 4173 --bind 127.0.0.1`, cwd는 저장소 루트, reuseExistingServer true
- reporter: list
- projects 6개: {mobile 375×812, tablet 768×1024, desktop 1280×800} × {dark, light}
  - 이름은 `mobile-dark` 형식
  - 각 project에 `colorScheme`과 `metadata.theme`을 지정한다.
- 테마 fixture: `addInitScript`는 `THEME_KEY`가 null일 때만 project 테마를 주입한다.
- 최초 방문 검사: fixture 없이 storage가 비어 있는 별도 context에서 light와 dark를 각각 확인한다.
- 스크롤스파이: 링크를 클릭한 뒤 `await expect(locator).toHaveClass(/active/)` 재시도 assertion으로 확인한다. 고정 대기는 쓰지 않는다.
- 콘솔: pageerror 0건, Google Fonts 도메인 외 console.error 0건

### 11.5 범위 검사 (`tests/scripts/verify-scope.mjs`)

BASE 대비 세 층을 각각 독립적으로 검사한다.
- committed: `git diff --name-only BASE HEAD`
- index: `git diff --cached --name-only BASE`
- working tree: `git diff --name-only BASE` + `git ls-files --others --exclude-standard`

경로 규칙
- 빌더 허용 경로: §11.1의 tracked source. 세 층 모두에서 허용한다.
- 하네스 소유 경로:
  - 목록: `CLAUDE.md`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`, `.claude/**`, `.codex/**`, `.harness/harness.lock.json`, `.harness/policy.json`, 이 설계 문서, 그리고 중앙 migration으로 제거된 레거시 `scripts/**`, `templates/**`, `harness-manifest.json`
  - committed 층에서는 면제한다.
  - 커밋되지 않은 변경은 위반이다: index와 HEAD의 차이, working tree와 HEAD의 차이, untracked 파일.
- 하네스 런타임 경로: 위 두 `.harness` 파일을 제외한 `.harness/**`(state, install lock, runtime), `.venv/**`, `phases/HOO-81-portfolio-redesign/**`. 모든 층에서 면제한다.
- 그 밖의 경로는 어느 층에서든 위반이다.

내용 규칙
- `js/data.js`: BASE→HEAD, BASE→index, BASE→working tree, index→working tree 네 구간을 모두 검사한다.
  - 삭제 줄은 0개여야 한다.
  - 추가 줄은 모두 `featured: true,`이고 3개 이하여야 한다.
  - `--final`이면 BASE→working tree와 BASE→index의 추가 줄이 정확히 3개여야 한다.
- `index.html`: HEAD, index, working 세 버전 모두에 `Space+Grotesk`가 있어야 한다.
- `tests/.gitignore`: index와 working 두 버전이 모두 §11.1 규칙을 만족해야 한다. 마지막 개행만 정규화하고, 정확한 7줄 배열과 순서를 비교한다.
- runtime 경로가 추적되면 위반이다.
- 루트 package.json이 있으면 위반이다.

동작과 self-test
- 위반이 하나라도 있으면 exit 1로 끝난다.
- `evaluateScope(input) => string[]`를 export한다.
- `--self-test`에 다음 사례를 포함한다.
  - stage한 뒤 working tree만 되돌리는 우회 3종: data.js, Space Grotesk, README
  - tests/.gitignore에서 추가 줄, 중복 줄, 빈 줄, 순서 변경, 주석 줄은 거부
  - 마지막 개행이 없는 tests/.gitignore는 허용
  - `.harness/harness.lock.json` 미커밋 수정은 위반
  - `.harness/runtime/x.json` untracked는 면제

### 11.6 통합 AC

- step 1 이후 모든 step: `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`
- hero.spec.js의 첫 화면 AC를 비롯한 각 spec의 AC는 이 명령 안에서 실행된다.
- 최종 step은 verify-scope에 `--final`을 붙인다.

## 12. 변경 허용 경로와 운영 경계

- index.json allowedPaths: `index.html`, `css/style.css`, `css/themes.css`, `js/main.js`, `js/data.js`, `tests/`
  - Harness managed·policy·lock·state 파일은 넣지 않는다.
- 각 step에 tracked source 허용 파일과 runtime 쓰기 경로를 정확히 명시한다.
- `css/themes.css`와 `index.html` 속성 변경은 step 8에서 fixture가 지정한 경우에만 한다. `index.html` 구조 변경은 step 5·6에서만 한다.
- 최종 step 10은 tests 보조 코드만 수정할 수 있다.
- 운영 명령은 모두 stable launcher로 하네스가 실행한다. 빌더는 실행하지 않는다.
  - 예: `harness --project-root . check`, `plan-session`, `review-plan`, `approval`, `runner`
- git checkout·add·commit·push는 하네스만 한다. 빌더는 working tree만 수정한다.
- 빌더는 다음 경로를 수정하지 않는다: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`

## 13. Step 목록 (각 20분 이하)

| # | name | 예상 시간 |
|---|---|---|
| 0 | tests-env-setup | 14분 |
| 1 | scope-verifier | 20분 |
| 2 | content-baseline-fixture | 20분 |
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
- 테스트 helper의 분할 방식
