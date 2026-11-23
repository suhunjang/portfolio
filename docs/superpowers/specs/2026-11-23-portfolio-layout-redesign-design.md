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
  - 사용자 결정·콘텐츠·비목표는 바뀌지 않았다.
- Harness 실행 identity (중앙 release, `.harness/harness.lock.json`이 고정)
  - sourceCommit `cb179f99acbb9ad32c5dcebab01ff19df7c3f4ae`
  - manifestHash `287201c44d766b0441470953005450b40f300de2718b246eeb44fd0e3c2f900a`
  - distributionVersion 2.0.0

## 1. 의도

2026-07-29 작업에서 색·서체·여백을 경영자의 절제 톤으로 정리했다. 그때 레이아웃 구조는 범위 밖이었다.

이번 작업은 그 톤을 유지하면서 구조를 다시 짠다. 채용·영입 의사결정자(임원 채용 담당자, 헤드헌터, 대표)가 30초 안에 다음 세 가지를 파악하게 하는 것이 목표다.
1. COO·CTO 포지셔닝
2. 핵심 지표
3. 대표 프로젝트라는 근거

## 2. 목표 / 비목표 / 실패 조건

### 목표
- 1280×800 초기 viewport 안에 이름, tagline, STATS 4개, 대표 프로젝트 3개의 제목을 담는다.
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
- 그라데이션·글로우 같은 장식이 추가된다.

## 3. 현재 코드 사실 (read-first 대상)

### 저장소 지침
- BASE에는 `README.md`만 있다.
- 현재 checkout에는 다음 하네스 파일이 있다.
  - `CLAUDE.md` (중앙 Harness 계약)
  - `.harness/harness.lock.json`, `.harness/policy.json`, `.harness/install-state.json`
  - `.claude/`, `.codex/`, `pytest.ini`, `.python-version`, `.gitattributes`
- Harness 공통 `scripts/`, `templates/`, `harness-manifest.json`은 중앙 store로 옮겨져 저장소에 없다.

### 데이터 (`js/data.js`)
- 전역 const: `PROFILE`, `STATS`(4), `CAREER`, `VIS_ACCENT`, `makeVisual`, `PROJECTS`(13, 모두 `detail` 있음), `STRENGTHS`(6), `SKILLS`
- `PROFILE.tagline`은 BASE에서 렌더링되지 않는다.
- email·phone·social.*은 빈 문자열이다.
- 대표 프로젝트의 원본 index: Motion AD=1, VigoRight (의료 AI/VR)=5, Lost Energy Intel=7

### 렌더링 (`js/main.js`)
- `setText(id, value)`로 텍스트를 채운다.
- data 렌더 대상
  - `#heroStats`
  - `#strengthsGrid`
  - `#timeline` (`.timeline-item` > `.timeline-period` + `.timeline-card`)
  - `#projectGrid`
  - `#skillsGrid`
  - `#contactActions`
- 프로젝트 카드: `article.project-card.has-detail[data-project=idx][tabindex=0][role=button]`

### 모달
- `openProjectModal(idx)`: `lastFocused = document.activeElement`를 저장한 뒤 닫기 버튼에 포커스한다.
- 열기: `#projectGrid`에서 click/keydown 위임
- 닫기: `[data-modal-close]` 또는 Esc. lightbox가 열려 있으면 Esc는 lightbox를 먼저 닫는다.

### lightbox
- `ensureLightbox()`가 처음 호출될 때만 `.lightbox`를 만든다.
- 현재 lightbox에는 Tab을 닫기 버튼에 고정하는 리스너가 있다.
- 모달에는 포커스 트랩이 없다.

### 기타
- 스크롤스파이: id 배열(about, strengths, career, projects, contact) 하드코딩 + IntersectionObserver
- reveal: IntersectionObserver로 `.in`을 붙인다. reduced-motion이면 즉시 붙인다.
- typing: `runTyping`. reduced-motion이면 `roles[0]`으로 고정한다.
- 테마: localStorage `THEME_KEY`. 저장값이 없으면 시스템 설정을 따른다.
- 메뉴: `#menuToggle`, `#navLinks.open`, `aria-expanded`
- 인쇄: `@media print`
- Google Fonts의 Space Grotesk 링크는 제거 금지다. data.js SVG가 이 폰트를 하드코딩한다.

## 4. 접근 방식

| 안 | 내용 | 판단 |
|---|---|---|
| A (선택) | 절제 톤 유지 + 레이아웃·구조 재구성 | Q1에서 선택 |
| B | 시각 방향 전면 교체 | 선행 작업을 되돌림 |
| C | 마감만 다듬기 | 체감 변화가 부족함 |

## 5. 첫 화면과 대표 프로젝트 (Q2, Q3)

### 히어로 DOM 순서
1. `.hero-eyebrow`
2. `h1#heroName`
3. `p.hero-tagline#heroTagline` — 신규, `setText`로 `PROFILE.tagline`을 넣는다.
4. `h2.hero-role` — `#typed` 포함, 보조 크기
5. `#heroSummary`
6. `.hero-cta` — `.btn-primary` 프로젝트 보기, `.btn-ghost` 연락하기
7. `ul#heroStats`
8. `div#heroFeatured`

### 대표 카드 마크업 (phrasing-content 계약)

```
<button type=button class=featured-card data-featured-card data-project={원본 idx}>
  <span class=featured-title>{p.title}</span>
  <span class=featured-blurb>{p.blurb}</span>
</button>
```

- 카드 안에는 `span`과 텍스트만 둔다.
- 다음 요소는 카드 안에 두지 않는다: h1~h6, p, div, ul, ol, li, section, article
- 두 span은 `display: block`으로 표시한다.

### 함수 계약
- `renderFeaturedProjects(): void`
  - 원본 순서대로, `featured === true`인 항목만 렌더링한다.
  - 새 문자열을 하드코딩하지 않는다.
  - 그리드 렌더링 직후에 호출한다.
- `openProjectModal(projectIndex, triggerElement = document.activeElement): void`
  - `lastFocused = triggerElement`로 저장한다.
  - projectGrid에서는 `openProjectModal(idx, card)`로 호출한다.
  - `#heroFeatured`에는 click 위임을 단다.
- `closeProjectModal(): void`
  - 어떤 경로로 닫든 `lastFocused`로 포커스를 복귀한다.

### data.js 변경
- index 1, 5, 7의 `title:` 다음 줄에 `featured: true,`를 넣는다(총 3줄).
- 그 밖의 변경은 금지다.

### 첫 화면 AC (desktop 1280×800, hero.spec.js)
- 대상: `#heroName`, `#heroTagline`, `#heroStats`, `.featured-title` 3개
- 사전 조건: `document.fonts.ready` 완료, `window.scrollY === 0`
- 각 대상은 다음을 모두 만족해야 한다.
  1. `toBeVisible()`
  2. width·height > 0
  3. 대상과 모든 조상의 computed `visibility === visible`, `opacity === 1` (`expect.poll`로 확인)
  4. `x >= 0`, `y >= 0`, `x + width <= 1280`, `y + height <= 800`
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

## 7. 콘텐츠 보존과 예외

### 7.1 기준
- BASE `js/data.js`를 평가한 결과: `BaselineData`
- BASE `index.html`의 정적 본문: `StaticContent`

### 7.2 허용 예외
1. index 1, 5, 7에 `featured: true` 추가
2. `kickers`(DOM 순서)는 다음 둘 중 정확히 하나와 같아야 한다.
   - BASE: [01 — About, 02 — Strengths, 03 — Career, 04 — Projects, 05 — Stack &amp; Contact]
   - FINAL: [01 — Career, 02 — Projects, 03 — Strengths, 04 — About, 05 — Contact]
3. `sectionTitles`(DOM 순서)는 다음 둘 중 하나와 같아야 한다.
   - BASE: [소개, 업무상 강점, 경력 &amp; 창업, 프로젝트 &amp; 제품, 기술 스택 &amp; 연락처]
   - FINAL: [경력 &amp; 창업, 프로젝트 &amp; 제품, 업무상 강점, 소개, 연락처]
   - FINAL이면 `h3.subsection-title` 기술 스택이 정확히 1개 있어야 한다.
4. nav와 섹션의 순서. 비교할 때 `navLabels`는 정렬한다.
5. skill-group 제목의 heading level
6. axe remediation 그룹 step(§8.3)에서 위반 대상 요소에 한해 aria-*, role, alt, lang, tabindex, for 속성 변경. 텍스트는 바꾸지 않는다.

### 7.3 helper 계약 (`tests/helpers/content.js`)
- `norm(s) = String(s).replace(/\s+/g, ' ').trim()`
- `BaselineData`
  - `{ PROFILE, STATS, CAREER, VIS_ACCENT, PROJECTS, STRENGTHS, SKILLS }`
  - JSON 형태이고 배열은 원본 순서를 유지한다.
  - deep-equal로 비교한다.
- `StaticContent` (모든 값에 norm 적용)
  - `title`, `metaDescription`
  - `navLabels` (sort)
  - `heroEyebrow`
  - `ctaLabels`, `kickers`, `sectionTitles`, `sectionSubs` (DOM 순서)
  - `aboutParagraphs` (`.about-text p:not([id])`)
  - `aboutPoints`, `aboutMetaTerms`
  - `contactHeading`, `contactText`
  - `footerNote`, `footerTop`
- 함수
  - `readLiveData(page): Promise<BaselineData>`
  - `normalizeFeatured(data): BaselineData` — 입력을 바꾸지 않는다(structuredClone). featured는 지정 index에만 허용한다.
  - `extractStatic(page): Promise<StaticContent>`

## 8. 접근성

### 8.1 axe
- 기준: wcag2a·wcag2aa의 serious/critical 위반 0건
- 시나리오 10개
  - page: 3 viewport × 2 테마 = 6
  - 모달 열림: dark, light
  - lightbox 열림: dark, light

### 8.2 포커스 트랩 (step 11)

`trapFocus(container, options?: { returnFocusTo?: HTMLElement }): () => void`
- trap은 스택으로 관리한다. 최상위 trap만 Tab 순환을 처리한다.
- `release()`
  - 스택에서 제거하고, returnFocusTo로 포커스를 옮긴 뒤, 직전 trap을 재개한다.
  - 여러 번 호출해도 안전하다.
- 모달: 열 때 push(returnFocusTo = trigger), 닫을 때 release
- lightbox: 열 때 push(returnFocusTo = `.shot-zoom`). 이 동안 모달 trap은 일시정지되고, lightbox를 닫으면 재개된다.
- 기존 Tab 고정 리스너는 제거한다.
- `:focus-visible` outline을 유지한다.
- h1은 1개만 두고, heading level을 건너뛰지 않는다.

### 8.3 axe 기준선, 식별, 해소

#### canonical target 식별 (step 5)

`selectors`는 정보로만 기록하고, 비교에는 아래 canonical key를 쓴다.

```
canonicalTarget = {ruleId}::{anchor}::{textSig}
```

anchor: 요소 자신부터 조상 방향으로 처음 만나는 것을 쓴다.
1. `[data-featured-card][data-project]` → `featured:{N}`
2. `[data-project]` → `project:{N}`
3. `[id]` → `#{id}`
4. landmark(header, nav, main, footer) → 태그명
5. 위에 해당하지 않으면 `document`

textSig
- `norm(textContent)`를 쓴다. 비어 있으면 aria-label, alt, title, src 파일명 순으로 대체한다.
- 숫자는 `#`으로 바꾼다.
- 80자까지만 쓴다.
- 고정 alias를 적용한다. 이 표는 설계에 고정된 것이고 실행 중에 추가하지 않는다.
  - `## — Stack & Contact` → `## — Contact`
  - `기술 스택 & 연락처` → `연락처`

태그명·클래스·DOM 경로·섹션 순서·kicker 번호가 바뀌어도 key는 그대로다. 같은 key는 하나로 합친다.

#### helper 구성 (`tests/helpers/axe.js`)
- step 5: `canonicalTargetInPage`, `canonicalFromDescriptor`, `ALIASES`, `runAxe(page, { include })` → `{ ruleId, impact, selectors, targets }[]`
- step 6: `COLLECT_DIR`, `EXPECTED_FILES`(10), `writeCollected`, `mergeCollected`, `baselineExists`, `loadBaseline`, `validateBaseline`, `checkRegression`, `validateRemediationPlan`
- step 6 CLI
  - `--reset`
  - `--merge [out]` (기본 out: `tests/fixtures/axe-collected.json`)
  - `--assert-empty [path]`
  - `--check-plan [--coverage]`

#### fixture

`tests/fixtures/axe-collected.json`
- step 7의 병합 수집 결과다. tracked이며 정보용이다.

`tests/fixtures/axe-baseline.json` (step 8)
- 항목 필드
  - `key`: `{scenario}:{project}:{ruleId}`
  - `scenario`, `project`, `ruleId`, `impact`
  - `targets`: canonical key
  - `selectors`
  - `fixes`: `[{ target, fixKind, fixFiles }]`. target마다 1개
  - `fixFiles`: fixes의 합집합
- fixKind와 수정 파일
  - css-token: `css/themes.css`
  - css-rule: `css/style.css`
  - js-render: `js/main.js`
  - static-markup: `index.html`
  - text-change: 빈 배열

`tests/fixtures/axe-remediation-plan.json` (step 8)
- 형식: `{ groups: [{ id, targets: canonical[], fixFiles: string[], difficulty: low|medium|high, estMinutes: number, blocked: boolean, reason }] }`
- `validateRemediationPlan(plan, baseline)` 규칙
  - 그룹 target은 baseline target의 부분집합이고 중복이 없다.
  - 그룹 `fixFiles`는 해당 target fixFiles의 합집합이다.
  - `estMinutes`는 20 이하다.
  - text-change가 있으면 `blocked`는 true다.
  - `--coverage`를 주면 모든 baseline target이 정확히 한 그룹에 속해야 한다.

#### 실행 모드

수집 모드 (`AXE_COLLECT=1`)
- 실제 fixture를 로드하지 않고 `writeCollected`만 한다.
- 명령은 항상 `npm --prefix tests test -- axe.spec.js axe-helper.spec.js`로 실행한다. 합성 helper 검증을 함께 돌리기 위해서다.

일반 모드
- baseline이 있으면 `checkRegression`과 `validateBaseline`을 실행한다.
- plan이 있으면 `validateRemediationPlan`도 실행한다.
- baseline이 없으면 시나리오 회귀 테스트를 skip한다. 이 경우는 step 7 수집 단계에만 해당한다.
- step 8 이후에는 read-first에서 fixture가 있는지 확인한다. step 14·15의 `--assert-empty`도 파일이 있어야 통과한다.

#### 단계

step 7: 10개 시나리오를 구현하고, 수집 디렉터리를 초기화한 뒤 수집한다. 10개 파일을 검증한 다음 `axe-collected.json`으로 병합한다.

step 8: 분류
1. 수집 결과를 (ruleId, 추정 출처 파일)별 target 묶음으로 나눈다.
2. 묶음별 예상 시간 = 2분 + target 수 × 1분
3. 전체 시간 = 묶음 합계 + 검증 5분
4. 전체가 20분을 넘으면 분류하지 않고 즉시 중단한 뒤 보고한다. Harness 재계획에서 묶음별 분류 step으로 나눈다.
5. 20분 이내이면 실제 CSS·렌더 출처를 조사해 baseline과 remediation plan을 확정한다.

회귀 판정 (step 7~12)
- 새 key나 새 canonical target이 나오면 실패다.
- 기존에 있던 것이 사라지는 것은 허용한다.
- 새 target을 baseline에 자동으로 넣는 것은 금지다.
- 새 target이 그 step의 마크업 때문에 생긴 실제 신규 위반이면, 그 step의 허용 파일 안에서 고친다.
- 식별이 보존되지 않아 생긴 것이면 중단하고 재계획을 요청한다.

step 13: remediation gate
1. 현재 상태를 다시 수집해 `tests/.tmp/axe-current.json`에 둔다.
2. plan에서 사라진 target을 제거하고, 비게 된 그룹을 삭제한다. 새 항목은 추가하지 않는다.
3. 남은 그룹이 있으면 Harness가 재계획한다.
   - 각 그룹마다 `axe-remediation-{id}` step을 step 13과 14 사이에 만든다.
   - allowedPaths는 그 그룹의 `fixFiles`로 정확히 제한한다.
   - 각 step은 20분 이하다.
   - AC는 그 그룹의 target이 사라지는 것이다.
   - blocked 그룹은 담당 구현 step(9 또는 10)을 다시 연다.

이 설계에는 allowedPaths가 정해지지 않은 remediation step을 두지 않는다.

step 14: finalize
- 전제 조건: plan의 groups가 `[]`이다. 아니면 중단한다.
- 이 step에서만 `axe-baseline.json`을 `[]`로 바꾼다.
- AC: `--assert-empty`와 일반 axe 전체 테스트 통과

## 9. 반응형

| 대상 | 375 | 768 | 1280 |
|---|---|---|---|
| `#heroStats` | 2×2 | 4열 1행 | 4열 1행 |
| `#heroFeatured` | 1열 | 2열 | 3열 |
| `#projectGrid` | 1열 | 2열 | 3열 |
| `#strengthsGrid` | 1열 | 2열 | 3열 |
| Career `.timeline-item` | 세로 | 가로 (top 차이 < 24px) | 가로 |

가로 스크롤이 생기면 안 된다.

## 10. 인쇄와 PDF

- 히어로, 대표 카드, 본문은 visible이고 opacity 1이다.
- 보이는 `.reveal`은 내용이 비어 있지 않다.
- 토글, 메뉴, scroll-hint, `#projectModal`은 display none이다.
- 시나리오 A (새 페이지): `.lightbox`가 없거나, 있으면 display none이다.
- 시나리오 B (overlay 열림): screen 상태에서 `.lightbox`가 존재하고 visible인지 먼저 확인한다. 그다음 print 상태에서 `.lightbox`와 `#projectModal`이 display none인지 확인한다.
- PDF 검사 (두 시나리오 모두)
  - 10240바이트를 넘어야 한다.
  - page 객체 수가 1 이상이어야 한다.
  - page 객체 수는 `buf.toString('latin1').match(/\/Type\s*\/Page\b/g)`로 센다. `\b` 때문에 `/Pages` 트리 노드는 세지 않는다.
  - PDF 파서 의존성은 추가하지 않는다.

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

Harness의 managed·policy·lock·state 파일은 tracked source와 runtime 경로 어디에도 포함하지 않는다.

`tests/.gitignore`는 다음 7줄을 이 순서로 담는다. 마지막 개행만 정규화하고 나머지는 정확히 일치해야 한다.

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
- 테마 fixture는 `THEME_KEY`가 null일 때만 테마를 주입한다.
- 최초 방문 검사는 fixture를 쓰지 않는 별도 context에서 한다.
- 스크롤스파이는 `toHaveClass(/active/)` 재시도 assertion으로 확인한다.

`collectConsoleErrors(page): ErrorCollector`

```
type ErrorRecord = { kind: 'pageerror' | 'console.error', message: string, url: string | null, line: number | null, column: number | null }
type ErrorCollector = { finish(): Promise<{ pageErrors: ErrorRecord[], consoleErrors: ErrorRecord[] }> }
```

- 호출하는 즉시 listener를 등록한다.
- pageerror는 전부 기록한다. url, line, column은 null이다.
- console은 type이 error인 것만 기록하고, `location()`에서 url, line, column을 가져온다.
- 제외 조건: location url의 hostname이 정확히 `fonts.googleapis.com` 또는 `fonts.gstatic.com`일 때만 제외한다. URL 파싱에 실패하면 제외하지 않는다.
- `finish()`는 networkidle을 기다린 뒤 수집 결과의 사본을 반환한다.
- 사용 순서 (고정): collect → goto → 동작 → finish → 두 배열이 `[]`인지 확인

### 11.5 범위 검사 (`tests/scripts/verify-scope.mjs`)

#### 경로 정책 (step 1)

rename 처리
- 모든 Git 경로 수집에 `--no-renames`를 쓴다.
- 이동은 삭제 경로와 추가 경로로 나뉘어 잡힌다. 금지 경로에서 옮겨 온 rename은 원래 경로 쪽에서 위반이 된다.
- 인자는 상수로 export한다: `GIT_DIFF_PATH_ARGS = ['--no-renames', '--name-only']`
- 적용 대상
  - committed: `git diff --no-renames --name-only BASE HEAD`
  - index: `git diff --cached --no-renames --name-only BASE`
  - worktree: `git diff --no-renames --name-only BASE` + untracked
  - uncommittedHarness용 diff(HEAD 기준 cached·worktree)
  - data.js diff 4종

경로 분류
- 빌더 허용 경로: §11.1의 tracked source
- 하네스 소유 경로
  - 목록: `CLAUDE.md`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`, `.claude/**`, `.codex/**`, `.harness/harness.lock.json`, `.harness/policy.json`, 이 설계 문서, 레거시 `scripts/**`, `templates/**`, `harness-manifest.json`
  - committed 층에서는 면제한다.
  - 커밋되지 않은 변경은 위반이다.
- 하네스 런타임 경로 (면제): 위 두 파일을 제외한 `.harness/**`, `.venv/**`, `phases/HOO-81-portfolio-redesign/**`
- runtime 경로가 추적되면 위반이다.
- 루트 package.json이 있으면 위반이다.

#### 내용 판정 (step 2)
- data.js 4구간: 삭제 줄 0개, `featured: true,` 줄만 3줄 이하. final이면 정확히 3줄.
- index.html 3종: 모두 `Space+Grotesk`를 포함해야 한다.
- `tests/.gitignore` index·worktree: §11.1 규칙을 만족해야 한다.

### 11.6 통합 AC
- step 1 이후: `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`
- step 14·15: 위에 `sh tests/scripts/with-env.sh node tests/helpers/axe.js --assert-empty`를 추가한다.
- step 15: `verify-scope -- --final`을 추가한다.

## 12. 변경 허용 경로와 운영 경계

- index.json allowedPaths: `index.html`, `css/style.css`, `css/themes.css`, `js/main.js`, `js/data.js`, `tests/`
  - Harness managed·policy·lock·state 파일은 넣지 않는다.
- 각 step에 tracked source 허용 파일과 runtime 쓰기 경로를 명시한다.
- `index.html`
  - 구조 변경: step 9·10
  - 속성 변경: 재계획으로 추가되는 remediation 그룹 step에서만
- `css/themes.css`: remediation 그룹 step에서만

명령 권한
- 빌더와 검증 스크립트 모두 허용: Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)
- 하네스만 실행
  - Git 상태 변경 명령(checkout, switch, add, commit, push, reset, stash, merge, rebase, tag 등)
  - Harness 운영 명령(`harness --project-root . check`, `plan-session`, `review-plan`, `approval`, `runner`)

빌더 수정 금지
- `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`

## 13. Step 목록 (각 20분 이하, 검증·디버깅 포함)

| # | name | 예상 | 선행 |
|---|---|---|---|
| 0 | tests-env-setup | 14분 | 없음 |
| 1 | scope-paths | 18분 | 0 |
| 2 | scope-content | 18분 | 0~1 |
| 3 | content-baseline-fixture | 20분 | 0~2 |
| 4 | interaction-regression | 18분 | 0~3 |
| 5 | axe-canonical | 18분 | 0~4 |
| 6 | axe-baseline-tooling | 20분 | 0~5 |
| 7 | axe-collect | 15분 | 0~6 |
| 8 | axe-classify | 20분 (초과 예상 시 재계획) | 0~7 |
| 9 | hero-featured | 20분 | 0~8 |
| 10 | section-order-layout | 20분 | 0~9 |
| 11 | focus-trap | 18분 | 0~10 |
| 12 | print-pdf | 15분 | 0~11 |
| 13 | axe-remediation-gate | 12분 | 0~12 |
| (재계획) | axe-remediation-{group} | 그룹당 20분 이하 | 13 |
| 14 | axe-finalize | 10분 | 0~13 + 재계획 그룹 |
| 15 | final-verification | 12분 | 0~14 |

## 14. 빌더 재량

- 세부 시각 표현: 선행 문서의 토큰과 accent 제한 안에서
- CSS 클래스 구조: 명시된 id, data 속성, 클래스는 유지한다.
- 테스트 helper 분할
