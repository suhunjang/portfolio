# 포트폴리오 레이아웃·구조 리디자인 설계 (HOO-81)

- 날짜: 2026-11-23 (범위 변경 반영 2026-11-24) / 브랜치: `feat/HOO-81/portfolio-redesign` (base `main`)
- BASE: `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`
- 선행 시각 설계: `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md` (적용 완료, 계속 유효)
- 합의: Q1 Discord 1574196542901059632, Q2 1574197289084387379, Q3~Q5 1574197696334405756 (추천안 일괄 확정)
- 범위 변경: 대표 결정 `scope-change-claude-design-v27`·`scope-change-claude-design-v28-compact` — Claude Design 패턴(레이아웃·컴포넌트·간격·타이포 위계만)을 구현 기준으로 추가. 이전 Harness 2.0.1 계획·리뷰·승인은 범위 변경으로 재사용하지 않는다.
- 리뷰 반영 이력: 1~30차(Astra `1432c5274b33` ~ `review-resume-h201-b86b75bb881e-v26`)의 모든 지적은 이 문서에 반영되어 있다(세부 목록은 Git 이력의 이전 설계 문서). 30차까지의 핵심: strict snapshot schema·token scanner, 경로 유형·projectRoot 검사, 저장소 상대 경로 계약, after.z fail-closed, trusted-agent 실행 전제, S·C·JS status parser 동일 엄격 계약(`bad git status`).
- 31차 `scope-change-claude-design-v27/v28`: Claude Design intake·guard step 추가(step 12·13), hero 2열·component state 단계 분할(step 36·39), 기존 step 12 이후 번호 재배정(+2, hero-first-screen 이후 +3, section-structure 이후 +4), step 0~11 재검증 모드, fresh runner preflight 추가. 기존 콘텐츠·FINAL 정보구조·대표 프로젝트 3개·PROJECTS 13개와 순서는 그대로.
- Harness 실행 identity (중앙 release, `.harness/harness.lock.json`을 직접 읽어 확인): sourceCommit `e7a03919a460f975149f7c55343ca4b34d3d2352`, manifestHash `b627e6a5ce4a903c24c400927ca2b49a14d0bd59632c691b2a5c2d74c6c08372`, distributionVersion 2.0.1
- 진행 순서: materialize → 새 plan commit → Astra `gpt-6-astra` 계획 리뷰 CLEAN → 대표 exact 승인 → §17 preflight → fresh runner(step 0~46) → 전체 테스트 → exact-commit Astra 리뷰 CLEAN → feature push → OPEN PR. merge·deploy·main 직접 변경 없음.

## 1. 의도

2026-07-29 작업에서 색·서체·여백을 경영자의 절제 톤으로 정리했다. 이번 작업은 그 톤(색·서체·문구·수치)을 유지한 채 구조와 레이아웃을 다시 짠다. 레이아웃·컴포넌트·간격·타이포 위계의 기준은 Claude Design으로 생성한 패턴 보드(§16)다. 채용·영입 의사결정자가 30초 안에 (1) COO·CTO 포지셔닝, (2) 핵심 지표, (3) 대표 프로젝트 근거를 파악하게 한다.

## 2. 목표 / 비목표 / 실패 조건

- 목표: 1280×800 첫 화면에 이름·tagline·STATS 4개·대표 프로젝트 제목 3개. FINAL 섹션 순서(hero → Career → Projects → Strengths → About → Contact). §16 허용 패턴(desktop 2열 좌측 정렬 hero, mobile 1열, 섹션 간격, card gap, component state, 44px hit target, 타이포 위계, line clamp). 기능·콘텐츠 보존과 §16 제외 범위를 자동 테스트·범위 검사로 증명.
- 비목표: 색·서체 재설계, 빌드 도구 도입, 신규 기능, 배포·merge·main 직접 변경.
- 실패 조건(동작해도 실패): §7 예외 밖의 문구·수치·경력 사실 변경/생성, 빈 email·phone·social 채우기, 기존 기능 회귀, axe serious/critical 잔존, §16.3 제외 항목 반영(새 색·색상 역할 변경·서체 asset/weight 변경·새 문구·수치·섹션·이미지·아이콘·프로젝트 순서·정보구조 변경·placeholder 실콘텐츠화), 그라데이션·글로우 장식 추가.

## 3. 현재 코드 사실 (read-first 대상)

- 저장소 지침: BASE에는 `README.md`만 있다. 현재 checkout의 하네스 파일은 `CLAUDE.md`, `.harness/harness.lock.json`, `.harness/policy.json`, `.harness/install-state.json`, `.claude/`, `.codex/`, `pytest.ini`, `.python-version`, `.gitattributes`. `.venv/`는 하네스 venv(루트 `.gitignore` 대상).
- HEAD에는 기존 step 0~11 구현 commit(`tests/scripts/with-env.sh`, `start-snapshot.py`, `scope-snapshot.mjs`, `tests/helpers/synthetic-repo.js`, scope-snapshot spec들, `tests/package.json`·lock·`.gitignore`·`playwright.config.js`·`bootstrap.spec.js`)이 있다. 커밋된 `tests/scripts/start-snapshot.py`의 `HARNESS`는 2.0.0 identity이므로 step 0 재검증에서 §11.7 S 블록(2.0.1)과 바이트가 다르다. worktree의 untracked `tests/helpers/theme.js`, `tests/specs/smoke.spec.js`는 이전 blocked 실행 산출물이며 승인된 구현이 아니다(§17에서 제거). `tests/.tmp/`에는 이전 실행의 `start-snapshot-step0~12.json`·`-after.z`가 남아 있다(§17).
- `js/data.js`: 전역 const `PROFILE`, `STATS`(4), `CAREER`, `VIS_ACCENT`, `makeVisual`, `PROJECTS`(13, 모두 `detail`), `STRENGTHS`(6), `SKILLS`. `PROFILE.tagline`은 BASE에서 렌더링되지 않는다. email·phone·social.*은 빈 문자열. 대표 프로젝트 index: Motion AD=1, VigoRight(의료 AI/VR)=5, Lost Energy Intel=7.
- `index.html` hero: `section.hero#hero` > `div.container.hero-inner` > (`p.hero-eyebrow`, `h1.hero-name#heroName`, `h2.hero-role`, `p.hero-summary#heroSummary`, `div.hero-cta`, `ul.hero-stats#heroStats`) + `a.scroll-hint`(hero-inner 밖). 테마 토글 `#themeToggle.theme-toggle`. strengths 카드 `.strength-card`(BASE `css/style.css`에 장식 `.strength-card::before` 규칙).
- `js/main.js`: `setText(id, value)`. 렌더 대상 `#heroStats`(STATS 항목마다 지표 item, item 안에 수치와 label), `#strengthsGrid`, `#timeline`(`.timeline-item` > `.timeline-period` + `.timeline-card`), `#projectGrid`, `#skillsGrid`, `#contactActions`. 카드: `article.project-card.has-detail[data-project=idx][tabindex=0][role=button]`.
- 모달: `div.modal#projectModal[hidden]` > `.modal-backdrop[data-modal-close]` + `.modal-dialog` > (`button.modal-close[data-modal-close]` + `div.modal-body#modalBody`). `#modalBody` 렌더: `.modal-visual`/`.modal-thumb`, `h3#modalTitle.modal-title`, `.modal-meta`, `p.modal-blurb`, `.modal-section`(갤러리 `.shot-zoom` 포함). `openProjectModal(idx)`는 `lastFocused = document.activeElement` 후 닫기 버튼 포커스, body `modal-open`. 열기 `#projectGrid` click/keydown 위임, 닫기 `[data-modal-close]` 또는 Esc(lightbox 우선).
- lightbox: `ensureLightbox()`가 `.lightbox[role=dialog]`(`button.modal-close` + `img`)를 만들고 `.shot-zoom`으로 연다. lightbox에만 Tab 고정 리스너가 있다.
- 기타: 스크롤스파이 id 배열(about, strengths, career, projects, contact) + IntersectionObserver. reveal `.reveal`→`.in`(reduced-motion 즉시). typing `runTyping`(reduced-motion이면 `roles[0]`). 테마 localStorage `THEME_KEY`. 메뉴 `#menuToggle`, `#navLinks.open`, `aria-expanded`. `@media print`. Google Fonts Space Grotesk 링크 제거 금지.

## 4. 접근 방식

A(선택, Q1): 절제 톤 유지 + 레이아웃·구조 재구성. 레이아웃·컴포넌트·간격·타이포 위계는 §16 Claude Design 패턴 중 허용 항목만 적용한다.

## 5. 첫 화면과 대표 프로젝트 (Q2, Q3)

히어로 DOM 순서(`.hero-inner`의 직계 자식, 정확히 8개): 1 `.hero-eyebrow` → 2 `h1#heroName` → 3 `p.hero-tagline#heroTagline`(신규, 정확히 `setText('heroTagline', PROFILE.tagline)`) → 4 `h2.hero-role`(`#typed`) → 5 `#heroSummary` → 6 `.hero-cta` → 7 `ul#heroStats` → 8 대표 프로젝트 컨테이너. 컨테이너 마크업은 정확히:

```
<div id="heroFeatured" role="region" aria-label="대표 프로젝트"></div>
```

대표 카드 (phrasing-content 계약):

```
<button type="button" class="featured-card" data-featured-card data-project="{원본 idx}">
  <span class="featured-title">{p.title}</span>
  <span class="featured-blurb">{p.blurb}</span>
</button>
```

- 카드 안에는 span과 텍스트만(h1~h6, p, div, ul, ol, li, section, article 금지). 두 span은 `display: block`.
- 대표 카드와 grid 카드는 같은 `data-project`. 테스트 helper는 grid 카드를 `#projectGrid .project-card[data-project="N"]`로 한정한다.
- 함수: `renderFeaturedProjects(): void`(원본 순서로 `featured === true`만, 새 문자열 하드코딩 금지, 그리드 렌더 직후 호출). `openProjectModal(projectIndex, triggerElement = document.activeElement)`(`lastFocused = triggerElement`, grid는 `(idx, card)`, `#heroFeatured` click 위임). `closeProjectModal()`은 모든 경로에서 `lastFocused`로 복귀.
- data.js: index 1, 5, 7의 `title:` 다음 줄에 `featured: true,` 총 3줄. 그 밖 변경 금지.
- 대표 카드의 색·테두리·배경은 새 색 선언 없이 기존 카드 규칙의 선택자 목록에 `.featured-card`를 추가하는 방식으로만 얻는다(§16.4 guard).

첫 화면 AC (desktop 1280×800, hero.spec.js 단독·통합 모두):
- 사전 조건: `document.fonts.ready` 완료, `scrollY === 0`.
- 대상: `#heroName`, `#heroTagline`, `#heroStats`, `.featured-title` 3개, 지표 item 4개(DOM 순서 = `STATS[0..3]`)마다 item·수치 요소(텍스트 norm = STATS 수치)·label 요소(텍스트 norm = STATS label). 셀렉터는 hero.spec.js 상단 상수 `STAT_ITEM`, `STAT_VALUE`, `STAT_LABEL`(read-first에서 main.js 렌더 코드로 확정).
- 각 대상: `toBeVisible()`, bbox w·h > 0, 자신과 모든 조상의 computed visibility `visible`·opacity `1`(`expect.poll`), x ≥ 0, y ≥ 0, x+w ≤ 1280, y+h ≤ 800.

## 6. 섹션 구조 (Q4, FINAL)

| 순서 | id | class | kicker | heading |
|---|---|---|---|---|
| 1 | hero | hero | 없음 | h1 `#heroName` |
| 2 | career | section | `01 — Career` | h2 경력 &amp; 창업 |
| 3 | projects | section section-alt | `02 — Projects` | h2 프로젝트 &amp; 제품 |
| 4 | strengths | section | `03 — Strengths` | h2 업무상 강점 (section-sub 유지) |
| 5 | about | section section-alt | `04 — About` | h2 소개 |
| 6 | contact | section | `05 — Contact` | h2 연락처 |

- about: 본문 뒤 `h3.subsection-title` 기술 스택 + `#skillsGrid`(skill-group 제목 h4). contact: `.contact-card`, h3 함께 만들어요 유지.
- nav: Career, Projects, Strengths, About, Contact. 스크롤스파이 배열: career, projects, strengths, about, contact. `.scroll-hint` href `#career`.
- 스크롤스파이 테스트 문법(정확히): `const link = page.locator('.nav-link[href="#projects"]'); await link.click(); await expect(link).toHaveClass(/active/);` (about도 같은 형식)
- PROJECTS 13개는 `#projectGrid`에 data.js 순서 그대로 모두 렌더링한다(Explore surface).

## 7. 콘텐츠 보존과 예외

### 7.1 기준
- `BaselineData`: BASE data.js 평가 결과(step 17). `StaticContent`: BASE index.html 정적 본문(step 18).

### 7.2 허용 예외
1. index 1, 5, 7의 `featured: true`
2. `kickers`(DOM 순서)는 BASE [01 — About, 02 — Strengths, 03 — Career, 04 — Projects, 05 — Stack &amp; Contact] 또는 FINAL [01 — Career, 02 — Projects, 03 — Strengths, 04 — About, 05 — Contact] 중 정확히 하나
3. `sectionTitles`는 BASE [소개, 업무상 강점, 경력 &amp; 창업, 프로젝트 &amp; 제품, 기술 스택 &amp; 연락처] 또는 FINAL [경력 &amp; 창업, 프로젝트 &amp; 제품, 업무상 강점, 소개, 연락처]. FINAL이면 `h3.subsection-title` 기술 스택 정확히 1개
4. nav·섹션 순서(`navLabels`는 정렬 비교)
5. skill-group 제목 heading level
6. axe remediation 그룹 step에서 위반 요소의 aria-*, role, alt, lang, tabindex, for 속성 변경(텍스트 불변)
- 이 밖의 콘텐츠 변경은 허용하지 않는다.

### 7.3 helper 계약 (`tests/helpers/content.js`)
- `norm(s) = String(s).replace(/\s+/g, ' ').trim()`
- `BaselineData = { PROFILE, STATS, CAREER, VIS_ACCENT, PROJECTS, STRENGTHS, SKILLS }` (JSON, 순서 유지, deep-equal)
- `StaticContent` (모두 norm): `title`, `metaDescription`, `navLabels`(정렬), `heroEyebrow`, `ctaLabels`, `kickers`, `sectionTitles`, `sectionSubs`, `aboutParagraphs`(`.about-text p:not([id])`), `aboutPoints`, `aboutMetaTerms`, `contactHeading`, `contactText`, `footerNote`, `footerTop`
- step 17: `readLiveData(page)`, `normalizeFeatured(data)`. step 18: `extractStatic(page)`

### 7.4 회귀 spec (step 19, 20)
- step 19 `modal-regression.spec.js` + `tests/helpers/modal.js`. step 20 `ui-regression.spec.js` + `first-visit.spec.js`.
- `modal.js`: `GRID_CARD = '#projectGrid .project-card'`; `gridCard(page, N)` = 정확히 `page.locator('#projectGrid .project-card[data-project="' + N + '"]')`; `openFirstProjectByClick`, `openFirstProjectByEnter`; `closeVia(page, 'button'|'backdrop'|'esc')`(button `#projectModal .modal-close[data-modal-close]`, backdrop `{x:5, y:5}`); `expectFocused`; `modalTitle(page)` = `page.locator('#projectModal #modalTitle')`; `findProjectWithShots(page): number|null`(grid 카드만 DOM 순서로 열고 `.shot-zoom` 확인 후 `closeVia('button')`, 첫 N 또는 null).

## 8. 접근성

### 8.1 axe
- wcag2a·wcag2aa serious/critical 0건. 시나리오 10개: page 3 viewport × 2 테마, modal × dark/light, lightbox × dark/light. 수집·일반 모드 모두 `prepareForAxe` 통과 후에만 실행.

### 8.2 포커스 트랩 (step 40, 41)
- `trapFocus(container, { returnFocusTo? }): () => void` — 스택, 최상위만 Tab 순환, document Tab 핸들러 1개. `release()`는 스택 제거·returnFocusTo 포커스·직전 trap 재개, 다중 호출 안전.
- step 40: 구현 + 모달 열 때 push(trigger)/닫을 때 release. lightbox 코드는 건드리지 않는다.
- step 41: lightbox 열 때 push(`.shot-zoom`), 열린 동안 모달 trap 일시정지, 닫히면 재개, 기존 lightbox Tab 리스너 제거, `:focus-visible` outline 유지·검증.
- h1은 1개, heading level을 건너뛰지 않는다.

### 8.3 axe 기준선·식별·해소

canonical target (step 21): `{ruleId}::{anchor}::{textSig}`. selectors는 정보용.
- anchor(자신부터 조상으로 처음): `[data-featured-card][data-project]`→`featured:{N}`, `[data-project]`→`project:{N}`, `[id]`→`#{id}`, landmark(header/nav/main/footer)→태그명, 없으면 `document`.
- textSig: norm(textContent), 비면 aria-label→alt→title→src 파일명. 숫자는 `#`, 80자 자름. 고정 alias: `## — Stack & Contact`→`## — Contact`, `기술 스택 & 연락처`→`연락처`.
- anchor와 대상의 조상 관계가 유지될 때만 같은 key를 보장한다.

entry key (step 25, 이후 공통): `makeEntryKey({ scenario, project, ruleId })` = `${scenario}:${project}:${ruleId}`(빈 값·`:` 포함 시 throw). (scenario, project, ruleId)마다 entry 1개, targets·selectors 중복 제거·오름차순. (key, target) 쌍이 위반 1건.

helper (`tests/helpers/axe.js`):
- step 21: `ALIASES`, `canonicalTargetInPage(el) → { anchor, text }`, `canonicalFromDescriptor({ ruleId, anchor, text })`, `runAxe(page, { include }) → Violation[]` (`{ ruleId, impact, selectors, targets }`)
- step 25: `makeEntryKey`; `COLLECT_DIR`(`tests/.tmp/axe-collected`); `EXPECTED_FILES` 10개(`page-{mobile,tablet,desktop}-{dark,light}.json`, `modal-desktop-{dark,light}.json`, `lightbox-desktop-{dark,light}.json`); `resolveCollectDir(opts)`(opts.collectDir → `AXE_COLLECT_DIR` → COLLECT_DIR, `tests/.tmp/` 밖이면 `Error('collectDir must be under tests/.tmp')`); `resetCollected`; `writeCollected(scenario, project, violations, opts)`; `mergeCollected({ collectDir, out })`(구성 불일치 `Error('collected files mismatch: missing=[...] extra=[...]')`, out 기본 `tests/fixtures/axe-collected.json`, `MergedEntry = { key, scenario, project, ruleId, impact, targets, selectors }`). CLI `--reset [--dir]`, `--merge [--dir] [--out]`, throw면 stderr + exit 1.
- step 26: `BASELINE_PATH`, `COLLECTED_PATH`, `PLAN_PATH`(`tests/fixtures/axe-{baseline,collected,remediation-plan}.json`); `FIX_FILES_BY_KIND` = css-token `[css/themes.css]`, css-rule `[css/style.css]`, js-render `[js/main.js]`, static-markup `[index.html]`, text-change `[]`; `baselineExists`; `loadBaseline`; `resolveBaselineMode({ path, collectedPath, planPath }) → 'check' | 'pending'`(baseline 있음 `check`; baseline 없음+collected 있음+plan 없음 `pending`; 그 밖 `Error('axe baseline missing: tests/fixtures/axe-baseline.json')`, 환경변수 우회 없음); `validateBaseline`; `checkRegression(violations, baseline, scenario, project)`(`new-key:{key}`, `new-target:{key}:{target}`); `assertEmptyFile`; CLI `--assert-empty [path]`.
- step 27: `PROJECTION_FIELDS`; `projectEntry`; `compareCollectedBaseline(collected, baseline) → { ok, missingEntries, extraEntries, missingTargets, extraTargets, fieldMismatches }`; CLI `--check-baseline-match [--collected] [--baseline]`.
- step 28: `GROUP_ID_RE = /^[a-z0-9]+(?:-[a-z0-9]+)*$/`; `loadPlan`; `validateRemediationPlan(plan, baseline, { coverage, requireEmpty })`; CLI `--check-plan [--coverage] [--require-empty] [--plan] [--baseline]`.
- step 29: `validateRemediationExecutable(plan, baseline)`(`blocked-group:{id}`, `text-change:{id}:{target}`, `empty-fixfiles:{id}`); CLI `--check-executable`(실패 시 첫 줄 `Harness 재계획 필요: 실행 불가 remediation 그룹`, exit 1).
- step 30 (`--collected` 기본 `tests/.tmp/axe-current.json`): `checkGroupDone`, `checkCollectedCoverage`, `countCollectedTargets`; CLI `--check-group-done <id>`, `--check-coverage`, `--assert-no-violations`.
- step 31: `checkCollectedRegression(collected, baseline)`(`bad-key:`, `new-key:`, `new-target:`); `prunePlan`(순수, 사라진 target 제거·빈 그룹 삭제·fixFiles 부분집합, 추가 없음); CLI `--check-regression`, `--prune-plan`(회귀 실패 시 쓰지 않고 exit 1, 통과 시 `JSON.stringify(plan, null, 2) + '\n'`).

fixture: `axe-collected.json`(step 32), `axe-baseline.json`·`axe-remediation-plan.json`(step 33; plan `{ groups: [{ id, targets, fixFiles, difficulty, estMinutes: 1~20, blocked, reason }] }`).

색 변경 제외(§16.3): 위반 해소에 색 값 또는 색 역할 변경이 필요한 target(css-token 및 색 선언을 바꾸는 css-rule)은 step 33에서 `blocked: true`, reason `color change excluded (HOO-81 §16.3)`로 기록한다. 그러면 `--check-executable`이 실패해 remediation step을 만들지 않고 대표 결정·재계획으로 넘긴다.

실행 모드:
- 공통: `prepareForAxe(page, { scenario })` 후 `runAxe(page, { include })`.
- 수집(`AXE_COLLECT=1`): `writeCollected`만.
- 일반: `resolveBaselineMode()`. `check`면 checkRegression·validateBaseline(desktop-dark 1회)·plan 있으면 validateRemediationPlan(coverage false). `pending`이면 준비까지만 하고 `test.skip(true, 'axe classification pending (step 33)')`. 그 밖은 실패.
- COLLECT_CHAIN(순차): `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset && AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge [--out <f>]`
- REGRESSION_GATE: `sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-regression --collected tests/.tmp/axe-current.json`

단계:
- step 32: 10개 시나리오 구현, axe-collected.json 생성, 종료 시 `pending`.
- step 33: 예상 = 묶음별(2분 + target × 1분) 합 + 6분, 20분 초과면 즉시 재계획. AC에 `--check-baseline-match`, `--check-executable`.
- step 34~42: 새 key/target은 실패(사라짐 허용, 자동 편입 금지). 해당 step이 만든 신규 위반은 그 step에서 고친다(색 변경 없이).
- step 43 gate: COLLECT_CHAIN(`--merge --out tests/.tmp/axe-current.json`) → REGRESSION_GATE → `--prune-plan` → `--check-coverage` → `--check-plan` → `--check-executable`. 그룹이 남으면 Harness가 `axe-remediation-{id}` step을 43과 44 사이에 재계획한다.
- 재계획 그룹 step: `--check-executable` 통과·`blocked === false`·`fixFiles.length >= 1`일 때만. 소스 allowedPaths = 그룹 fixFiles, 20분 이하, plan 수정 금지, 첫 동작 `python3 -I tests/scripts/start-snapshot.py axe-remediation-{id}`, AC: COLLECT_CHAIN && REGRESSION_GATE && `--check-group-done {id}` && `npm --prefix tests test` && verify-scope && `scope-snapshot.mjs --check tests/.tmp/start-snapshot-axe-remediation-{id}.json --allow {fixFiles}`.
- step 44 recheck: gate 재실행 + `--check-plan --require-empty` + `--assert-no-violations`.
- step 45 finalize: 전제 통과 후에만 baseline을 `[]`로.

### 8.4 axe 시나리오 준비 (`tests/helpers/axe-prepare.js`)

- step 22: `PREPARE_PREFIX = 'prepareForAxe: '`; `prepareError(code, cause?)`; `withPrepareCode(code, fn)`; `preparePage(page, { timeoutMs = 10000 }) → { revealChecked, scrollSteps }`(fonts `loaded` 아니면 `fonts-not-ready`, `innerHeight × 0.8` 간격 스크롤, `scrollTo(0, 0)`, 모든 `.reveal`의 `.in`·visibility·opacity를 poll, 실패 `reveal-hidden:{n}`).
- step 23: `MODAL_ROOT = '#projectModal'`, `MODAL_BODY_TEXT = '#modalBody .modal-blurb, #modalBody .modal-section'`; `assertContentLoaded(locator, timeoutMs, { textLocator = null })`(img `complete && naturalWidth > 0` → `content-not-loaded:img`, svg bbox > 0 → `content-not-loaded:svg`, textLocator 있으면 norm 길이 > 0 → `content-not-loaded:text`); `prepareModal(page, { projectIndex = 0, timeoutMs })`(`gridCard` 개수 ≠ 1 → `project-card-not-found:{N}`, 열림 확인 실패 `modal-not-open`, 반환 `{ include: '#projectModal', projectIndex }`).
- step 24: `prepareLightbox(page, { projectIndex?, timeoutMs })`(기본 `findProjectWithShots`, null → `no-shots-project`, 열림 실패 `lightbox-not-open`, 반환 `{ include: '.lightbox', projectIndex }`); `prepareOverlay`(그 밖 `unknown-scenario`); `prepareForAxe(page, { scenario, projectIndex?, timeoutMs })`(page면 `{ include: 'body', projectIndex: null }`).
- 합성 fixture: 동작 모달 fixture(grid click handler가 `#modalBody`를 채우고 `modal-open`, `window.__opens`·`__closes`·`__clicks`)와 handler 없는 fixture.

## 9. 반응형 (§16 tokens 반영)

| 대상 | 375 | 768 | 1280 |
|---|---|---|---|
| hero `.hero-inner` | 1열(DOM 순서, 좌측 정렬) | 1열 | 2열 grid(§16.2) |
| `#heroStats` | 2×2 | 4×1 | 4×1(2열 grid의 전체 폭) |
| `#heroFeatured` | 1열 | 2열 | 3열(전체 폭) |
| `#projectGrid` | 1열 | 2열 | 3열 |
| `#strengthsGrid` | 1열 | 2열 | 3열 |
| Career `.timeline-item` | 세로 | 가로(top 차 < 24px) | 가로 |
| 섹션 padding-top·bottom(career~contact) | 64px | 80px | 96px |
| card gap(`#heroFeatured`, `#projectGrid`, `#strengthsGrid` row·column) | 24px | 24px | 24px |

가로 스크롤 없음. hero 2열 전환 기준은 viewport 너비 1024px 이상.

## 10. 인쇄와 PDF

- 히어로·대표 카드·본문 visible·opacity 1, 보이는 `.reveal` 비어 있지 않음. 토글·메뉴·scroll-hint·`#projectModal` display none. 인쇄에서는 line clamp를 해제한다(`-webkit-line-clamp: unset`, blurb 전문).
- A(새 페이지): `.lightbox` 없거나 display none. B(overlay 열림): screen에서 `.lightbox` visible 확인 → print → `.lightbox`·`#projectModal` display none.
- PDF > 10240바이트, `buf.toString('latin1').match(/\/Type\s*\/Page\b/g)` 개수 ≥ 1, 파서 의존성 없음.

## 11. 검증 체계 (Q5)

### 11.1 경로
- tracked source: 사이트 `index.html`, `css/style.css`, `css/themes.css`, `js/main.js`, `js/data.js`; tests `tests/package.json`, `tests/package-lock.json`, `tests/.gitignore`, `tests/playwright.config.js`, `tests/helpers/**`, `tests/specs/**`, `tests/fixtures/**`, `tests/scripts/**`(fixtures는 step이 명시한 정확한 파일만).
- runtime(추적 금지): `tests/node_modules/**`, `tests/.npm-cache/**`, `tests/.pw-browsers/**`, `tests/.tmp/**`, `tests/test-results/**`, `tests/playwright-report/**`, 최종 step만 `tests/screenshots/**`.
- Harness managed·policy·lock·state 파일과 §16의 외부 evidence 경로는 두 목록 모두에서 제외한다.
- `tests/.gitignore`는 다음 7줄(끝 개행만 정규화, 정확히 일치):

```
node_modules/
.npm-cache/
.pw-browsers/
.tmp/
test-results/
playwright-report/
screenshots/
```

### 11.2 `tests/scripts/with-env.sh`

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

npm·node·playwright는 모두 이 래퍼로 실행한다. 하네스 testCommand(모든 step 공통, 환경변수 없음): `sh tests/scripts/with-env.sh npm --prefix tests test`.

### 11.3 tests/package.json
- devDependencies `@playwright/test`, `@axe-core/playwright`. scripts: `test` `playwright test`, `browsers:install` `playwright install chromium`, `verify-scope` `node scripts/verify-scope.mjs`, `verify-scope:selftest` `node scripts/verify-scope.mjs --self-test`, `fixtures` `node scripts/make-fixtures.mjs`.

### 11.4 Playwright와 콘솔 수집
- webServer `python3 -m http.server 4173 --bind 127.0.0.1`(cwd `..`, reuseExistingServer), baseURL `http://127.0.0.1:4173`, testDir `./specs`, reporter list, retries 0, outputDir `./test-results`.
- 직렬화(고정): `workers: 1`, `fullyParallel: false`. CLI로 덮어쓰지 않는다. bootstrap.spec.js가 검증한다.
- projects 6개: {mobile 375×812, tablet 768×1024, desktop 1280×800} × {dark, light}, 각각 colorScheme·metadata.theme.
- 테마 fixture는 `THEME_KEY`가 null일 때만 주입. 최초 방문 검사는 fixture 없는 별도 context.
- `collectConsoleErrors(page)`: 즉시 listener, pageerror 전부, console.error는 location hostname이 정확히 Google Fonts 두 도메인일 때만 제외. `finish()`는 networkidle 후 `{ pageErrors, consoleErrors }` 사본. 순서: collect → goto → 동작 → finish → 두 배열 `[]`.

### 11.5 `tests/scripts/verify-scope.mjs`
- step 15 경로: `GIT_DIFF_PATH_ARGS = ['--no-renames', '--name-only']`, `GIT_DIFF_PATCH_ARGS = ['--no-renames', '--unified=0']`(data.js 4구간 BASE→HEAD, BASE→index, BASE→worktree, index→worktree). 둘 다 export, 섞지 않음. `collectInput({ git = runGit })`(Git 읽기만). 경로 정책: 빌더 허용 = §11.1 tracked. 하네스 소유(`CLAUDE.md`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`, `.claude/**`, `.codex/**`, `.harness/harness.lock.json`, `.harness/policy.json`, 이 설계 문서, 레거시 `scripts/**`·`templates/**`·`harness-manifest.json`)은 committed 면제·미커밋 위반. 하네스 런타임 면제: 위 두 `.harness` 파일 외 `.harness/**`, `.venv/**`, `phases/HOO-81-portfolio-redesign/**`. runtime 경로 추적·루트 package.json은 위반.
- step 16 내용: `checkDataJsDiff(patch, { requireExactly3 })`(삭제 줄 0, 추가 줄은 trim 후 `featured: true,`만, 3줄 이하). `--final`이면 BASE→HEAD/index/worktree 정확히 3. index.html 3종 `Space+Grotesk` 포함. gitignore(index, worktree) §11.1. 합성: 가짜 git이 PATCH 인자에만 patch.

### 11.6 통합 AC와 재검증 모드
- 모든 step: 첫 동작 §11.7 시작 snapshot, 종료 시 기본 testCommand 통과(환경변수 없음), AC 마지막 §11.7 범위 gate.
- 종료 gate: step 0~11은 `python3 -I tests/scripts/start-snapshot.py step{N}`(`reused`) 직후 inline C. step 12부터 모든 step(재계획 `axe-remediation-{id}` 포함)은 CLI `scope-snapshot.mjs --check`(projectRoot 유형 → snapshot 경로 유형 → strict schema → lock·identity → 현재 상태 수집(unsafe면 after.z 미접촉 exit 1) → after.z 안전 쓰기 → 판정).
- step 15 이후 기본: 자기 spec 단독 → `npm --prefix tests test` → `verify-scope` → 범위 gate. step 12 이후 시각 step(34~39)과 46은 `python3 -I tests/scripts/design-intake-check.py`(§16.1)를 AC에 포함한다.
- 재검증 모드(step 0~11): HEAD에 그 step의 tracked 허용 파일이 이미 commit되어 있으면(`git ls-files`로 확인) 해당 step은 재검증 모드로 실행한다. 순서: 시작 snapshot → AC의 테스트·S `reused` 명령을 그대로 실행 → 모두 통과하면 파일을 바꾸지 않고(no-op) 범위 gate를 실행하고 runner 로그에 `reverify step{N}: no-op`을 남긴다 → AC가 불일치하면 그 step의 tracked 허용 파일 안에서만 고쳐 AC를 통과시키고 로그에 `reverify step{N}: fixed <파일 목록>`을 남긴다. 재검증 모드의 범위 gate는 세 번째 인자(require-absent)를 `''`로 실행한다(허용 파일이 시작 snapshot에 이미 있으므로). step 0의 `step0 start clean` 조건과 설치 전 작성 순서는 최초 구축에만 적용하고 재검증 모드에서는 생략한다. 기능 추가 없음.

### 11.7 시작 snapshot과 범위 gate

규칙:
- RUNTIME 접두어: §11.1 runtime 7개 디렉터리. SKIP 접두어 = RUNTIME + `.git/` + `.venv/`: 안으로 걷지 않고 그 아래 경로는 hash·기록하지 않는다. EXEMPT: `.harness/`, `.venv/`, `phases/HOO-81-portfolio-redesign/` (GUARDED `.harness/harness.lock.json`, `.harness/policy.json`은 면제 아님).
- 기록 대상 = status의 path·origPath ∪ `git ls-files -z` ∪ projectRoot walk의 `tests/` 아래 파일(C·takeCurrent는 시작 snapshot의 files 키도 포함) − SKIP. 경로별 값: regular file이면 sha256, 경로가 없으면 null.
- 저장소 상대 경로 계약(모든 파일시스템 접근 전, Python `rel_ok(p)` = JS `isRepoRelative(p)`): 문자열, 비어 있지 않음, NUL 없음, 런타임 path API 기준 절대 경로 아님(Python `os.path.isabs`·`os.path.splitdrive(p)[0]`, Node `path.isAbsolute`·`path.parse(p).root`), `/`로 나눈 구성요소가 비어 있지 않고 `.`·`..` 아님. 적용: snapshot `files`의 모든 key(C는 `xy` key도), status parser가 산출하는 모든 path·origPath. 위반은 대상 lstat·open 없이 즉시 거부: S 생성 분기 `bad git status`, S 재사용 분기·JS loader `bad start snapshot: paths: <snapshot>`, C는 snapshot key 위반 `bad start snapshot: paths: <snapshot>`·현재 status 위반 `bad git status`, CLI·`runCheck`는 loader 오류를 code 1로. 산출물을 만들거나 바꾸지 않는다.
- status parser 계약(S·C·JS 동일): NUL로 나눈 뒤 마지막 원소가 빈 bytes면 그 하나만 버린다. 남은 각 레코드는 길이 ≥ 4이고 세 번째 바이트가 공백(빈 레코드 포함 위반은 형식 오류). XY = 앞 2바이트, path = 4번째 바이트부터, 엄격 UTF-8 디코드(실패는 형식 오류). X 또는 Y가 `R`·`C`면 다음 원소가 존재하고 비어 있지 않아야 하며 그것이 origPath(아니면 형식 오류). path·origPath는 저장소 상대 경로 계약 통과(위반은 경로 오류). 오류 범주: Python `ValueError('bad status record')`(UnicodeDecodeError 포함) / `ValueError('bad path')`, JS `Error('bad status record: …')` / `Error('bad path: …')`. S 생성 분기와 C는 parser의 모든 `ValueError`를 정확히 `bad git status`로 종료한다. S와 C의 `parse_status` 정의는 바이트 동일하다.
- projectRoot 유형(모든 하위 접근보다 먼저): S·C는 `git rev-parse --show-toplevel` 경로를, JS는 `root` 인자를 lstat해 `dir`인지 확인. symlink `symlink:{root}`, 없음 `missing:{root}`, 그 밖 `non-regular:{root}`로 즉시 실패. 그다음 realpath(projectRoot)와 realpath(cwd) 비교.
- 경로 유형 계약(lstat 전용): `kind(p)` ∈ `missing`·`file`·`dir`·`symlink`·`other`. `check(p, 허용 leaf)`는 조상을 앞에서부터 lstat하고, 조상이 없으면 leaf를 `missing`으로, 조상이 `dir`가 아니면 `symlink:{조상}`/`non-regular:{조상}`. leaf가 허용 밖이면 `symlink:{p}`, `missing:{p}`, 그 밖 `non-regular:{p}`.
- 경로별 허용 leaf: 기록 대상 `missing|file`; lock `file`; S의 `tests/.tmp` `missing|dir`, S의 snapshot `missing|file`; C·loader·CLI의 snapshot `file`; after.z `missing|file`.
- 읽기: 검사를 통과한 경로만 `O_RDONLY | O_NOFOLLOW | O_NONBLOCK`으로 열고(`O_NOFOLLOW`는 leaf만 보호), fd `fstat`가 regular가 아니면 `unsafe path: non-regular:{p}`(FIFO에서 멈추지 않음). 쓰기: 새 snapshot `O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW`, after.z는 기록 대상 unsafe가 없을 때만 쓰기 직전 `check` 재실행 후 `O_WRONLY | O_CREAT | O_TRUNC | O_NOFOLLOW | O_NONBLOCK`.
- 실행 전제(trusted-agent canary): snapshot 생성부터 그 step 종료 gate까지 다른 프로세스가 projectRoot 내부 경로·조상·snapshot·after.z를 생성·교체·삭제하지 않는다. 동시 경로 교체 공격은 지원 범위 밖. 보장 범위는 실행 시점 lstat 유형 검사, leaf `O_NOFOLLOW`·fd `fstat`, 저장소 밖 경로 거부, unsafe 시 fail-closed. dirfd/openat 구현이나 경쟁 주입 테스트는 두지 않는다.
- symlink 금지: projectRoot부터 lstat으로 걷고 SKIP 내부는 들어가지 않는다. 발견한 모든 symlink 엔트리(SKIP 디렉터리 엔트리 자체 포함)는 `symlink:{p}`, allow·EXEMPT·GUARDED도 면제하지 않는다. symlink 대상은 resolve·readlink·open하지 않는다.
- 실행 순서
  - S: step id → toplevel → projectRoot 유형 → realpath·cwd 비교 → walk → `git status`(parser 계약, 위반 `bad git status`)·`git ls-files` → 기록 대상·lock·`tests/.tmp`·snapshot 경로 유형 검사(실패면 `unsafe path: {정렬 목록}`, 이 시점까지 프로젝트 파일 open·write 없음) → `rev-parse --verify BASE` → lock 읽기 → identity → 재사용(검증) 또는 생성(hash → `tests/.tmp` 생성 → exclusive create).
  - C: toplevel → projectRoot 유형 → realpath·cwd 비교 → snapshot·after.z 경로 유형 검사 → snapshot 읽기 → 키·`files`·`xy` 형식과 key 경로 계약 → status(parser 계약, 위반이면 walk·`ls-files`·hash·after.z 쓰기 없이 `bad git status`) → walk → 기록 대상 유형 검사 → unsafe 없을 때만 hash → unsafe가 있으면 after.z 미접촉으로 snapshot-not-first·정렬 unsafe를 stderr에 exit 1 → 변경 판정 → after.z 재검사 → after.z 쓰기 → 결과.
- 판정(시작·현재 합집합 p, allow·EXEMPT 제외): hash 다르면 tests 안 `tests-changed:{p}`, 밖 `outside-tests:{p}`. hash 같고 xy 다르면 `status-changed:{p}`. 시작에 없던 RUNTIME 경로가 status에 보이면 `runtime-visible:{p}`. `--require-absent` 경로가 시작 기록에 있으면 `snapshot-not-first:{p}`. 순서: snapshot-not-first → 정렬된 unsafe → 경로 오름차순 변경 → runtime-visible.
- Git은 `status`, `ls-files`, `rev-parse` 읽기만. python3 표준 라이브러리만.

schema (strict, schemaVersion 1):
- JSON 파싱: 모든 깊이의 중복 key, `NaN`·`Infinity`·`-Infinity`는 `invalid json`(Python `object_pairs_hook=no_dup, parse_constant=no_const`, JS `JSON.parse` 후 `scanJsonTopLevel`).
- 키 집합 정확히 `schemaVersion, stepId, projectRoot, head, base, harness, statusZHex, xy, files`.
- `schemaVersion`: 최상위에 정확히 한 번, lexical token 정확히 `1`(Python `type(v) is int and v == 1`, JS `Number.isInteger(v) && v === 1`이고 최상위 token이 `'1'`).
- stepId `step{N}` | `axe-remediation-{id}` | 테스트 전용 `parity-{숫자}`, 파일 `tests/.tmp/start-snapshot-{stepId}.json`. projectRoot = toplevel realpath. head = `git rev-parse HEAD`. base = BASE. harness = 중앙 identity 3값 + lock sha256(`lockSha256`), lock에 3값이 모두 있어야 한다.
- `statusZHex`: 짝수 길이 소문자 hex, 디코드 bytes를 parser 계약으로 파싱(형식 오류 `status parse`, 경로 위반 `paths`). `xy`는 파싱 결과와 정확히 같음. `files`: 값은 소문자 64hex 또는 null(위반 `files`), key 경로 계약(위반 `paths`), 파싱된 비SKIP status 경로는 모두 key(위반 `files/status`).
- 검사 순서: invalid json → keys → schemaVersion → (loader만 stepId) → statusZHex → status parse/paths → xy → files → paths → files/status.
- 메시지: `bad start snapshot: {범주}: <path>`, `start snapshot identity mismatch: {field}`, `unsafe path: {…}`.

`scanJsonTopLevel(rawText) → Array<{ key, token }>` (JS, step 2): 한 번 훑으며 공백 skip, 큰따옴표 문자열은 백슬래시 다음 1문자를 건너뛰며 slice, 스택 `{ kind, keys, expectKey }`, object key slice는 `JSON.parse`로 디코드하고 중복이면 `Error('duplicate key: {key}')`, 깊이 1 멤버의 값 원문(trim)을 token으로 기록, 최상위가 객체가 아니면 `[]`.

최초 실행·재시도: 파일이 없으면 검사 후 exclusive create(`start-snapshot: created <path>`). 있으면 새로 수집하지 않고 schema·identity를 현재 값과 비교해 모두 같으면 `start-snapshot: reused <path>`, 아니면 exit 1. 기존 snapshot을 덮어쓰기·삭제·재기준화하지 않는다. 불일치는 하네스 조치·재계획 사유.

스크립트 S — step 0은 어떤 파일보다 먼저 `python3 -I - step0 <<'PY'` + 아래 본문 + `PY`로 실행하고, 같은 본문을 바이트 그대로 `tests/scripts/start-snapshot.py`에 저장한다. step 1 이후 첫 동작은 `python3 -I tests/scripts/start-snapshot.py step{N}`. 빌더는 이 본문을 바꾸지 않는다.

```
import hashlib, json, os, re, stat, subprocess, sys
RUNTIME = ('tests/node_modules/', 'tests/.npm-cache/', 'tests/.pw-browsers/', 'tests/.tmp/', 'tests/test-results/', 'tests/playwright-report/', 'tests/screenshots/')
SKIP = RUNTIME + ('.git/', '.venv/')
BASE = 'd0a8a6e462bc1366757b1401c3ba7aeb0fbf391d'
HARNESS = {'sourceCommit': 'e7a03919a460f975149f7c55343ca4b34d3d2352', 'manifestHash': 'b627e6a5ce4a903c24c400927ca2b49a14d0bd59632c691b2a5c2d74c6c08372', 'distributionVersion': '2.0.1'}
LOCK = '.harness/harness.lock.json'
KEYS = {'schemaVersion', 'stepId', 'projectRoot', 'head', 'base', 'harness', 'statusZHex', 'xy', 'files'}
HEX64 = re.compile('[0-9a-f]{64}')
STEP = sys.argv[1] if len(sys.argv) == 2 else ''
if not re.fullmatch('step[0-9]+|axe-remediation-[a-z0-9]+(-[a-z0-9]+)*|parity-[0-9]+', STEP):
    sys.exit('bad step id: ' + STEP)
OUT = 'tests/.tmp/start-snapshot-' + STEP + '.json'
def git(*args):
    return subprocess.run(['git', *args], check=True, capture_output=True).stdout
def unsafe(items):
    sys.exit('unsafe path: ' + ','.join(items))
def rel_ok(p):
    if not isinstance(p, str) or p == '' or chr(0) in p or os.path.isabs(p) or os.path.splitdrive(p)[0]:
        return False
    return all(c not in ('', '.', '..') for c in p.split('/'))
def kind(p):
    try:
        mode = os.lstat(p).st_mode
    except FileNotFoundError:
        return 'missing'
    if stat.S_ISLNK(mode):
        return 'symlink'
    if stat.S_ISDIR(mode):
        return 'dir'
    if stat.S_ISREG(mode):
        return 'file'
    return 'other'
def label(k, p):
    return {'symlink': 'symlink:', 'missing': 'missing:'}.get(k, 'non-regular:') + p
def check(p, leaf):
    parts = p.split('/')
    for i in range(1, len(parts)):
        a = '/'.join(parts[:i])
        k = kind(a)
        if k == 'missing':
            return None if 'missing' in leaf else 'missing:' + p
        if k != 'dir':
            return label(k, a)
    k = kind(p)
    return None if k in leaf else label(k, p)
def read(p):
    fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as f:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            unsafe(['non-regular:' + p])
        return f.read()
def digest(p):
    k = kind(p)
    if k == 'missing':
        return None
    if k != 'file':
        unsafe([label(k, p)])
    return hashlib.sha256(read(p)).hexdigest()
def scan():
    bad, found = [], []
    for top, dirs, names in os.walk('.'):
        rel = '' if top == '.' else top[2:] + '/'
        keep = []
        for d in dirs:
            if os.path.islink(rel + d):
                bad.append('symlink:' + rel + d)
            elif not (rel + d + '/').startswith(SKIP):
                keep.append(d)
        dirs[:] = keep
        for n in names:
            if os.path.islink(rel + n):
                bad.append('symlink:' + rel + n)
            elif (rel + n).startswith('tests/'):
                found.append(rel + n)
    return bad, found
def parse_status(raw):
    recs = raw.split(bytes(1))
    if recs and recs[-1] == b'':
        recs.pop()
    xy = {}
    i = 0
    while i < len(recs):
        rec = recs[i]
        i += 1
        if len(rec) < 4 or rec[2:3] != b' ':
            raise ValueError('bad status record')
        code = rec[:2].decode()
        p = rec[3:].decode()
        if not rel_ok(p):
            raise ValueError('bad path')
        xy[p] = code
        if code[0] in 'RC' or code[1] in 'RC':
            if i >= len(recs) or not recs[i]:
                raise ValueError('bad status record')
            o = recs[i].decode()
            if not rel_ok(o):
                raise ValueError('bad path')
            xy[o] = code
            i += 1
    return xy
def fail(what):
    sys.exit('bad start snapshot: ' + what + ': ' + OUT)
def version_ok(v):
    return type(v) is int and v == 1
def no_dup(pairs):
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError('duplicate key')
    return dict(pairs)
def no_const(name):
    raise ValueError('json constant ' + name)
top = git('rev-parse', '--show-toplevel').decode().strip()
rk = kind(top)
if rk != 'dir':
    unsafe([label(rk, top)])
root = os.path.realpath(top)
if os.path.realpath(os.getcwd()) != root:
    sys.exit('run from project root: ' + root)
bad, found = scan()
status = git('status', '--porcelain=v1', '-z', '--untracked-files=all')
try:
    xy = parse_status(status)
except ValueError:
    sys.exit('bad git status')
tracked = [p.decode() for p in git('ls-files', '-z').split(bytes(1)) if p]
targets = sorted(p for p in set(xy) | set(found) | set(tracked) if not p.startswith(SKIP))
bad += [r for r in (check(p, ('missing', 'file')) for p in targets) if r]
bad += [r for r in (check(LOCK, ('file',)), check('tests/.tmp', ('missing', 'dir')), check(OUT, ('missing', 'file'))) if r]
if bad:
    unsafe(sorted(set(bad)))
git('rev-parse', '--verify', BASE + '^{commit}')
lock = read(LOCK)
if any(v.encode() not in lock for v in HARNESS.values()):
    sys.exit('harness identity mismatch: ' + LOCK)
ident = {'schemaVersion': 1, 'stepId': STEP, 'projectRoot': root, 'head': git('rev-parse', 'HEAD').decode().strip(), 'base': BASE, 'harness': dict(HARNESS, lockSha256=hashlib.sha256(lock).hexdigest())}
if not version_ok(ident['schemaVersion']):
    fail('schemaVersion')
if kind(OUT) == 'file':
    try:
        old = json.loads(read(OUT).decode('utf-8'), object_pairs_hook=no_dup, parse_constant=no_const)
    except (OSError, ValueError):
        fail('invalid json')
    if not isinstance(old, dict) or set(old) != KEYS:
        fail('keys')
    if not version_ok(old['schemaVersion']):
        fail('schemaVersion')
    hx, oxy, ofiles = old['statusZHex'], old['xy'], old['files']
    if not isinstance(hx, str) or len(hx) % 2 or not re.fullmatch('[0-9a-f]*', hx):
        fail('statusZHex')
    try:
        parsed = parse_status(bytes.fromhex(hx))
    except ValueError as e:
        fail('paths' if str(e) == 'bad path' else 'status parse')
    if parsed != oxy:
        fail('xy')
    if not isinstance(ofiles, dict) or any(not (v is None or (isinstance(v, str) and HEX64.fullmatch(v))) for v in ofiles.values()):
        fail('files')
    if not all(rel_ok(p) for p in ofiles):
        fail('paths')
    if any(p not in ofiles for p in parsed if not p.startswith(SKIP)):
        fail('files/status')
    for k in sorted(ident):
        if old[k] != ident[k]:
            sys.exit('start snapshot identity mismatch: ' + k)
    print('start-snapshot: reused ' + OUT)
    sys.exit(0)
files = {p: digest(p) for p in targets}
os.makedirs('tests/.tmp', exist_ok=True)
fd = os.open(OUT, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
with os.fdopen(fd, 'w', encoding='utf-8') as f:
    json.dump(dict(ident, statusZHex=status.hex(), xy=xy, files=files), f, indent=1, sort_keys=True)
print('start-snapshot: created ' + OUT)
```

inline 범위 검사 C — step 0~11 종료 검사. 반드시 직전에 S `reused`를 통과한 뒤 실행한다. 실행: `python3 -I - <stepId> '<allow 쉼표 목록>' '<require-absent 쉼표 목록>' <<'PY'` + 아래 본문 + `PY`. 위반이면 stderr 목록 + exit 1, 아니면 `scope-snapshot: OK`. 아래 본문이 확정본이다: `parse_status` 정의는 S의 정의와 바이트 동일하며, 빌더는 이 본문을 수정·재작성·우회하지 않는다.

```
import hashlib, json, os, stat, subprocess, sys
RUNTIME = ('tests/node_modules/', 'tests/.npm-cache/', 'tests/.pw-browsers/', 'tests/.tmp/', 'tests/test-results/', 'tests/playwright-report/', 'tests/screenshots/')
SKIP = RUNTIME + ('.git/', '.venv/')
EXEMPT = ('.harness/', '.venv/', 'phases/HOO-81-portfolio-redesign/')
GUARDED = ('.harness/harness.lock.json', '.harness/policy.json')
KEYS = {'schemaVersion', 'stepId', 'projectRoot', 'head', 'base', 'harness', 'statusZHex', 'xy', 'files'}
STEP = sys.argv[1]
START = 'tests/.tmp/start-snapshot-' + STEP + '.json'
AFTER = START[:-5] + '-after.z'
allow = {p for p in sys.argv[2].split(',') if p}
absent = {p for p in sys.argv[3].split(',') if p}
def git(*args):
    return subprocess.run(['git', *args], check=True, capture_output=True).stdout
def rel_ok(p):
    if not isinstance(p, str) or p == '' or chr(0) in p or os.path.isabs(p) or os.path.splitdrive(p)[0]:
        return False
    return all(c not in ('', '.', '..') for c in p.split('/'))
def parse_status(raw):
    recs = raw.split(bytes(1))
    if recs and recs[-1] == b'':
        recs.pop()
    xy = {}
    i = 0
    while i < len(recs):
        rec = recs[i]
        i += 1
        if len(rec) < 4 or rec[2:3] != b' ':
            raise ValueError('bad status record')
        code = rec[:2].decode()
        p = rec[3:].decode()
        if not rel_ok(p):
            raise ValueError('bad path')
        xy[p] = code
        if code[0] in 'RC' or code[1] in 'RC':
            if i >= len(recs) or not recs[i]:
                raise ValueError('bad status record')
            o = recs[i].decode()
            if not rel_ok(o):
                raise ValueError('bad path')
            xy[o] = code
            i += 1
    return xy
def kind(p):
    try:
        mode = os.lstat(p).st_mode
    except FileNotFoundError:
        return 'missing'
    if stat.S_ISLNK(mode):
        return 'symlink'
    if stat.S_ISDIR(mode):
        return 'dir'
    if stat.S_ISREG(mode):
        return 'file'
    return 'other'
def label(k, p):
    return {'symlink': 'symlink:', 'missing': 'missing:'}.get(k, 'non-regular:') + p
def check(p, leaf):
    parts = p.split('/')
    for i in range(1, len(parts)):
        a = '/'.join(parts[:i])
        k = kind(a)
        if k == 'missing':
            return None if 'missing' in leaf else 'missing:' + p
        if k != 'dir':
            return label(k, a)
    k = kind(p)
    return None if k in leaf else label(k, p)
def read(p):
    fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as f:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            sys.exit('unsafe path: non-regular:' + p)
        return f.read()
def no_dup(pairs):
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError('duplicate key')
    return dict(pairs)
top = git('rev-parse', '--show-toplevel').decode().strip()
rk = kind(top)
if rk != 'dir':
    sys.exit('unsafe path: ' + label(rk, top))
if os.path.realpath(top) != os.path.realpath(os.getcwd()):
    sys.exit('run from project root: ' + top)
pre = [r for r in (check(START, ('file',)), check(AFTER, ('missing', 'file'))) if r]
if pre:
    sys.exit('unsafe path: ' + ','.join(sorted(set(pre))))
start = json.loads(read(START).decode('utf-8'), object_pairs_hook=no_dup)
if not isinstance(start, dict) or set(start) != KEYS or start['stepId'] != STEP or not isinstance(start['files'], dict) or not isinstance(start['xy'], dict):
    sys.exit('bad start snapshot: ' + START)
if not all(rel_ok(p) for p in list(start['files']) + list(start['xy'])):
    sys.exit('bad start snapshot: paths: ' + START)
status = git('status', '--porcelain=v1', '-z', '--untracked-files=all')
try:
    xy = parse_status(status)
except ValueError:
    sys.exit('bad git status')
unsafe, found = [], []
for top_dir, dirs, names in os.walk('.'):
    rel = '' if top_dir == '.' else top_dir[2:] + '/'
    keep = []
    for d in dirs:
        if os.path.islink(rel + d):
            unsafe.append('symlink:' + rel + d)
        elif not (rel + d + '/').startswith(SKIP):
            keep.append(d)
    dirs[:] = keep
    for n in names:
        if os.path.islink(rel + n):
            unsafe.append('symlink:' + rel + n)
        elif (rel + n).startswith('tests/'):
            found.append(rel + n)
listed = [p.decode() for p in git('ls-files', '-z').split(bytes(1)) if p]
targets = sorted(p for p in set(xy) | set(start['files']) | set(found) | set(listed) if not p.startswith(SKIP))
unsafe += [r for r in (check(p, ('missing', 'file')) for p in targets) if r]
def digest(p):
    k = kind(p)
    if k == 'file':
        return hashlib.sha256(read(p)).hexdigest()
    if k != 'missing':
        unsafe.append(label(k, p))
    return None
files = {} if unsafe else {p: digest(p) for p in targets}
bad = ['snapshot-not-first:' + p for p in sorted(absent) if p in start['files'] or p in start['xy']]
if unsafe:
    sys.exit('\n'.join(bad + sorted(set(unsafe))))
for p in sorted(files):
    if p in allow or (p.startswith(EXEMPT) and p not in GUARDED):
        continue
    if start['files'].get(p) != files[p]:
        bad.append(('tests-changed:' if p.startswith('tests/') else 'outside-tests:') + p)
    elif start['xy'].get(p) != xy.get(p):
        bad.append('status-changed:' + p)
bad += ['runtime-visible:' + p for p in sorted(xy) if p.startswith(RUNTIME) and p not in start['xy']]
r = check(AFTER, ('missing', 'file'))
if r:
    sys.exit('\n'.join(bad + ['unsafe path: ' + r]))
fd = os.open(AFTER, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW | os.O_NONBLOCK, 0o644)
with os.fdopen(fd, 'wb') as f:
    f.write(status)
if bad:
    sys.exit('\n'.join(bad))
print('scope-snapshot: OK')
```

설계 블록 추출 규칙(테스트용, 읽기 전용): `스크립트 S`로 시작하는 줄 다음 첫 fenced code block이 S 본문, `inline 범위 검사 C`로 시작하는 줄 다음 첫 fenced code block이 C 본문(여는·닫는 ``` 줄 제외, 끝 개행 1개 포함). 함수 정의 추출: `def <이름>(` 줄부터 다음 들여쓰기 없는 줄 직전까지.

S·C exec harness(테스트 전용): `python3 -I -c '<harness>'`가 S 또는 C 본문을 받아 `subprocess.run`(`rev-parse --show-toplevel`은 지정 경로, `status`는 호출자가 bytes를 지정한 경우에만 그 bytes, 그 밖 git 호출은 기록 후 예외), `os.lstat`·`os.walk`·`os.open`·`os.makedirs`·`builtins.open`을 기록용 래퍼로 감싸 `exec`하고 `SystemExit` 메시지·그 밖 예외 유형·호출 기록을 JSON으로 출력한다.

비교 도구 `tests/scripts/scope-snapshot.mjs` (S·C와 같은 판정·문자열·순서, step별 추가만):
- step 1: 상수(`RUNTIME_PREFIXES`, `SKIP_PREFIXES`, `EXEMPT_PREFIXES`, `GUARDED_PATHS`, `LOCK_PATH`, `SNAPSHOT_KEYS`, `STEP_ID_RE`, `HEX64_RE`, `BASE`, `HARNESS_IDENTITY`, `STATUS_ARGS`, `LS_FILES_ARGS`), `UnsafePathError`, `checkRoot`, `pathKind`, `checkPath`, `readRegular`.
- step 2: `isRepoRelative`, `parseStatusZ`(parser 계약, `new TextDecoder('utf-8', { fatal: true })`), `statusXyMap`, `scanJsonTopLevel`, `isSchemaVersion1(value, token)`.
- step 3: `loadStartSnapshot(file, { fs, root })`(위 검사 순서, snapshot 외 경로 접근 없음).
- step 4: `scanProject`, `hashPath`, `takeCurrent(start | null, { git, fs, root })`(start key 경로 계약 선검사, unsafe면 hash 없이 `files: {}`).
- step 5·6: 코드 없음(symlink·특수 파일·조상 symlink 거부 실행 검증).
- step 7: `computeIdentity`, `checkIdentity`, `diffAgainstStart`, `classifyChanges`, `checkRuntimeVisible`, `checkSnapshotFirst`, `evaluateGate`.
- step 8: `writeAfterZ`, `runCheck`((0) checkRoot → (1) loader → (2) identity → (3) takeCurrent(unsafe면 after.z 미접촉 code 1) → (4) writeAfterZ → (5) evaluateGate), CLI `--check <start.json> --allow <list> [--require-absent <list>]`(인자 오류 exit 2).
- step 9~11: 코드 없음. parity-core (i)~(v), parity-paths (vi), parity-artifacts(after.z 보존 4조합, CLI `tests/.tmp` 조상 링크 거부, after.z FIFO·identity 변형 거부).

테스트 격리 규칙: 실제 저장소에는 runtime 경로(`tests/.tmp/start-snapshot-parity-{숫자}.json`과 그 after.z, `tests/.tmp/snapshot-probes/__retry_probe.txt`, `tests/.tmp/status-harness-<pid>/`)만 쓴다. 비runtime 경로 검증은 합성 저장소 `tests/.tmp/synthetic-repos/<pid>/`(+`<pid>-outside`, `<pid>-link`, `<pid>-file`)에서 한다. 거부 대상 상태는 실행 전에 만들고 실행 중 바꾸지 않는다. S·C·CLI subprocess는 timeout 10초.

## 12. 변경 허용 경로와 운영 경계

- index.json allowedPaths: `index.html`, `css/style.css`, `css/themes.css`, `js/main.js`, `js/data.js`, `tests/` (Harness managed·policy·lock·state와 외부 evidence 제외). 각 step의 tracked 허용 파일 = 범위 gate `--allow`.
- `index.html` 구조 변경은 step 34·35·37만. 속성 변경은 remediation 그룹 step만 허용하며 예외는 step 37의 두 가지: (a) `.scroll-hint` `href`를 `#career`로, (b) §6 표대로 section `class`(`#projects`·`#about`은 정확히 `section section-alt`, `#career`·`#strengths`·`#contact`는 정확히 `section`). `css/themes.css`는 변경하지 않는다(§16.4 guard가 거부; 색 변경은 §16.3 제외).
- 빌더 허용 명령: Git 읽기(rev-parse, diff, show, ls-files, ls-tree, status, log, `-w` 없는 hash-object), §11.7 snapshot·검사, §16.1 intake 검사(외부 evidence 읽기 전용). 하네스 전용: 프로젝트 저장소 Git 상태 변경, Harness 운영 명령. main 직접 변경·merge·deploy 금지.
- 합성 저장소 예외: `tests/.tmp/synthetic-repos/<pid>/`에서만 `git -C <dir> init -q`, `add -A`/정확한 경로 add, `-c user.name=t -c user.email=t@example.invalid commit -q -m <msg>`. 권한 변경 없음, 종료 시 정리.
- 빌더 수정 금지: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`, 시작 snapshot 파일, 외부 evidence 디렉터리와 그 파일.

## 13. Step 목록 (각 20분 이하, snapshot·gate·검증·디버깅 포함)

| # | name | 예상 | 종료 gate |
|---|---|---|---|
| 0 | tests-env-bootstrap (재검증) | 18 | S reused + C |
| 1 | scope-snapshot-paths (재검증) | 17 | S reused + C |
| 2 | scope-snapshot-parse (재검증) | 19 | S reused + C |
| 3 | scope-snapshot-loader (재검증) | 19 | S reused + C |
| 4 | scope-snapshot-state (재검증) | 19 | S reused + C |
| 5 | scope-snapshot-symlink (재검증) | 18 | S reused + C |
| 6 | scope-snapshot-special-files (재검증) | 19 | S reused + C |
| 7 | scope-snapshot-identity (재검증) | 18 | S reused + C |
| 8 | scope-snapshot-cli (재검증) | 17 | S reused + C |
| 9 | scope-snapshot-parity-core (재검증) | 19 | S reused + C |
| 10 | scope-snapshot-parity-paths (재검증) | 17 | S reused + C |
| 11 | scope-snapshot-parity-artifacts (재검증) | 19 | S reused + C |
| 12 | claude-design-intake | 15 | CLI (첫 CLI gate) |
| 13 | design-guard | 19 | CLI |
| 14 | tests-browser-smoke | 15 | CLI |
| 15 | scope-paths | 19 | CLI |
| 16 | scope-content | 19 | CLI |
| 17 | content-data-baseline | 16 | CLI |
| 18 | content-static-baseline | 17 | CLI |
| 19 | modal-regression | 18 | CLI |
| 20 | ui-regression | 17 | CLI |
| 21 | axe-canonical | 19 | CLI |
| 22 | axe-prepare-page | 15 | CLI |
| 23 | axe-prepare-modal | 18 | CLI |
| 24 | axe-prepare-lightbox | 19 | CLI |
| 25 | axe-collect-tooling | 19 | CLI |
| 26 | axe-baseline-regression | 19 | CLI |
| 27 | axe-baseline-projection | 17 | CLI |
| 28 | axe-remediation-plan-schema | 17 | CLI |
| 29 | axe-plan-executable | 15 | CLI |
| 30 | axe-current-checks | 17 | CLI |
| 31 | axe-regression-prune | 19 | CLI |
| 32 | axe-collect | 17 | CLI |
| 33 | axe-classify | ≤20 (초과 시 재계획) | CLI |
| 34 | featured-projects | 19 | CLI |
| 35 | hero-first-screen | 20 | CLI |
| 36 | hero-two-column | 17 | CLI |
| 37 | section-structure | 19 | CLI |
| 38 | section-layout | 17 | CLI |
| 39 | component-states | 19 | CLI |
| 40 | focus-trap-modal | 17 | CLI |
| 41 | focus-trap-lightbox | 17 | CLI |
| 42 | print-pdf | 17 | CLI |
| 43 | axe-remediation-gate | 18 | CLI |
| (재계획) | axe-remediation-{id} | ≤20 | CLI |
| 44 | axe-remediation-recheck | 18 | CLI |
| 45 | axe-finalize | 16 | CLI |
| 46 | final-verification | 17 | CLI |

각 step의 선행은 그보다 작은 번호 전부(44는 재계획 그룹 포함).

## 14. 빌더 재량

§16.2 tokens 안의 세부 수치(폰트 크기·line-height·letter-spacing 등 비색 타이포 값), CSS 클래스 구조(명시된 id·data 속성·클래스 유지), 테스트 helper 분할.

## 15. step 공통 절차 (모든 stepN.md가 참조)

1. read-first: `CLAUDE.md`, `README.md`, 하위 `CLAUDE.md`·`AGENTS.md`, 선행 시각 설계 문서, 이 문서의 지정 절. 선행 step이 모두 completed인지 확인한다.
2. read-only: §12 빌더 수정 금지 목록.
3. 명령 권한: §12.
4. 실행: npm·node는 `sh tests/scripts/with-env.sh <명령>`. Playwright는 `workers: 1`. §11.7 실행 전제를 지킨다.
5. 첫 동작: 어떤 파일도 쓰기 전에 시작 snapshot(`python3 -I tests/scripts/start-snapshot.py step{N}`, step 0은 heredoc S). `created`/`reused`가 아니면 중단·보고.
6. runtime 쓰기 기본 R0: `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`.
7. 공통 수정 금지: step 허용 목록 밖 파일, 이전 step 함수의 동작, 시작 snapshot, 비runtime 경로의 symlink·특수 파일 생성, §16.3 제외 항목.
8. 종료 조건: 기본 testCommand 통과 + AC 마지막 범위 gate 통과(step 0~11은 S reused + inline C, 재검증 모드면 require-absent `''`; step 12부터 CLI).
9. step 0~11은 §11.6 재검증 모드 규칙을 따른다.

## 16. Claude Design 반영

### 16.1 evidence와 intake

- 연결 검증: Claude Code 대화형 `/design`이 실제 인식되어 artifact까지 생성됐다. Claude Design 전용 MCP는 없고 이번 실행은 handoff ID 없이 로컬 bundle만 생성됐다.
- summary: `/Users/hoon/.hermes/company/development/product-management/HOO-81-evidence/claude-design-pattern-board-summary-2026-11-24.md`
- bundle dir: `/Users/hoon/.hermes/company/development/product-management/HOO-81-evidence/claude-design-pattern-board-2026-11-24/` — 정확히 9개 파일과 SHA-256:
  - `canvas.json` `83c1c86506050649e92a6a8100bab41d99068856e472caf20f2d2b4eee27d811`
  - `Main.dc.html` `6d51dc701d49ef17e8bd2b1c2041d96c79b585f5139739c4862171db69deee9f`
  - `Foundations.dc.html` `27ecd3caa0c0b22e2eb5a8da03e9ac409c0ee7aa35e63a664fe17e9768e13b27`
  - `Components.dc.html` `abe37081269d8230b5ab3afbaf725399bf24f274dc31f8e003e1b152874f4a21`
  - `DesktopTop.dc.html` `48d5ba837d41b485df03199779eb84ebbc51ae494add2d6971648b52fbfb83ca`
  - `DesktopExplore.dc.html` `d83dda4dffdc93e95f52c368699ecee92740713838cb50b5b4f9987a62930287`
  - `DesktopFirstLight.dc.html` `bb7dff0e579762c4c77fe5ad7e8f60fd448947aa5fa9410a6e840a5c3e29c658`
  - `Mobile.dc.html` `6abe200fbbb1bbaf1306b784b0a04b700ff9345b44889c684b0dc801e5cc67b2`
  - `MobileMenu.dc.html` `c1ba1bc7ae336146357db585ca4408a9962f21c8e7eb3c76b654e49b7ac663e9`
- 이 외부 경로는 allowedPaths·범위 gate 대상이 아니며 읽기 전용이다. 빌더는 bundle을 참조하기 전에 항상 `python3 -I tests/scripts/design-intake-check.py`(DESIGN_HASH_CHECK)를 실행해 `design-intake: OK`를 확인한다. mockup의 문구·숫자·placeholder는 콘텐츠로 쓰지 않는다(콘텐츠는 data.js·index.html 기존 값만).
- `tests/fixtures/claude-design-intake.json` (step 12, 정확한 내용·키 순서):

```
{
  "schemaVersion": 1,
  "summaryPath": "/Users/hoon/.hermes/company/development/product-management/HOO-81-evidence/claude-design-pattern-board-summary-2026-11-24.md",
  "bundleDir": "/Users/hoon/.hermes/company/development/product-management/HOO-81-evidence/claude-design-pattern-board-2026-11-24",
  "files": {
    "canvas.json": "83c1c86506050649e92a6a8100bab41d99068856e472caf20f2d2b4eee27d811",
    "Main.dc.html": "6d51dc701d49ef17e8bd2b1c2041d96c79b585f5139739c4862171db69deee9f",
    "Foundations.dc.html": "27ecd3caa0c0b22e2eb5a8da03e9ac409c0ee7aa35e63a664fe17e9768e13b27",
    "Components.dc.html": "abe37081269d8230b5ab3afbaf725399bf24f274dc31f8e003e1b152874f4a21",
    "DesktopTop.dc.html": "48d5ba837d41b485df03199779eb84ebbc51ae494add2d6971648b52fbfb83ca",
    "DesktopExplore.dc.html": "d83dda4dffdc93e95f52c368699ecee92740713838cb50b5b4f9987a62930287",
    "DesktopFirstLight.dc.html": "bb7dff0e579762c4c77fe5ad7e8f60fd448947aa5fa9410a6e840a5c3e29c658",
    "Mobile.dc.html": "6abe200fbbb1bbaf1306b784b0a04b700ff9345b44889c684b0dc801e5cc67b2",
    "MobileMenu.dc.html": "c1ba1bc7ae336146357db585ca4408a9962f21c8e7eb3c76b654e49b7ac663e9"
  },
  "adopted": ["explore-surface", "hero-two-column-left", "mobile-single-column", "final-section-order", "featured-three", "projects-thirteen-order", "component-states", "hit-target-44", "section-padding", "card-gap", "type-hierarchy", "line-clamp", "strength-stripe-removal"],
  "excluded": ["new-color", "color-role-change", "dark-text-0d0f12", "muted-grey-reassign", "font-asset-change", "new-copy-or-number", "new-section-image-icon", "project-order-or-ia-change", "placeholder-as-content"],
  "tokens": {
    "heroTwoColumnMinViewportPx": 1024,
    "heroColumns": "minmax(0, 5fr) minmax(0, 7fr)",
    "heroColumnGapPx": 48,
    "heroAreas": ["eyebrow summary", "name summary", "tagline summary", "role cta", "stats stats", "featured featured"],
    "sectionPaddingPx": { "375": 64, "768": 80, "1280": 96 },
    "cardGapPx": 24,
    "hitTargetMinPx": 44,
    "blurbLineClamp": 3
  }
}
```

- `tests/scripts/design-intake-check.py`(step 12, python3 표준 라이브러리, 쓰기 없음): fixture를 읽고 → `summaryPath`·`bundleDir`·각 bundle 파일을 lstat해 symlink·non-regular면 `design-intake: unsafe:{path}` exit 1 → `os.listdir(bundleDir)`의 정렬 목록이 `files` key 9개와 정확히 같지 않으면 `design-intake: files mismatch` exit 1 → 각 파일을 `rb`로 읽어 sha256이 fixture와 다르면 `design-intake: hash mismatch:{name}` exit 1 → summary 텍스트에 각 `` `{name}` — `{sha}` `` 줄이 정확히 있지 않으면 `design-intake: summary mismatch:{name}` exit 1 → 통과 시 stdout `design-intake: OK`, exit 0. 어떤 파일도 쓰거나 지우지 않는다.

### 16.2 허용 패턴 (구현 기준)

- Explore surface: PROJECTS 13개 전체를 기존 순서로 card grid에 두고 card → modal 탐색 유지.
- hero(step 35·36): `.hero-inner` 직계 자식 8개(§5). viewport ≥ 1024px에서 `.hero-inner`는 `display: grid`, `grid-template-columns: minmax(0, 5fr) minmax(0, 7fr)`, column-gap 48px, `grid-template-areas: "eyebrow summary" "name summary" "tagline summary" "role cta" "stats stats" "featured featured"`(DOM 순서는 바꾸지 않음), 텍스트 좌측 정렬. 1024px 미만은 1열(DOM 순서대로 세로, 좌측 정렬).
- 섹션 padding-top·bottom: §9 표(64/80/96px). card gap 24px(§9 표 대상).
- component state: 대상 `.nav-link`, `#menuToggle`, `#themeToggle`, `.hero-cta .btn`, `.featured-card`, `#projectGrid .project-card`, `#projectModal .modal-close`, `#contactActions a`, `.scroll-hint`(보이는 경우). default/hover/active는 비색 속성(transform·opacity)만 달라지고 color·background-color·border-color·outline-color는 default와 같다. focus-visible은 기존 outline(step 41 검증). open은 기존 `aria-expanded="true"`·`#navLinks.open`·body `modal-open` 상태이며 새 색을 쓰지 않는다. 보이는 대상의 bounding box는 width·height 모두 ≥ 44px.
- typography hierarchy: 기존 텍스트·서체로 font-size·line-height·letter-spacing·margin 위계만 조정. font-weight는 BASE `css/style.css`에 이미 쓰인 값(400·500·600·700)만.
- line clamp: `.featured-blurb`와 `#projectGrid` 카드 blurb 요소에 screen에서 `-webkit-line-clamp: 3`(DOM 텍스트는 전문 유지, 모달·print는 전문).
- strength 장식 stripe: BASE의 `.strength-card::before` 장식 규칙은 제거해도 된다(선택).

### 16.3 제외(절대 반영 금지)

새 색상 값, 기존 색상의 역할·적용 위치 변경(특히 button/logo dark text `#0d0f12` 재배정, muted grey 재배정), 서체 family/weight asset 변경, 새 문구·수치·통계·섹션·이미지·아이콘, 프로젝트 순서·정보구조 변경, mockup placeholder의 실콘텐츠화. bundle의 hero `min-height` 변경·card thumb 비율 변경 등 허용 목록 밖 제안도 반영하지 않는다.

### 16.4 design guard (step 13, `tests/helpers/design-guard.js` + `tests/specs/design-guard.spec.js`)

입력: `git diff --no-renames --unified=0 <BASE> -- <파일>`(worktree 대 BASE, Git 읽기)의 patch, `git show <BASE>:css/style.css`·`<BASE>:css/themes.css`. 순수 함수 `checkCssPatch(patch, { baseCss, baseThemes })`, `checkMarkupPatch(patch, kind)`가 위반 문자열 배열을 반환한다(`n`은 patch 안 줄 번호).
- css/style.css 추가 줄: 색 리터럴(`#[0-9a-fA-F]{3,8}\b`, `rgb(`, `rgba(`, `hsl(`, `hsla(`, `hwb(`, `lab(`, `lch(`, `oklab(`, `oklch(`, `color-mix(`) → `color-literal:{n}`; 색을 담는 속성 선언(`color`, `background`, `background-color`, `background-image`, `border`·`border-top|right|bottom|left`(값이 `0`·`none`이면 허용), `border-color`, `outline`, `outline-color`, `fill`, `stroke`, `box-shadow`, `text-shadow`, `text-decoration-color`, `caret-color`, `accent-color`) → `color-prop:{n}`(단 `:focus-visible`을 포함한 선택자 블록의 `outline`·`outline-offset`은 BASE에 정의된 `var(--…)`만 쓰면 허용); `font-family`·`font:`·`@font-face`·`@import` → `font-asset:{n}`; `font-weight` 값이 BASE style.css의 font-weight 값 집합 밖 → `font-weight:{n}`; `url(` → `asset:{n}`; `content:` 값이 `none`·`''`·`""`·`normal` 밖 → `content:{n}`; `var(--x)`의 x가 BASE style.css·themes.css 정의와 추가된 비색 custom property 정의에 없으면 → `unknown-token:{n}`.
- css/style.css 삭제 줄: 색을 담는 속성 선언 삭제는 BASE에서 그 줄을 감싸는 가장 가까운 선택자에 `strength-card`가 있을 때만 허용, 아니면 `color-removed:{n}`.
- css/themes.css: patch가 비어 있지 않으면 `themes-changed`.
- index.html·js/main.js 추가 줄: `<img`, `<svg`, `<picture`, `<video`, `<i `, `<i>`, `<link`, `<script`, `<font`, `style=`, `.style.color`, `.style.background`, `.style.font` → `markup-asset:{n}`.
- 실제 저장소 검사는 모든 step의 전체 testCommand에서 실행되어 위반 0을 요구한다.

## 17. fresh runner preflight (승인 후, runner 시작 전, 하네스 수행)

1. stale 산출물 보존·제거(정확히 두 경로만): `tests/helpers/theme.js`, `tests/specs/smoke.spec.js`가 `git status --porcelain=v1 -z --untracked-files=all -- <path>` 결과 `??`(untracked)인지 확인 → 각 sha256 기록 → `/Users/hoon/.hermes/company/development/product-management/HOO-81-evidence/stale-step12-untracked-<UTC 타임스탬프>/`에 `cp -p`로 같은 파일명 복사 → 복사본 sha256이 원본과 같음을 확인 → `rm -- tests/helpers/theme.js tests/specs/smoke.spec.js`. `git clean`, `git reset`, `git restore`, `git checkout`, 와일드카드·디렉터리 삭제는 쓰지 않는다. 두 파일 내용은 승인된 구현으로 간주하지 않으며 step 14가 새로 작성한다.
2. 검증: 두 경로가 없고, HEAD가 plan commit과 같으며, `git status --porcelain=v1 --untracked-files=all`에 §11.5 하네스 런타임 면제 경로 밖 항목이 없다.
3. 이전 runtime snapshot: `tests/.tmp/start-snapshot-*.json`·`*-after.z`(현재 worktree에 step0~12 잔존 확인)는 삭제하지 않는다. 존재하면 목록·sha256을 위 evidence 디렉터리에 기록하고 runner 시작을 멈춰 하네스 조치(대표 별도 지시)를 받는다. 이 계획은 그 파일들의 삭제를 승인하지 않는다(S `reused`의 identity 불일치 방지 목적).
4. Harness 2.0.1 migration·Chromium 선행 HOO-100은 완료 상태이므로 선행 대기 조건이 아니다.
