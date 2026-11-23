# 포트폴리오 레이아웃·구조 리디자인 설계 (HOO-81)

- 날짜: 2026-11-23
- 브랜치: `feat/HOO-81/portfolio-redesign` (base `main`)
- 기준 commit(BASE): `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`
- 선행 시각 설계: `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md` (적용 완료, 계속 유효)
- 합의
  - Q1: Discord 1574196542901059632
  - Q2: 1574197289084387379
  - Q3~Q5: 1574197696334405756 (추천안 일괄 확정)
- 리뷰 반영 이력
  - 1차 Astra `1432c5274b33`: 12건, 승인 1574220980048634010
  - 2차 `570513f95a2f`: 7건
  - 3차 `9e8c69018dc0`: 4건
  - 4차 `8014bc034fb4`: 3건
  - 5차 `9277e222d6c3`: 4건
  - 6차 `5331b1167a3c`: 6건
  - 7차 `e849940ab365`: 6건
  - 8차 `77397ef36423`: 6건
  - 9차 `1890a28bd4a9`: 7건
  - 10차 `754f651120b1`: 4건
  - 11차 `2e850c809ca8`: 5건 (diff 인자 분리, entry key 계약, plan 수정 전 회귀 gate, focus trap 분할, locator 문법)
  - 12차 `a26257befcd4`: 4건 (axe 준비 절차, 회귀 spec 분할, blocked 그룹 중단, collected↔baseline 양방향 일치)
  - 사용자 결정·콘텐츠·비목표는 바뀌지 않았다.
- Harness 실행 identity (중앙 release, `.harness/harness.lock.json`이 고정)
  - sourceCommit: `cb179f99acbb9ad32c5dcebab01ff19df7c3f4ae`
  - manifestHash: `287201c44d766b0441470953005450b40f300de2718b246eeb44fd0e3c2f900a`
  - distributionVersion: 2.0.0

## 1. 의도

2026-07-29 작업에서 색·서체·여백을 경영자의 절제 톤으로 정리했다. 그때 레이아웃 구조는 범위 밖이었다.

이번 작업은 그 톤을 유지한 채 구조를 다시 짠다. 채용·영입 의사결정자(임원 채용 담당자, 헤드헌터, 대표)가 30초 안에 다음 세 가지를 파악하게 하는 것이 목표다.
1. COO·CTO 포지셔닝
2. 핵심 지표
3. 대표 프로젝트라는 근거

## 2. 목표 / 비목표 / 실패 조건

### 목표
- 1280×800 초기 viewport 안에 이름, tagline, STATS 4개, 대표 프로젝트 제목 3개를 담는다.
- 섹션을 근거 우선 순서로 재배치한다.
- 섹션 리듬, 카드, 타임라인, 모바일 배치를 재구성한다.
- 기존 기능과 콘텐츠 보존을 자동 테스트와 범위 검사로 증명한다.

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
- 그라데이션·글로우 같은 장식을 추가한다.

## 3. 현재 코드 사실 (read-first 대상)

### 저장소 지침
- BASE에는 `README.md`만 있다.
- 현재 checkout의 하네스 파일
  - `CLAUDE.md` (중앙 Harness 계약)
  - `.harness/harness.lock.json`, `.harness/policy.json`, `.harness/install-state.json`
  - `.claude/`, `.codex/`, `pytest.ini`, `.python-version`, `.gitattributes`
- Harness 공통 `scripts/`, `templates/`, `harness-manifest.json`은 중앙 store에 있고 이 저장소에는 없다.

### 데이터 (`js/data.js`)
- 전역 const: `PROFILE`, `STATS`(4), `CAREER`, `VIS_ACCENT`, `makeVisual`, `PROJECTS`(13, 모두 `detail` 있음), `STRENGTHS`(6), `SKILLS`
- `PROFILE.tagline`은 BASE에서 렌더링되지 않는다.
- email·phone·social.*은 빈 문자열이다.
- 대표 프로젝트 원본 index: Motion AD=1, VigoRight (의료 AI/VR)=5, Lost Energy Intel=7

### 렌더링 (`js/main.js`)
- `setText(id, value)`로 텍스트를 채운다. 첫 인자는 id 문자열이다.
- data를 렌더링하는 대상: `#heroStats`, `#strengthsGrid`, `#timeline`(`.timeline-item` > `.timeline-period` + `.timeline-card`), `#projectGrid`, `#skillsGrid`, `#contactActions`
- 프로젝트 카드: `article.project-card.has-detail[data-project=idx][tabindex=0][role=button]`

### 모달
- `openProjectModal(idx)`는 `lastFocused = document.activeElement`를 저장한 뒤 닫기 버튼에 포커스한다. 열리면 body에 `modal-open` 클래스가 붙는다.
- 열기: `#projectGrid`의 click/keydown 위임
- 닫기: `[data-modal-close]` 또는 Esc. lightbox가 열려 있으면 Esc는 lightbox부터 닫는다.

### lightbox
- `ensureLightbox()`를 처음 호출할 때만 `.lightbox`가 생성된다. 모달 안의 `.shot-zoom`으로 연다.
- lightbox에는 Tab 고정 리스너가 있다. 모달에는 포커스 트랩이 없다.

### 기타
- 스크롤스파이: id 배열(about, strengths, career, projects, contact) 하드코딩 + IntersectionObserver
- reveal: IntersectionObserver로 `.reveal`에 `.in`을 붙인다. reduced-motion이면 즉시 붙인다.
- typing: `runTyping`. reduced-motion이면 `roles[0]`으로 고정한다.
- 테마: localStorage `THEME_KEY`. 저장값이 없으면 시스템 설정을 따른다.
- 메뉴: `#menuToggle`, `#navLinks.open`, `aria-expanded`
- 인쇄: `@media print`
- Google Fonts의 Space Grotesk 링크는 제거 금지다. data.js의 SVG가 이 서체를 하드코딩한다.

## 4. 접근 방식

| 안 | 내용 | 판단 |
|---|---|---|
| A (선택) | 절제 톤 유지 + 레이아웃·구조 재구성 | Q1에서 선택 |
| B | 시각 방향 전면 교체 | 선행 작업을 되돌림 |
| C | 마감만 다듬기 | 체감 변화 부족 |

## 5. 첫 화면과 대표 프로젝트 (Q2, Q3)

### 히어로 DOM 순서
1. `.hero-eyebrow`
2. `h1#heroName`
3. `p.hero-tagline#heroTagline`: 신규. 정확히 `setText('heroTagline', PROFILE.tagline)`으로 채운다.
4. `h2.hero-role` (`#typed`, 보조 크기)
5. `#heroSummary`
6. `.hero-cta`: `.btn-primary` 프로젝트 보기, `.btn-ghost` 연락하기
7. `ul#heroStats`
8. 대표 프로젝트 컨테이너. 마크업은 정확히 다음과 같다.

```
<div id="heroFeatured" role="region" aria-label="대표 프로젝트"></div>
```

### 대표 카드 마크업 (phrasing-content 계약)

```
<button type="button" class="featured-card" data-featured-card data-project="{원본 idx}">
  <span class="featured-title">{p.title}</span>
  <span class="featured-blurb">{p.blurb}</span>
</button>
```

- 카드 안에는 `span`과 텍스트만 둔다.
- h1~h6, p, div, ul, ol, li, section, article은 넣지 않는다.
- 두 span은 `display: block`으로 표시한다.

### 함수 계약
- `renderFeaturedProjects(): void`
  - 원본 순서대로 `featured === true`인 항목만 렌더링한다.
  - 새 문자열을 하드코딩하지 않는다.
  - 그리드 렌더링 직후에 호출한다.
- `openProjectModal(projectIndex, triggerElement = document.activeElement): void`
  - `lastFocused = triggerElement`
  - projectGrid에서는 `openProjectModal(idx, card)`로 호출한다.
  - `#heroFeatured`에는 click 위임을 둔다.
- `closeProjectModal(): void`: 어느 경로로 닫든 `lastFocused`로 포커스를 복귀한다.
- tagline: `setText('heroTagline', PROFILE.tagline)`. id 문자열 `heroTagline`과 `#heroTagline` 요소가 일치해야 한다.

### data.js 변경
- index 1, 5, 7의 `title:` 다음 줄에 `featured: true,`를 넣는다. 총 3줄이다.
- 그 밖의 data.js 변경은 금지다.

### 첫 화면 AC (desktop 1280×800, hero.spec.js)
- 대상: `#heroName`, `#heroTagline`, `#heroStats`, `.featured-title` 3개
- 사전 조건: `document.fonts.ready` 완료, `window.scrollY === 0`
- 각 대상은 다음을 모두 만족해야 한다.
  - `toBeVisible()`
  - width > 0, height > 0
  - 자신과 모든 조상의 computed `visibility === visible`, `opacity === 1` (`expect.poll`로 확인)
  - `x >= 0`, `y >= 0`, `x + width <= 1280`, `y + height <= 800`
- 이 검사는 통합 AC에 포함된다.

## 6. 섹션 구조 (Q4) — 최종 표

| 순서 | section id | class | kicker | heading |
|---|---|---|---|---|
| 1 | hero | hero | 없음 | h1 `#heroName` |
| 2 | career | section | `01 — Career` | h2 경력 &amp; 창업 |
| 3 | projects | section section-alt | `02 — Projects` | h2 프로젝트 &amp; 제품 |
| 4 | strengths | section | `03 — Strengths` | h2 업무상 강점 (section-sub 유지) |
| 5 | about | section section-alt | `04 — About` | h2 소개 |
| 6 | contact | section | `05 — Contact` | h2 연락처 |

- about: 본문 다음에 `h3.subsection-title` 기술 스택과 `#skillsGrid`를 둔다. skill-group 제목은 h4로 바꾼다.
- contact: `.contact-card`를 둔다. h3 함께 만들어요는 유지한다.
- nav 순서: Career, Projects, Strengths, About, Contact
- 스크롤스파이 배열: career, projects, strengths, about, contact
- `.scroll-hint` href: `#career`
- 스크롤스파이 테스트 예시(정확한 JS 문법)
  - `const link = page.locator('.nav-link[href="#projects"]'); await link.click(); await expect(link).toHaveClass(/active/);`
  - `const link = page.locator('.nav-link[href="#about"]'); await link.click(); await expect(link).toHaveClass(/active/);`

## 7. 콘텐츠 보존과 예외

### 7.1 기준
- `BaselineData`: BASE `js/data.js`를 평가한 결과. step 3에서 검증한다.
- `StaticContent`: BASE `index.html`의 정적 본문. step 4에서 검증한다.

### 7.2 허용 예외
1. index 1, 5, 7의 `featured: true`
2. `kickers`(DOM 순서)는 다음 둘 중 정확히 하나와 같아야 한다.
   - BASE: [01 — About, 02 — Strengths, 03 — Career, 04 — Projects, 05 — Stack &amp; Contact]
   - FINAL: [01 — Career, 02 — Projects, 03 — Strengths, 04 — About, 05 — Contact]
3. `sectionTitles`(DOM 순서)는 다음 둘 중 하나와 같아야 한다.
   - BASE: [소개, 업무상 강점, 경력 &amp; 창업, 프로젝트 &amp; 제품, 기술 스택 &amp; 연락처]
   - FINAL: [경력 &amp; 창업, 프로젝트 &amp; 제품, 업무상 강점, 소개, 연락처]
   - FINAL이면 `h3.subsection-title` 기술 스택이 정확히 1개 있어야 한다.
4. nav와 섹션의 순서. `navLabels`는 정렬해서 비교한다.
5. skill-group 제목의 heading level
6. axe remediation 그룹 step(§8.3)에서 위반 대상 요소의 aria-*, role, alt, lang, tabindex, for 속성을 바꾸는 것. 텍스트는 바꾸지 않는다.
- 이 목록 밖의 콘텐츠 변경(예: axe text-change로 문구·색 대비를 위해 텍스트를 바꿔야 하는 경우)은 이 계획에서 허용하지 않는다. 필요하면 Harness 재계획에서 설계 예외와 담당 step allowedPaths를 먼저 확정한다(§8.3 실행 불가 그룹).

### 7.3 helper 계약 (`tests/helpers/content.js`)
- `norm(s) = String(s).replace(/\s+/g, ' ').trim()`
- `BaselineData`
  - 필드: `{ PROFILE, STATS, CAREER, VIS_ACCENT, PROJECTS, STRENGTHS, SKILLS }`
  - JSON 형태, 배열 순서 유지, deep-equal로 비교한다.
- `StaticContent` (모든 값에 norm 적용)
  - `title`, `metaDescription`
  - `navLabels` (정렬)
  - `heroEyebrow`
  - `ctaLabels`, `kickers`, `sectionTitles`, `sectionSubs` (DOM 순서)
  - `aboutParagraphs` (`.about-text p:not([id])`)
  - `aboutPoints`, `aboutMetaTerms`
  - `contactHeading`, `contactText`, `footerNote`, `footerTop`
- 함수
  - step 3: `readLiveData(page): Promise<BaselineData>`
  - step 3: `normalizeFeatured(data): BaselineData`. 입력을 바꾸지 않는다(structuredClone). 지정 index만 허용한다.
  - step 4: `extractStatic(page): Promise<StaticContent>`

### 7.4 회귀 spec 분할 (step 5, 6)
- step 5 `modal-regression.spec.js`: `tests/helpers/modal.js`와 함께 모달·lightbox 회귀만 다룬다.
- step 6 `ui-regression.spec.js` + `first-visit.spec.js`: 테마, 최초 방문, 메뉴, scrollspy, typing, reduced-motion 회귀만 다룬다.
- `tests/helpers/modal.js` 계약 (step 5)
  - `openFirstProjectByClick(page): Promise<Locator>` — 첫 `.project-card`를 click으로 열고 그 카드를 반환
  - `openFirstProjectByEnter(page): Promise<Locator>`
  - `closeVia(page, how: 'button'|'backdrop'|'esc'): Promise<void>` (backdrop은 `{x:5, y:5}` 클릭)
  - `expectFocused(page, locator): Promise<void>`
  - `modalTitle(page): Locator` — 열린 모달의 제목 요소
  - `findProjectWithShots(page): Promise<number | null>` — 모달 안에 `.shot-zoom`이 렌더링되는 첫 프로젝트 index. 없으면 null

## 8. 접근성

### 8.1 axe
- 기준: wcag2a·wcag2aa의 serious/critical 위반 0건
- 시나리오 10개
  - page: 3 viewport × 2 테마 = 6
  - 모달 열림 × dark/light = 2
  - lightbox 열림 × dark/light = 2
- 모든 시나리오는 수집 모드와 일반 모드 모두 §8.4의 `prepareForAxe`를 먼저 통과한 뒤에만 axe를 실행한다.

### 8.2 포커스 트랩 (step 22, 23)

`trapFocus(container, options?: { returnFocusTo?: HTMLElement }): () => void`
- 스택 구조이며 최상위 trap만 Tab 순환을 처리한다. document Tab 핸들러는 1개다.
- `release()`
  - 스택에서 제거하고, returnFocusTo로 포커스를 옮기고, 직전 trap을 재개한다.
  - 여러 번 호출해도 안전하다.
- step 22 (modal): trapFocus 구현, 모달 열 때 push(returnFocusTo = trigger), 닫을 때 release. 모달 경계 Tab/Shift+Tab 순환과 닫기 경로별 복귀를 검증한다. lightbox 코드와 기존 lightbox Tab 리스너는 건드리지 않는다.
- step 23 (lightbox): lightbox 열 때 push(returnFocusTo = `.shot-zoom`)
  - 열려 있는 동안 모달 trap은 일시정지된다.
  - 닫히면 모달 trap이 재개된다.
  - 기존 lightbox Tab 고정 리스너는 제거한다.
  - `:focus-visible` outline을 유지·검증한다.
- h1은 1개만 두고, heading level을 건너뛰지 않는다.

### 8.3 axe 기준선, 식별, 해소

#### canonical target 식별 (step 7)

`selectors`는 정보로만 기록한다. 비교에는 아래 key를 쓴다.

```
canonicalTarget = {ruleId}::{anchor}::{textSig}
```

anchor: 요소 자신부터 조상 방향으로 처음 만나는 것
1. `[data-featured-card][data-project]` → `featured:{N}`
2. `[data-project]` → `project:{N}`
3. `[id]` → `#{id}`
4. landmark(header, nav, main, footer) → 태그명
5. 해당 없음 → `document`

textSig
- `norm(textContent)`를 쓴다. 비어 있으면 aria-label, alt, title, src 파일명 순으로 대체한다.
- 숫자는 `#`으로 바꾼다.
- 80자로 자른다.
- 고정 alias를 적용한다(설계 고정, 실행 중 추가 금지).
  - `## — Stack & Contact` → `## — Contact`
  - `기술 스택 & 연락처` → `연락처`

안정성 보장 범위
- anchor와 대상의 조상 관계가 유지되는 동안에만 같은 key를 보장한다. anchor subtree를 통째로 이동하는 경우가 이에 해당한다.
- 대상이 anchor 경계 밖으로 나가면 다른 key가 된다.

#### entry key와 병합 단위 (step 9, 이후 모든 step 공통)

- `makeEntryKey({ scenario, project, ruleId }): string` → 정확히 `${scenario}:${project}:${ruleId}`
  - scenario는 `page|modal|lightbox`, project는 Playwright project 이름(예: `desktop-dark`)
  - 세 값 중 하나라도 빈 문자열이거나 `:`를 포함하면 throw
- entry는 (scenario, project, ruleId) 조합마다 정확히 1개다.
- `targets`: canonical target을 중복 제거하고 문자열 오름차순 정렬해 저장한다.
- `selectors`: 중복 제거·정렬해 정보로만 저장한다.
- 같은 canonical target이 다른 scenario 또는 project에 나타나면 별도 entry로 각각 보존한다. 합치지 않는다.
- 이 계약을 따르는 곳: `mergeCollected`, baseline entry(`key`), `validateBaseline`, `projectEntry`, `compareCollectedBaseline`, `checkRegression`, `checkCollectedRegression`, `countCollectedTargets`, `checkGroupDone`, `checkCollectedCoverage`, `prunePlan`, 그리고 step 16 이후 모든 step
- (key, target) 쌍이 위반 1건의 단위다.

#### helper 계약 (`tests/helpers/axe.js`)

step 7 — 식별
- `ALIASES`
- `canonicalTargetInPage(el) → { anchor, text }`
- `canonicalFromDescriptor({ ruleId, anchor, text }) → string`
- `runAxe(page, { include }) → Violation[]`
  - `Violation = { ruleId, impact, selectors: string[], targets: string[] }`

step 8 — 시나리오 준비 (`tests/helpers/axe-prepare.js`, §8.4)

step 9 — entry key, 수집 파일 관리
- `makeEntryKey` (위 계약)
- `COLLECT_DIR`: 기본 실제 수집 디렉터리(`tests/.tmp/axe-collected` 절대경로)
- `EXPECTED_FILES: readonly string[]` (10개)
  - `page-{mobile,tablet,desktop}-{dark,light}.json`
  - `modal-desktop-{dark,light}.json`
  - `lightbox-desktop-{dark,light}.json`
- `resolveCollectDir(opts?: { collectDir?: string }): string`
  - 우선순위: `opts.collectDir` → `AXE_COLLECT_DIR` → `COLLECT_DIR`
  - `tests/.tmp/` 밖이면 `Error('collectDir must be under tests/.tmp')`를 던진다.
- `resetCollected(opts?): string`
- `writeCollected(scenario: 'page'|'modal'|'lightbox', project: string, violations: Violation[], opts?): string`
  - 파일명이 `EXPECTED_FILES`에 없으면 throw한다.
- `mergeCollected(opts?: { collectDir?: string, out?: string }): { entries: MergedEntry[], outPath: string }`
  - 파일 구성이 다르면 `Error('collected files mismatch: missing=[...] extra=[...]')`를 던진다.
  - 파일마다 scenario·project를 파일명에서 얻고, 같은 ruleId의 violation들을 하나의 entry로 합친다(targets·selectors 중복 제거·정렬).
  - entries는 key 오름차순으로 정렬한다.
  - out 기본값: `tests/fixtures/axe-collected.json`
  - `MergedEntry = { key, scenario, project, ruleId, impact, targets, selectors }`, `key === makeEntryKey(entry)`
- CLI
  - `--reset [--dir <d>]`
  - `--merge [--dir <d>] [--out <f>]`
  - throw가 나면 stderr에 출력하고 exit 1

step 10 — baseline 스키마·회귀 판정·누락 정책
- `BASELINE_PATH`: `tests/fixtures/axe-baseline.json`
- `FIX_FILES_BY_KIND`
  - css-token: `[css/themes.css]`
  - css-rule: `[css/style.css]`
  - js-render: `[js/main.js]`
  - static-markup: `[index.html]`
  - text-change: `[]`
- `baselineExists(path = BASELINE_PATH): boolean`
- `loadBaseline(path = BASELINE_PATH): BaselineEntry[]`
  - 파일 없음, JSON 오류, 배열 아님이면 throw한다.
- `resolveBaselineMode({ path = BASELINE_PATH, env = process.env } = {}): 'check' | 'skip'`
  - 파일이 있으면 `check`
  - 파일이 없고 `env.AXE_ALLOW_MISSING_BASELINE === '1'`이면 `skip`
  - 그 밖에는 `Error('axe baseline missing: tests/fixtures/axe-baseline.json')`. 기본 실행은 누락 시 실패한다.
- `validateBaseline(entries: unknown): string[]`
  - 각 항목의 `key === makeEntryKey(항목)`이어야 한다. key는 고유해야 한다.
  - `targets`는 중복 없이 정렬되어 있어야 한다.
  - 각 `fixes[i].fixFiles`가 `FIX_FILES_BY_KIND[fixKind]`와 정확히 같아야 한다.
  - 항목 `fixFiles`는 fixes의 합집합이어야 한다.
- `checkRegression(violations, baseline, scenario, project): string[]`
  - 순수 함수이며 입력을 바꾸지 않는다.
  - 각 violation의 key는 `makeEntryKey({ scenario, project, ruleId })`로 만든다.
  - 반환 형식: `new-key:{key}`, `new-target:{key}:{target}`
- `assertEmptyFile(path = BASELINE_PATH): { ok: boolean, reason?: string }`
- CLI: `--assert-empty [path]` (정확히 `[]`이면 0, 아니면 1)

step 11 — collected↔baseline 투영·양방향 일치
- `PROJECTION_FIELDS = ['key','scenario','project','ruleId','impact','targets','selectors']`
- `projectEntry(entry): ProjectedEntry`
  - 위 7개 필드만 남긴다. `targets`·`selectors`는 중복 제거·오름차순 정렬한다. `fixes`, `fixFiles` 같은 baseline 전용 필드는 버린다.
  - 필드가 없거나 `key !== makeEntryKey(entry)`이면 throw한다.
- `compareCollectedBaseline(collected: MergedEntry[], baseline: BaselineEntry[]): { ok: boolean, missingEntries: string[], extraEntries: string[], missingTargets: { key, target }[], extraTargets: { key, target }[], fieldMismatches: { key, field }[] }`
  - 순수 함수이며 입력을 바꾸지 않는다. 양쪽을 `projectEntry`로 투영해 key로 맞춘다.
  - `missingEntries`: collected에 있고 baseline에 없는 key
  - `extraEntries`: baseline에 있고 collected에 없는 key
  - `missingTargets`/`extraTargets`: 같은 key에서 각각 baseline에 없는/ collected에 없는 target
  - `fieldMismatches`: 같은 key에서 `scenario`, `project`, `ruleId`, `impact`, `selectors` 중 다른 필드
  - 어느 한쪽에 중복 key가 있으면 throw한다.
  - 모든 목록이 비어 있을 때만 `ok`다.
- CLI: `--check-baseline-match [--collected <f>] [--baseline <f>]`
  - `--collected` 기본값: `tests/fixtures/axe-collected.json`
  - ok면 exit 0. 아니면 다섯 목록을 stderr에 출력하고 exit 1. 파일 없음·파싱 오류도 exit 1

step 12 — remediation plan 스키마
- `PLAN_PATH`: `tests/fixtures/axe-remediation-plan.json`
- `GROUP_ID_RE = /^[a-z0-9]+(?:-[a-z0-9]+)*$/`
- `loadPlan(path = PLAN_PATH): Plan`
  - 파일 없음, JSON 오류, 형식 오류면 throw한다.
- `validateRemediationPlan(plan, baseline, opts?: { coverage?: boolean, requireEmpty?: boolean }): string[]`
  - `requireEmpty`이면 `groups.length !== 0`일 때 `groups: expected empty, got {n}` 오류를 낸다.
- CLI: `--check-plan [--coverage] [--require-empty] [--plan <f>] [--baseline <f>]`
  - 오류가 있거나 파일이 없으면 exit 1

step 13 — 실행 가능성 검사 (blocked·text-change·빈 fixFiles 중단)
- `validateRemediationExecutable(plan: Plan, baseline: BaselineEntry[]): string[]`
  - 순수 함수다. 남은 그룹마다 다음을 오류로 반환한다.
    - `blocked-group:{id}`: `blocked === true`
    - `text-change:{id}:{target}`: 그룹 target의 baseline fix가 `text-change`
    - `empty-fixfiles:{id}`: `fixFiles`가 빈 배열
  - groups가 `[]`이면 `[]`를 반환한다.
- CLI: `--check-executable [--plan <f>] [--baseline <f>]`
  - 오류 0이면 exit 0
  - 아니면 `Harness 재계획 필요: 실행 불가 remediation 그룹` 첫 줄과 오류 목록을 stderr에 출력하고 exit 1
  - 파일 없음·파싱 오류는 exit 1
- 이 검사가 실패하면 자동 remediation step 생성과 다음 단계 진행을 모두 멈춘다. 기존 콘텐츠 변경이 필요한 경우 새 계획에서 §7.2 설계 예외와 담당 step allowedPaths를 확정한 뒤에만 진행한다.
- `fixFiles = []`인 실행 step은 생성하지 않는다.

step 14 — 현재 수집 결과 판정
- `checkGroupDone(collected: MergedEntry[], plan: Plan, groupId: string): { done: boolean, remaining: { key: string, target: string }[] }`
  - 순수 함수다.
  - `collected`가 배열이 아니면 `Error('invalid collected')`
  - `groupId`가 형식 오류이거나 plan에 없으면 `Error('unknown group id: {id}')`
- `checkCollectedCoverage(collected: MergedEntry[], plan: Plan): { ok: boolean, uncovered: { key: string, target: string }[] }`
  - 순수 함수다.
  - `collected`의 모든 (key, target)에 대해 target이 남은 plan groups 중 어느 한 그룹의 targets에 정확히 포함되어야 `ok`다.
  - 빠진 쌍은 `uncovered`로 반환한다.
  - 자동 편입하지 않는다.
- `countCollectedTargets(collected: MergedEntry[]): number`
  - 모든 entry의 (key, target) 쌍을 센다. 같은 target이 다른 entry에 있으면 각각 센다.
  - `collected`가 배열이 아니면 throw한다.
- CLI (`--collected` 기본값은 모두 `tests/.tmp/axe-current.json`)
  - `--check-group-done <id> [--collected <f>] [--plan <f>]`: done이면 0, 그 밖에는 1
  - `--check-coverage [--collected <f>] [--plan <f>]`
    - uncovered가 0이면 exit 0
    - 그 밖에는 `재계획 필요: plan 밖 잔여 target` 목록을 stderr에 출력하고 exit 1
  - `--assert-no-violations [--collected <f>]`
    - `countCollectedTargets === 0`이면 0
    - 그 밖에는 개수와 목록을 출력하고 exit 1
  - 파일 없음이나 파싱 오류는 exit 1

step 15 — plan 수정 전 회귀 gate와 plan 정리 도구
- `checkCollectedRegression(collected: MergedEntry[], baseline: BaselineEntry[]): string[]`
  - 순수 함수다. 각 entry에 대해 `entry.key === makeEntryKey(entry)`를 확인하고(불일치면 `bad-key:{key}`), `checkRegression`과 같은 규칙으로 `new-key:{key}`, `new-target:{key}:{target}`을 반환한다.
- `prunePlan(plan: Plan, collected: MergedEntry[], baseline: BaselineEntry[]): Plan`
  - 순수 함수이며 입력을 바꾸지 않는다.
  - 현재 collected 어느 entry에도 없는 target을 그룹에서 제거한다.
  - targets가 빈 그룹을 삭제한다.
  - 그룹 fixFiles를 남은 target의 baseline fixes로 다시 계산한다. 결과는 기존 fixFiles의 부분집합이다.
  - id, difficulty, estMinutes, blocked, reason은 유지한다. target이나 그룹을 추가하지 않는다.
- CLI
  - `--check-regression [--collected <f>] [--baseline <f>]`: 오류 0이면 exit 0, 아니면 stderr 목록 + exit 1
  - `--prune-plan [--collected <f>] [--baseline <f>] [--plan <f>]`
    - 먼저 파일 3개를 읽고 `checkCollectedRegression`을 실행한다.
    - 읽기 실패나 회귀 오류가 있으면 plan 파일에 쓰지 않고 exit 1. 이때 plan 파일 bytes는 변하지 않는다.
    - 통과하면 `prunePlan` 결과를 `JSON.stringify(plan, null, 2) + '\n'`으로 쓰고 exit 0
- plan 파일 수정은 `--prune-plan`으로만 한다. 손으로 편집하는 것은 금지다.

#### fixture

`tests/fixtures/axe-collected.json` (step 16)
- 병합한 수집 결과. tracked이며 정보용이다. entry 계약을 따른다.

`tests/fixtures/axe-baseline.json` (step 17)
- 항목 필드: `key`(= `makeEntryKey`), `scenario`, `project`, `ruleId`, `impact`, `targets`(canonical, 중복 제거·정렬), `selectors`, `fixes[{ target, fixKind, fixFiles }]`(target마다 1개), `fixFiles`(합집합)
- `projectEntry`로 투영했을 때 axe-collected.json과 양방향으로 정확히 같아야 한다(`--check-baseline-match`).
- fixKind와 fixFiles의 대응은 `FIX_FILES_BY_KIND`와 정확히 같아야 한다.

`tests/fixtures/axe-remediation-plan.json` (step 17)
- 형식: `{ groups: [{ id, targets: canonical[], fixFiles: string[], difficulty: 'low'|'medium'|'high', estMinutes: number, blocked: boolean, reason: string }] }`
- 규칙
  - `id`는 `GROUP_ID_RE`를 만족하고 고유해야 한다.
  - target은 baseline canonical target 합집합의 부분집합이고, 그룹 사이에 중복이 없어야 한다.
  - `fixFiles`는 해당 target fixFiles의 합집합이다.
  - `estMinutes`는 1~20 정수다.
  - `difficulty`는 열거값 중 하나다.
  - text-change가 있으면 `blocked`는 true다.
  - `--coverage`이면 모든 baseline target이 정확히 한 그룹에 속해야 한다.
  - 실행 가능 조건(`--check-executable`)을 통과하지 못하면 다음 단계로 가지 않는다.

#### 실행 모드
- 두 모드 공통: 시나리오마다 `prepareForAxe(page, { scenario })`를 먼저 호출하고, 반환된 `include`로 `runAxe(page, { include })`를 실행한다. 준비가 throw하면 그 테스트는 실패한다.
- 수집 모드(`AXE_COLLECT=1`): axe.spec.js는 baseline을 로드하지 않는다. `writeCollected`만 하며 위치는 `resolveCollectDir()`가 정한다.
- 일반 모드(기본): axe.spec.js가 `resolveBaselineMode()`를 호출한다.
  - check이면 회귀 판정(`checkRegression`), `validateBaseline`, plan 검증을 실행한다.
  - baseline이 없으면 기본적으로 실패한다.
  - `AXE_ALLOW_MISSING_BASELINE=1`은 step 16의 일반 실행 명령에서만 쓴다.
- 수집 명령 순서(COLLECT_CHAIN): 최초 수집, gate, recheck, finalize, remediation 그룹 step에 공통으로 적용한다.
  1. helper 합성 검증: `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js`. 독립 디렉터리만 쓰며, 실제 `COLLECT_DIR`가 보존되는지 증명한다.
  2. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset`
  3. 실제 수집: `AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js`
  4. 1과 3이 모두 성공한 뒤에만 merge: `sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge [--out <f>]`
  - 모두 `&&`로 순차 연결한다. 병렬 실행은 금지다.
- 회귀 사전 gate(REGRESSION_GATE): plan 수정 전에 COLLECT_CHAIN 바로 뒤에 `&&`로 연결한다.
  - `sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-regression --collected tests/.tmp/axe-current.json`

#### 단계

step 16 — 최초 수집
- 10개 시나리오를 구현하고 `axe-collected.json`을 만든다.
- 이 step의 일반 실행에만 `AXE_ALLOW_MISSING_BASELINE=1`을 붙인다.
  - 명령: `AXE_ALLOW_MISSING_BASELINE=1 sh tests/scripts/with-env.sh npm --prefix tests test`
  - 하네스는 이 step의 본문 AC로 검증한다.
  - 옵션 없는 기본 실행이 이 시점에 실패하는 것은 의도된 결과다.
  - step 17 이후에는 기본 testCommand가 통과해야 한다.

step 17 — 분류
- 예상 시간 = 묶음별 (2분 + target × 1분)의 합 + 5분
- 20분을 넘으면 즉시 중단하고 재계획을 요청한다.
- 20분 이하면 실제 출처를 조사해 baseline과 plan을 확정한다.
- AC에 `--check-baseline-match`와 `--check-executable`을 포함한다. blocked 그룹(text-change 포함)이 하나라도 있으면 step은 실패로 끝나고 Harness 재계획을 요청한다.

step 18~24 — 회귀 판정
- 새 key나 target이 나오면 실패, 사라진 것은 허용한다.
- 자동 편입은 금지다.
- 해당 step이 만든 실제 신규 위반은 그 step 안에서 고친다.
- 기존 위반의 식별이 깨진 경우면 중단하고 재계획을 요청한다.

step 25 — gate (순차, `&&`)
1. COLLECT_CHAIN (`--merge --out tests/.tmp/axe-current.json`)
2. REGRESSION_GATE (`--check-regression`). 실패하면 plan은 건드리지 않고 중단한다.
3. `--prune-plan --collected tests/.tmp/axe-current.json`. 내부에서도 회귀를 다시 확인하며 실패 시 plan bytes는 그대로다.
4. `--check-coverage --collected tests/.tmp/axe-current.json`. 빠진 target이 있으면 자동 편입하지 않고 재계획 사유로 실패한다.
5. `--check-plan`
6. `--check-executable`. 실패하면 remediation step을 만들지 않고 다음 단계로 가지 않는다(Harness 재계획 사유).
7. 1~6이 모두 통과하고 그룹이 남으면 Harness가 그룹마다 `axe-remediation-{id}` step을 step 25와 26 사이에 재계획한다.

재계획 그룹 step 계약
- 생성 조건: `--check-executable` 통과, 그룹 `blocked === false`, `fixFiles.length >= 1`. 하나라도 어기면 생성 금지.
- allowedPaths
  - 소스: 그룹 `fixFiles`만
  - runtime: `tests/.tmp/**`(실제 `COLLECT_DIR`, `axe-current.json` 포함), `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`
- 시간: 20분 이하
- plan 파일은 수정하지 않는다.
- AC (순차): COLLECT_CHAIN(`--out tests/.tmp/axe-current.json`) → REGRESSION_GATE → `--check-group-done {id}` → `npm --prefix tests test` → verify-scope

step 26 — recheck
- gate 1~6을 같은 순서·같은 allowedPaths로 다시 실행한다. REGRESSION_GATE를 plan 수정 전에 똑같이 적용한다.
- 추가 AC
  - `--check-plan --require-empty`
  - `--assert-no-violations --collected tests/.tmp/axe-current.json`
- baseline에 target이 남아 있어도 회귀 판정은 통과할 수 있다. 그 허점은 `--assert-no-violations`로 막는다.

step 27 — finalize
1. 시작 전에 COLLECT_CHAIN과 REGRESSION_GATE를 다시 실행한다.
2. `--check-plan --require-empty && --assert-no-violations`가 통과해야 한다. 아니면 중단한다.
3. 이 step에서만 baseline을 `[]`로 바꾼다.
4. AC: `--assert-empty` + 일반 axe 전체 통과

### 8.4 axe 시나리오 준비 (`tests/helpers/axe-prepare.js`, step 8)

```
prepareForAxe(page, { scenario, projectIndex?, timeoutMs = 10000 }):
  Promise<{ scenario, include: string, projectIndex: number | null, revealChecked: number, scrollSteps: number }>
```

- `scenario`: `'page' | 'modal' | 'lightbox'`. 그 밖이면 reject.
- 공통 절차 (모든 scenario)
  1. `await page.evaluate(() => document.fonts.ready)` 후 `document.fonts.status === 'loaded'`를 assertion으로 확인한다.
  2. 페이지 전체 순회 스크롤: `scrollY = 0`에서 시작해 `innerHeight × 0.8` 간격으로 `scrollHeight` 끝까지 내려가며 단계마다 2 animation frame을 기다린다. 끝에서 `scrollTo(0, 0)`로 돌아간다. 단계 수는 `scrollSteps`로 반환한다.
  3. 모든 `.reveal` 요소에 대해 `.in` 클래스, computed `visibility === 'visible'`, `opacity === '1'`을 `expect.poll`로 확인한다. 개수는 `revealChecked`로 반환한다.
- `page`: `include = 'body'`, `projectIndex = null`
- `modal`
  - `projectIndex` 기본값 0. 해당 `[data-project="{N}"]` 카드를 click으로 연다.
  - 열림: body에 `modal-open` 클래스, `#projectModal`이 visible, computed opacity `1`
  - 표시: `modalTitle(page)` 텍스트가 `norm(PROJECTS[N].title)`과 같다.
  - 콘텐츠 로딩: 모달 안 모든 `img`가 `complete && naturalWidth > 0`, 모든 `svg`의 bounding box width·height > 0, 본문 텍스트 길이 > 0
  - `include = '#projectModal'`
- `lightbox`
  - `projectIndex` 기본값: `findProjectWithShots(page)`. null이면 `no-shots-project`로 reject.
  - 모달을 위와 같이 연 뒤 첫 `.shot-zoom`을 click한다. `.shot-zoom`이 없거나 lightbox가 열리지 않으면 `lightbox-not-open`으로 reject.
  - 열림: `.lightbox`가 1개이며 visible, computed opacity `1`, `document.activeElement`가 `.lightbox` 안에 있다.
  - 콘텐츠 로딩: `.lightbox img`가 `complete && naturalWidth > 0`
  - `include = '.lightbox'`
- 오류 계약: 모든 실패는 message가 `prepareForAxe: `로 시작하는 `Error`로 reject한다. `expect.poll` 타임아웃도 아래 코드로 변환한다.
  - `unknown-scenario`
  - `fonts-not-ready`
  - `reveal-hidden:{개수}`
  - `modal-not-open`
  - `lightbox-not-open`
  - `content-not-loaded:{img|svg|text}`
  - `no-shots-project`
- 준비 helper는 reduced-motion이나 테마를 바꾸지 않는다. 입력 page 상태만 사용한다.

## 9. 반응형

| 대상 | 375 | 768 | 1280 |
|---|---|---|---|
| `#heroStats` | 2×2 | 4열 1행 | 4열 1행 |
| `#heroFeatured` | 1열 | 2열 | 3열 |
| `#projectGrid` | 1열 | 2열 | 3열 |
| `#strengthsGrid` | 1열 | 2열 | 3열 |
| Career `.timeline-item` | 세로 | 가로 (top 차이 < 24px) | 가로 |

가로 스크롤이 없어야 한다.

## 10. 인쇄와 PDF

- 히어로, 대표 카드, 본문: visible이고 opacity 1이다.
- 보이는 `.reveal`은 비어 있지 않다.
- 토글, 메뉴, scroll-hint, `#projectModal`: display none이다.
- 시나리오 A (새 페이지): `.lightbox`가 없거나, 있으면 display none이다.
- 시나리오 B (overlay 열림)
  1. screen에서 `.lightbox`가 존재하고 visible인지 먼저 확인한다.
  2. print로 전환한다.
  3. `.lightbox`와 `#projectModal`이 display none인지 확인한다.
- PDF
  - 10240바이트를 넘어야 한다.
  - `buf.toString('latin1').match(/\/Type\s*\/Page\b/g)`로 센 값이 1 이상이어야 한다. `/Pages`는 세지 않는다.
  - 파서 의존성은 추가하지 않는다.

## 11. 검증 체계 (Q5)

### 11.1 tracked source와 runtime 경로

tracked source
- 사이트: `index.html`, `css/style.css`, `css/themes.css`, `js/main.js`, `js/data.js`
- tests 파일: `tests/package.json`, `tests/package-lock.json`, `tests/.gitignore`, `tests/playwright.config.js`
- tests 디렉터리: `tests/helpers/**`, `tests/specs/**`, `tests/fixtures/**`, `tests/scripts/**`

runtime 쓰기 경로 (추적 금지)
- `tests/node_modules/**`, `tests/.npm-cache/**`, `tests/.pw-browsers/**`
- `tests/.tmp/**`, `tests/test-results/**`, `tests/playwright-report/**`
- 최종 step만: `tests/screenshots/**`

Harness managed·policy·lock·state 파일은 위 두 목록에서 제외한다.

`tests/.gitignore`는 다음 7줄을 이 순서로 담는다. 마지막 개행만 정규화하고 정확히 일치해야 한다.

```
node_modules/
.npm-cache/
.pw-browsers/
.tmp/
test-results/
playwright-report/
screenshots/
```

### 11.2 공통 실행 계약 (`tests/scripts/with-env.sh`)

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

- npm, node, playwright는 모두 이 래퍼를 거쳐 실행한다.
- 하네스 testCommand: `sh tests/scripts/with-env.sh npm --prefix tests test`

### 11.3 tests/package.json

- devDependencies: `@playwright/test`, `@axe-core/playwright`
- scripts
  - `test`: `playwright test`
  - `browsers:install`: `playwright install chromium`
  - `verify-scope`: `node scripts/verify-scope.mjs`
  - `verify-scope:selftest`: `node scripts/verify-scope.mjs --self-test`
  - `fixtures`: `node scripts/make-fixtures.mjs`

### 11.4 Playwright와 콘솔 수집

- webServer: `python3 -m http.server 4173 --bind 127.0.0.1`
- projects 6개: {mobile 375×812, tablet 768×1024, desktop 1280×800} × {dark, light}
- 테마 fixture: `THEME_KEY`가 null일 때만 주입한다.
- 최초 방문 검사: fixture 없이 별도 context에서 한다.
- 스크롤스파이: §6의 정확한 locator 예시와 `toHaveClass(/active/)` 재시도 assertion

`collectConsoleErrors(page): ErrorCollector`

```
type ErrorRecord = { kind: 'pageerror' | 'console.error', message: string, url: string | null, line: number | null, column: number | null }
type ErrorCollector = { finish(): Promise<{ pageErrors: ErrorRecord[], consoleErrors: ErrorRecord[] }> }
```

- 호출하는 즉시 listener를 등록한다.
- pageerror는 모두 기록한다.
- console.error는 location url의 hostname이 정확히 Google Fonts 두 도메인일 때만 제외한다. 파싱에 실패하면 제외하지 않는다.
- `finish()`는 networkidle 이후 사본을 반환한다.
- 사용 순서는 collect → goto → 동작 → finish → 두 배열이 `[]`인지 확인으로 고정한다.

### 11.5 범위 검사 (`tests/scripts/verify-scope.mjs`)

#### Git diff 인자 (분리, step 1)
- `GIT_DIFF_PATH_ARGS = ['--no-renames', '--name-only']`: 경로 수집 전용. committed·index·worktree·uncommittedHarness에 쓴다.
- `GIT_DIFF_PATCH_ARGS = ['--no-renames', '--unified=0']`: `js/data.js` 4구간(BASE→HEAD, BASE→index, BASE→worktree, index→worktree) 실제 patch 수집 전용.
- 두 상수는 export하며 서로 섞어 쓰지 않는다. 이동은 삭제 + 추가로 판정한다.
- `collectInput({ git = runGit } = {})`: git 실행 함수를 주입할 수 있다. `runGit(args): string`은 Git 읽기 명령만 실행한다.
- `input.dataJsDiffs = { baseHead, baseIndex, baseWorktree, indexWorktree }`는 실제 patch 문자열이며, 그대로 `checkDataJsDiff`에 전달된다.

#### 경로 정책 (step 1)
- 빌더 허용 경로: §11.1 tracked source
- 하네스 소유 경로
  - 대상: `CLAUDE.md`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`, `.claude/**`, `.codex/**`, `.harness/harness.lock.json`, `.harness/policy.json`, 이 설계 문서, 레거시 `scripts/**`, `templates/**`, `harness-manifest.json`
  - committed 층은 면제한다.
  - 미커밋 변경은 위반이다.
- 하네스 런타임(면제): 위 두 `.harness` 파일을 제외한 `.harness/**`, `.venv/**`, `phases/HOO-81-portfolio-redesign/**`
- runtime 경로가 추적되거나 루트 package.json이 있으면 위반이다.

#### 내용 판정 (step 2)
- `js/data.js` 4구간 공통 (`checkDataJsDiff(patchText, { requireExactly3 })`)
  - `---`/`+++` 헤더를 제외한 삭제 줄 0줄
  - 추가 줄은 trim 후 `featured: true,`만
  - 3줄 이하
- `--final`이면 BASE→HEAD, BASE→index, BASE→worktree 각각 정확히 3줄이다. index→worktree에는 공통 규칙만 적용한다.
- `index.html` 3종은 `Space+Grotesk`를 포함해야 한다.
- `tests/.gitignore`(index, worktree)는 §11.1 규칙을 따른다.
- 합성 테스트: 주입한 가짜 git이 `GIT_DIFF_PATCH_ARGS` 호출에만 patch를, `GIT_DIFF_PATH_ARGS` 호출에는 이름 목록을 돌려준다. data.js 4구간이 patch 인자로 호출되었고 그 patch 문자열이 `checkDataJsDiff`까지 전달되어 판정에 쓰이는지 확인한다.

### 11.6 통합 AC
- step 1 이후 기본: `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`
- step 16: 일반 실행에 `AXE_ALLOW_MISSING_BASELINE=1`을 붙인다.
- step 27·28: `--assert-empty`를 추가한다.
- step 28: `verify-scope -- --final`을 추가한다.
- 각 step은 자기 spec을 먼저 단독으로 실행한 뒤 전체 회귀를 돌린다.

## 12. 변경 허용 경로와 운영 경계

### allowedPaths
- index.json allowedPaths: `index.html`, `css/style.css`, `css/themes.css`, `js/main.js`, `js/data.js`, `tests/`
  - Harness managed·policy·lock·state 파일은 제외한다.
- 각 step에 tracked source 허용 파일과 runtime 쓰기 경로를 명시한다.

### 사이트 파일 변경 시점
- `index.html`
  - 구조 변경: step 18, 19, 20
  - 속성 변경: 재계획된 remediation 그룹 step만
- `css/themes.css`: remediation 그룹 step만

### 명령 권한
- Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 빌더와 검증 스크립트에 허용한다.
- 하네스만 실행
  - Git 상태 변경 명령: init, checkout, switch, add, commit, push, reset, stash, merge, rebase, tag 등
  - Harness 운영 명령: `harness --project-root . check`, `plan-session`, `review-plan`, `approval`, `runner`

### 빌더 수정 금지
- `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`

## 13. Step 목록 (각 20분 이하, 검증·디버깅 포함)

| # | name | 예상 | 선행 |
|---|---|---|---|
| 0 | tests-env-setup | 14분 | 없음 |
| 1 | scope-paths | 18분 | 0 |
| 2 | scope-content | 18분 | 0~1 |
| 3 | content-data-baseline | 15분 | 0~2 |
| 4 | content-static-baseline | 16분 | 0~3 |
| 5 | modal-regression | 16분 | 0~4 |
| 6 | ui-regression | 16분 | 0~5 |
| 7 | axe-canonical | 18분 | 0~6 |
| 8 | axe-prepare | 18분 | 0~7 |
| 9 | axe-collect-tooling | 18분 | 0~8 |
| 10 | axe-baseline-regression | 18분 | 0~9 |
| 11 | axe-baseline-projection | 16분 | 0~10 |
| 12 | axe-remediation-plan-schema | 16분 | 0~11 |
| 13 | axe-plan-executable | 14분 | 0~12 |
| 14 | axe-current-checks | 16분 | 0~13 |
| 15 | axe-regression-prune | 18분 | 0~14 |
| 16 | axe-collect | 16분 | 0~15 |
| 17 | axe-classify | 20분 (초과 예상 시 재계획) | 0~16 |
| 18 | featured-projects | 18분 | 0~17 |
| 19 | hero-first-screen | 18분 | 0~18 |
| 20 | section-structure | 18분 | 0~19 |
| 21 | section-layout | 15분 | 0~20 |
| 22 | focus-trap-modal | 16분 | 0~21 |
| 23 | focus-trap-lightbox | 16분 | 0~22 |
| 24 | print-pdf | 15분 | 0~23 |
| 25 | axe-remediation-gate | 17분 | 0~24 |
| (재계획) | axe-remediation-{id} | 그룹당 20분 이하, 생성 조건 충족 시만 | 25 |
| 26 | axe-remediation-recheck | 17분 | 0~25 + 재계획 그룹 |
| 27 | axe-finalize | 15분 | 0~26 |
| 28 | final-verification | 12분 | 0~27 |

## 14. 빌더 재량

- 세부 시각 표현: 선행 문서의 토큰과 accent 제한 안에서 정한다.
- CSS 클래스 구조: 명시된 id, data 속성, 클래스는 유지한다.
- 테스트 helper 분할
