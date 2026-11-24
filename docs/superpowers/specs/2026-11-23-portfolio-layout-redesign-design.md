# 포트폴리오 레이아웃·구조 리디자인 설계 (HOO-81)

- 날짜: 2026-11-23 (범위 변경 반영 2026-11-24) / 브랜치: `feat/HOO-81/portfolio-redesign` (base `main`)
- BASE: `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`
- 선행 시각 설계: `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md` (적용 완료, 계속 유효)
- 합의: Q1 Discord 1574196542901059632, Q2 1574197289084387379, Q3~Q5 1574197696334405756 (추천안 일괄 확정)
- 범위 변경: 대표 결정 `scope-change-claude-design-v27`·`scope-change-claude-design-v28-compact` — Claude Design 패턴(레이아웃·컴포넌트·간격·타이포 위계만)을 구현 기준으로 추가. 이전 Harness 2.0.1 계획·리뷰·승인은 재사용하지 않는다.
- 리뷰 반영 이력: 1~30차(Astra `1432c5274b33` ~ `review-resume-h201-b86b75bb881e-v26`)는 이 문서에 반영되어 있다(세부는 Git 이력). 31차 범위 변경. 32차 `review-resume-c57f750bfd7a-v29`: 규칙 구조 CSS guard, baseline(§8.5)·plan(§8.6) schema, component state 측정, `css/themes.css` 제외, §17 preflight 28개 경로. 33차 `review-resume-d032b938c536-v30`: 색 custom property 의존 그래프, CSS guard step 분할, step 6·8·32 완전 기술, baseline 오류 예 교정, component state 3분할. 34차 `review-resume-16ea71f32fac-v31`: 고정 S·C `parse_status`의 UTF-8 decode 실패 → `ValueError('bad status record')` 변환(설계 소유자 확정), step 6 합성 저장소 lock·조상 준비, 색 guard 3분할(step 14~16), step 재번호. 35차 `review-resume-6a5d82a7db93-v32`(record `6a5d82a7db9327845ac1b1a429b2113f20fff779984eecc4fc27f7eba059c7b7`): step 15 custom property 정의 제외, step 33·34 plan fixture를 FIXTURE_OK·FIXTURE_THEMES로 분리(§8.6). 36차 `review-resume-9c1f912760e7-v33`(record `9c1f912760e7aba49329496be4ce22a53612f3498c7796f636a018bd1ec817b0`): `COLOR_PROPS` 확장, 짝지어진 규칙의 새 색 선언 거부, BASE `font-family`·`font` 양방향 보존, hero 5:7 열 폭·1023/1024px 전환. 37차 `review-resume-4a273c5a72dc-v34`(record `4a273c5a72dc829f3819e328102c0d73235e74a36730dd2472acfbe16f5d0192`): 규칙 4 prop 제한 제거, 다중 진단 순서·중복 제거 고정, `matchesBaseRule` 공용 대응. 38차 `review-resume-07753db669ba-v35`(record `07753db669ba0d853347ef8f1315c077b1e18998cfe10e670989ffdeb6b6e593`): step 0 `HARNESS_IDENTITY` 동기화, `waitForFiniteAnimations`, 상태별 BASE 색 fixture. 39차 `review-resume-194334d2d96f-v36`(record `194334d2d96fbd34834e49b486a28bbd62e1d3a80584c8df95a2d3cea6b28275`): 공용 `measureStateSequence`로 대상마다 새 page·finally `mouse.up()`·`page.close()`·격리 회귀. 40차 `review-resume-e72caf27c285-v37`(record `e72caf27c28507c265ab6f5579f6ddfa3e1b8fabf14c7321e3144d934772abcd`, major 3): step 15 색 선언 순서 비교(`color-decl-reordered`)와 진단 순서 갱신, step 13 Rule `prelude` 추가와 step 17 `@import` 대응(file·chain·atRule·prelude, 변경·신규는 정확히 `asset:@import`), 기존 step 45를 state-sequence(45)·state-colors-fixture(46)·component-hover-active(47)로 분할하고 이후 step을 48~55로 재번호(§13, §16).
- Harness 실행 identity (중앙 release, `.harness/harness.lock.json`을 직접 읽어 확인): sourceCommit `e7a03919a460f975149f7c55343ca4b34d3d2352`, manifestHash `b627e6a5ce4a903c24c400927ca2b49a14d0bd59632c691b2a5c2d74c6c08372`, distributionVersion 2.0.1
- 진행 순서: materialize → 새 plan commit → Astra `gpt-6-astra` 계획 리뷰 CLEAN → 대표 exact 승인(§17 경로 목록 포함) → §17 preflight → fresh runner(step 0~55) → 전체 테스트 → exact-commit Astra 리뷰 CLEAN → feature push → OPEN PR. merge·deploy·main 직접 변경 없음.

## 1. 의도

2026-07-29 작업에서 색·서체·여백을 경영자의 절제 톤으로 정리했다. 이번 작업은 그 톤(색·서체·문구·수치)을 유지한 채 구조와 레이아웃을 다시 짠다. 레이아웃·컴포넌트·간격·타이포 위계의 기준은 Claude Design 패턴 보드(§16)다. 채용·영입 의사결정자가 30초 안에 (1) COO·CTO 포지셔닝, (2) 핵심 지표, (3) 대표 프로젝트 근거를 파악하게 한다.

## 2. 목표 / 비목표 / 실패 조건

- 목표: 1280×800 첫 화면에 이름·tagline·STATS 4개·대표 프로젝트 제목 3개. FINAL 섹션 순서(hero → Career → Projects → Strengths → About → Contact). §16 허용 패턴. 기능·콘텐츠 보존과 §16.3 제외 범위를 자동 테스트·범위 검사로 증명.
- 비목표: 색·서체 재설계, 빌드 도구 도입, 신규 기능, 배포·merge·main 직접 변경.
- 실패 조건(동작해도 실패): §7 예외 밖의 문구·수치·경력 사실 변경/생성, 빈 email·phone·social 채우기, 기존 기능 회귀, axe serious/critical 잔존, §16.3 제외 항목 반영, 그라데이션·글로우 장식 추가.

## 3. 현재 코드 사실 (read-first 대상)

- 저장소 지침: BASE에는 `README.md`만 있다. 하네스 파일 `CLAUDE.md`, `.harness/harness.lock.json`, `.harness/policy.json`, `.harness/install-state.json`, `.claude/`, `.codex/`, `pytest.ini`, `.python-version`, `.gitattributes`. `.venv/`는 하네스 venv.
- HEAD에는 기존 step 0~11 구현 commit(`tests/scripts/with-env.sh`, `start-snapshot.py`, `scope-snapshot.mjs`, `tests/helpers/synthetic-repo.js`, scope-snapshot spec들, `tests/package.json`·lock·`.gitignore`·`playwright.config.js`·`bootstrap.spec.js`)이 있다. 커밋된 `start-snapshot.py`는 2.0.0 identity이고 decode 변환이 없는 이전 `parse_status`라 §11.7 S 블록과 바이트가 다르다. 커밋된 `scope-snapshot.mjs`의 `HARNESS_IDENTITY`(sourceCommit·manifestHash·distributionVersion)도 2.0.0 값이다. 두 불일치는 step 0이 최초 전체 테스트 전에 동기화한다. worktree의 untracked `tests/helpers/theme.js`, `tests/specs/smoke.spec.js`와 `tests/.tmp/`의 이전 snapshot 26개는 §17에서 처리한다.
- `js/data.js`: 전역 const `PROFILE`, `STATS`(4), `CAREER`, `VIS_ACCENT`, `makeVisual`, `PROJECTS`(13, 모두 `detail`), `STRENGTHS`(6), `SKILLS`. `PROFILE.tagline`은 BASE에서 렌더링되지 않는다. email·phone·social.*은 빈 문자열. 대표 프로젝트 index: Motion AD=1, VigoRight(의료 AI/VR)=5, Lost Energy Intel=7.
- `index.html` hero: `section.hero#hero` > `div.container.hero-inner` > (`p.hero-eyebrow`, `h1.hero-name#heroName`, `h2.hero-role`, `p.hero-summary#heroSummary`, `div.hero-cta`, `ul.hero-stats#heroStats`) + `a.scroll-hint`(hero-inner 밖). 테마 토글 `#themeToggle.theme-toggle`. strengths 카드 `.strength-card`(BASE `css/style.css`에 장식 `.strength-card::before` 규칙). 무한 반복 장식 애니메이션: typing `.caret` blink, `.scroll-hint span` scrollDot.
- `js/main.js`: `setText(id, value)`. 렌더 대상 `#heroStats`, `#strengthsGrid`, `#timeline`(`.timeline-item` > `.timeline-period` + `.timeline-card`), `#projectGrid`, `#skillsGrid`, `#contactActions`. 카드: `article.project-card.has-detail[data-project=idx][tabindex=0][role=button]`.
- 모달: `div.modal#projectModal[hidden]` > `.modal-backdrop[data-modal-close]` + `.modal-dialog` > (`button.modal-close[data-modal-close]` + `div.modal-body#modalBody`). `#modalBody`: `.modal-visual`/`.modal-thumb`, `h3#modalTitle.modal-title`, `.modal-meta`, `p.modal-blurb`, `.modal-section`(갤러리 `.shot-zoom`). `openProjectModal(idx)`는 `lastFocused = document.activeElement` 후 닫기 버튼 포커스, body `modal-open`. 열기 `#projectGrid` 위임, 닫기 `[data-modal-close]` 또는 Esc(lightbox 우선).
- lightbox: `ensureLightbox()`가 `.lightbox[role=dialog]`(`button.modal-close` + `img`)를 만들고 `.shot-zoom`으로 연다. lightbox에만 Tab 고정 리스너가 있다.
- 기타: 스크롤스파이 id 배열(about, strengths, career, projects, contact). reveal `.reveal`→`.in`. typing `runTyping`(reduced-motion이면 `roles[0]`). 테마 localStorage `THEME_KEY`. 메뉴 `#menuToggle`, `#navLinks.open`, `aria-expanded`. `@media print`. Google Fonts Space Grotesk 링크 제거 금지.

## 4. 접근 방식

A(선택, Q1): 절제 톤 유지 + 레이아웃·구조 재구성. 레이아웃·컴포넌트·간격·타이포 위계는 §16 허용 항목만 적용한다.

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

- 카드 안에는 span과 텍스트만. 두 span은 `display: block`.
- 대표 카드와 grid 카드는 같은 `data-project`. 테스트 helper는 grid 카드를 `#projectGrid .project-card[data-project="N"]`로 한정한다.
- 함수: `renderFeaturedProjects(): void`(원본 순서로 `featured === true`만, 그리드 렌더 직후). `openProjectModal(projectIndex, triggerElement = document.activeElement)`(grid는 `(idx, card)`, `#heroFeatured` click 위임). `closeProjectModal()`은 모든 경로에서 `lastFocused`로 복귀.
- data.js: index 1, 5, 7의 `title:` 다음 줄에 `featured: true,` 총 3줄.
- 대표 카드의 색은 새 색 선언 없이, 기존 `.project-card` 색 규칙의 선택자 목록에 그 featured 대응 선택자(§16.4)를 추가하는 방식으로만 얻는다.

첫 화면 AC (desktop 1280×800, hero.spec.js 단독·통합 모두): `document.fonts.ready` 후 `scrollY === 0`. 대상 `#heroName`, `#heroTagline`, `#heroStats`, `.featured-title` 3개, 지표 item 4개(DOM 순서 = `STATS[0..3]`)마다 item·수치 요소(텍스트 norm = STATS 수치)·label 요소(텍스트 norm = STATS label); 셀렉터는 hero.spec.js 상수 `STAT_ITEM`, `STAT_VALUE`, `STAT_LABEL`. 각 대상: `toBeVisible()`, bbox w·h > 0, 자신과 모든 조상 visibility `visible`·opacity `1`(`expect.poll`), x ≥ 0, y ≥ 0, x+w ≤ 1280, y+h ≤ 800.

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
- `BaselineData`: BASE data.js 평가 결과(step 22). `StaticContent`: BASE index.html 정적 본문(step 23).

### 7.2 허용 예외
1. index 1, 5, 7의 `featured: true`
2. `kickers`는 BASE [01 — About, 02 — Strengths, 03 — Career, 04 — Projects, 05 — Stack &amp; Contact] 또는 FINAL [01 — Career, 02 — Projects, 03 — Strengths, 04 — About, 05 — Contact] 중 정확히 하나
3. `sectionTitles`는 BASE [소개, 업무상 강점, 경력 &amp; 창업, 프로젝트 &amp; 제품, 기술 스택 &amp; 연락처] 또는 FINAL [경력 &amp; 창업, 프로젝트 &amp; 제품, 업무상 강점, 소개, 연락처]. FINAL이면 `h3.subsection-title` 기술 스택 정확히 1개
4. nav·섹션 순서(`navLabels`는 정렬 비교)
5. skill-group 제목 heading level
6. axe remediation 그룹 step에서 위반 요소의 aria-*, role, alt, lang, tabindex, for 속성 변경(텍스트 불변)

### 7.3 helper 계약 (`tests/helpers/content.js`)
- `norm(s) = String(s).replace(/\s+/g, ' ').trim()`
- `BaselineData = { PROFILE, STATS, CAREER, VIS_ACCENT, PROJECTS, STRENGTHS, SKILLS }`
- `StaticContent`(모두 norm): `title`, `metaDescription`, `navLabels`(정렬), `heroEyebrow`, `ctaLabels`, `kickers`, `sectionTitles`, `sectionSubs`, `aboutParagraphs`(`.about-text p:not([id])`), `aboutPoints`, `aboutMetaTerms`, `contactHeading`, `contactText`, `footerNote`, `footerTop`
- step 22: `readLiveData(page)`, `normalizeFeatured(data)`. step 23: `extractStatic(page)`

### 7.4 회귀 spec (step 24, 25)
- step 24 `modal-regression.spec.js` + `tests/helpers/modal.js`. step 25 `ui-regression.spec.js` + `first-visit.spec.js`.
- `modal.js`: `GRID_CARD = '#projectGrid .project-card'`; `gridCard(page, N)` = 정확히 `page.locator('#projectGrid .project-card[data-project="' + N + '"]')`; `openFirstProjectByClick`, `openFirstProjectByEnter`; `closeVia(page, 'button'|'backdrop'|'esc')`(button `#projectModal .modal-close[data-modal-close]`, backdrop `{x:5, y:5}`); `expectFocused`; `modalTitle(page)`; `findProjectWithShots(page): number|null`(grid 카드만).

## 8. 접근성

### 8.1 axe
- wcag2a·wcag2aa serious/critical 0건. 시나리오 10개: page 3 viewport × 2 테마, modal × dark/light, lightbox × dark/light. `prepareForAxe` 통과 후에만 실행.

### 8.2 포커스 트랩 (step 49, 50)
- `trapFocus(container, { returnFocusTo? }): () => void` — 스택, 최상위만 Tab 순환, document Tab 핸들러 1개, `release()` 다중 호출 안전.
- step 49: 구현 + 모달 push/release. step 50: lightbox push(`.shot-zoom`), 모달 trap 일시정지·재개, 기존 lightbox Tab 리스너 제거, `:focus-visible` outline 검증.

### 8.3 axe 식별·도구

canonical target (step 26): `{ruleId}::{anchor}::{textSig}`. anchor: `[data-featured-card][data-project]`→`featured:{N}`, `[data-project]`→`project:{N}`, `[id]`→`#{id}`, landmark→태그명, 없으면 `document`. textSig: norm(textContent) → aria-label → alt → title → src 파일명, 숫자는 `#`, 80자 자름. alias: `## — Stack & Contact`→`## — Contact`, `기술 스택 & 연락처`→`연락처`.

entry key (step 30): `makeEntryKey({ scenario, project, ruleId })` = `${scenario}:${project}:${ruleId}`(빈 값·`:` 포함 throw). (key, target) 쌍이 위반 1건.

helper (`tests/helpers/axe.js`):
- step 26: `ALIASES`, `canonicalTargetInPage`, `canonicalFromDescriptor`, `runAxe(page, { include }) → Violation[]`
- step 30: `makeEntryKey`, `COLLECT_DIR`(`tests/.tmp/axe-collected`), `EXPECTED_FILES` 10개, `resolveCollectDir`, `resetCollected`, `writeCollected`, `mergeCollected({ collectDir, out })`(MergedEntry = §8.5의 앞 7필드, key 정렬), CLI `--reset`, `--merge [--dir] [--out]`.
- step 31: `BASELINE_PATH`, `COLLECTED_PATH`, `PLAN_PATH`, `FIX_FILES_BY_KIND`, `baselineExists`, `loadBaseline`, `resolveBaselineMode`(`check`/`pending`/throw, 환경변수 우회 없음), `validateBaseline`(§8.5 그대로), `checkRegression(violations, baseline, scenario, project)`(`new-key:{key}`, `new-target:{key}:{target}`), `assertEmptyFile`, CLI `--assert-empty`.
- step 32: `PROJECTION_FIELDS = ['key','scenario','project','ruleId','impact','targets','selectors']`, `projectEntry`, `compareCollectedBaseline(collected, baseline) → { ok, missingEntries: string[], extraEntries: string[], missingTargets: PlanTarget[], extraTargets: PlanTarget[], fieldMismatches: Array<{ key, field }> }`(missingEntries = collected에만 있는 key, extraEntries = baseline에만 있는 key, missingTargets = 같은 key에서 collected에만 있는 target, extraTargets = baseline에만 있는 target, fieldMismatches = 같은 key에서 scenario·project·ruleId·impact·selectors 중 다른 필드, 모두 정렬, ok = 다섯 배열이 모두 비었는가), CLI `--check-baseline-match [--collected] [--baseline]`(불일치 시 stderr에 `missing-entry:{key}`, `extra-entry:{key}`, `missing-target:{key}|{target}`, `extra-target:{key}|{target}`, `field-mismatch:{key}|{field}` 줄을 이 순서로, exit 1).
- step 33: `GROUP_ID_RE`, `loadPlan`, `validateRemediationPlan(plan, baseline, { coverage, requireEmpty })`(§8.6 그대로), CLI `--check-plan [--coverage] [--require-empty]`.
- step 34: `validateRemediationExecutable`(`blocked-group:{id}`, `text-change:{id}:{key}:{target}`, `empty-fixfiles:{id}`), CLI `--check-executable`(첫 줄 `Harness 재계획 필요: 실행 불가 remediation 그룹`).
- step 35: `checkGroupDone(collected, plan, id) → { done, remaining: PlanTarget[] }`, `checkCollectedCoverage → { ok, uncovered: PlanTarget[] }`, `countCollectedTargets`, CLI `--check-group-done <id>`, `--check-coverage`, `--assert-no-violations`(`--collected` 기본 `tests/.tmp/axe-current.json`).
- step 36: `checkCollectedRegression`, `prunePlan(plan, collected, baseline)`(§8.6 prune), CLI `--check-regression`, `--prune-plan`(회귀 실패 시 쓰지 않음, 통과 시 `JSON.stringify(plan, null, 2) + '\n'`).

실행 모드: 공통 `prepareForAxe` → `runAxe`. 수집(`AXE_COLLECT=1`) `writeCollected`만. 일반: `resolveBaselineMode()`; `check`면 checkRegression·validateBaseline(desktop-dark 1회)·plan 있으면 validateRemediationPlan(coverage false); `pending`이면 `test.skip(true, 'axe classification pending (step 38)')`.
- COLLECT_CHAIN: `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset && AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge [--out <f>]`
- REGRESSION_GATE: `sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-regression --collected tests/.tmp/axe-current.json`

단계: step 37 수집(`pending`으로 종료) → step 38 분류(§8.5·§8.6 계약으로만 생성, 예상 = 묶음별(2분 + target × 1분) + 6분, 20분 초과면 재계획) → step 39~51 새 key/target은 실패(색 변경 없이 그 step에서 해결) → step 52 gate(COLLECT_CHAIN(`--out tests/.tmp/axe-current.json`) → REGRESSION_GATE → `--prune-plan` → `--check-coverage` → `--check-plan` → `--check-executable`, 그룹이 남으면 하네스가 52와 53 사이에 `axe-remediation-{id}` 재계획) → step 53 recheck(+ `--require-empty`, `--assert-no-violations`) → step 54 finalize(baseline `[]`).
- 재계획 그룹 step: `--check-executable` 통과·`blocked === false`·`fixFiles.length >= 1`일 때만. allowedPaths = 그룹 fixFiles(index.json allowedPaths의 부분집합, `css/themes.css`가 있으면 생성하지 않음), 20분 이하, 첫 동작 `python3 -I tests/scripts/start-snapshot.py axe-remediation-{id}`, AC: COLLECT_CHAIN && REGRESSION_GATE && `--check-group-done {id}` && `npm --prefix tests test` && verify-scope && `scope-snapshot.mjs --check tests/.tmp/start-snapshot-axe-remediation-{id}.json --allow {fixFiles}`.

### 8.4 axe 시나리오 준비 (`tests/helpers/axe-prepare.js`)
- step 27: `PREPARE_PREFIX = 'prepareForAxe: '`, `prepareError(code, cause?)`, `withPrepareCode(code, fn)`, `preparePage(page, { timeoutMs = 10000 })`(`fonts-not-ready`, `reveal-hidden:{n}`).
- step 28: `MODAL_ROOT`, `MODAL_BODY_TEXT = '#modalBody .modal-blurb, #modalBody .modal-section'`, `assertContentLoaded(locator, timeoutMs, { textLocator = null })`(`content-not-loaded:img|svg|text`), `prepareModal(page, { projectIndex = 0 })`(`project-card-not-found:{N}`, `modal-not-open`).
- step 29: `prepareLightbox`(`no-shots-project`, `lightbox-not-open`), `prepareOverlay`(`unknown-scenario`), `prepareForAxe(page, { scenario, projectIndex? })`.
- 합성 fixture: 동작 모달 fixture(`window.__opens`·`__closes`·`__clicks`)와 handler 없는 fixture.

### 8.5 axe baseline schema (고정, step 31 이전 확정)

- 파일: JSON 배열. 원소는 key 오름차순(코드 유닛 비교), key 고유. 빈 배열 허용.
- BaselineEntry 필드는 정확히 `key, scenario, project, ruleId, impact, targets, selectors, fixes, fixFiles`(누락·여분 금지).
  - `scenario` ∈ `page|modal|lightbox`; `project` ∈ `mobile-dark`, `mobile-light`, `tablet-dark`, `tablet-light`, `desktop-dark`, `desktop-light`; `ruleId` 비어 있지 않고 `:` 없음; `key === makeEntryKey({ scenario, project, ruleId })`; `impact` ∈ `serious|critical`.
  - `targets`: 비어 있지 않은 문자열 배열, 고유, 오름차순. `selectors`: 문자열 배열, 고유, 오름차순.
  - `fixes`: targets와 같은 길이, `fixes[j].target === targets[j]`. Fix 필드는 정확히 `target, fixKind, fixFiles`. `fixKind` ∈ `css-token|css-rule|js-render|static-markup|text-change`. `fixFiles`는 `FIX_FILES_BY_KIND[fixKind]`와 정확히 같은 배열(css-token `["css/themes.css"]`, css-rule `["css/style.css"]`, js-render `["js/main.js"]`, static-markup `["index.html"]`, text-change `[]`).
  - entry `fixFiles`: 모든 fixes의 fixFiles 합집합, 고유, 오름차순(전부 text-change면 `[]`).
- `validateBaseline(baseline) → string[]` 오류 형식(발견 순서): `baseline: not-array`; `baseline[{i}]: not-object`; `baseline[{i}]: fields missing=[a,b] extra=[c]`; `baseline[{i}]: bad-scenario|bad-project|bad-ruleId|key-mismatch|bad-impact`; `baseline[{i}]: targets empty|not-string|duplicate|unsorted`; `baseline[{i}]: selectors not-string|duplicate|unsorted`; `baseline[{i}]: fixes count`; `baseline[{i}].fixes[{j}]: not-object|fields missing=[..] extra=[..]|target-mismatch|bad-fixKind|fixFiles-mismatch`; `baseline[{i}]: fixFiles union-mismatch`(fix 오류가 하나도 없는 entry에서만 판정); `baseline: duplicate-key {key}`; `baseline: unsorted`. 오류 없으면 `[]`.
- 정상 예(아래 FIXTURE_THEMES와 같은 내용):

```
[
  {
    "key": "page:desktop-dark:color-contrast",
    "scenario": "page",
    "project": "desktop-dark",
    "ruleId": "color-contrast",
    "impact": "serious",
    "targets": ["color-contrast::#career::## — Career"],
    "selectors": ["#career .section-kicker"],
    "fixes": [{ "target": "color-contrast::#career::## — Career", "fixKind": "css-token", "fixFiles": ["css/themes.css"] }],
    "fixFiles": ["css/themes.css"]
  }
]
```

- 오류 예 A: 위 entry에 `"note": "x"` 추가 → 정확히 `["baseline[0]: fields missing=[] extra=[note]"]`.
- 오류 예 B: fix의 `fixKind`만 `css-rule`로 바꾸고 fix `fixFiles`와 entry `fixFiles`는 유지 → 정확히 `["baseline[0].fixes[0]: fixFiles-mismatch"]`.
- 오류 예 C: fix는 정상 그대로 두고 entry `fixFiles`만 `["css/style.css"]`로 바꿈 → 정확히 `["baseline[0]: fixFiles union-mismatch"]`.
- step 38은 이 계약으로만 baseline을 생성하고, step 31·32·36·54가 같은 계약을 쓴다.

### 8.6 remediation plan schema (고정)

- 파일: 객체, 필드는 정확히 `groups`. `groups`: 배열, id 오름차순, id 고유.
- Group 필드는 정확히 `id, targets, fixFiles, difficulty, estMinutes, blocked, reason`.
  - `id`: `/^[a-z0-9]+(?:-[a-z0-9]+)*$/`.
  - `targets`: 비어 있지 않은 PlanTarget 배열. PlanTarget 필드는 정확히 `key, target`(둘 다 문자열). (key, target) 오름차순(key 먼저), 그룹 안 중복 없음. 각 PlanTarget은 baseline에 그 key의 entry가 있고 그 entry `targets`에 target이 있어야 한다. 같은 PlanTarget이 두 그룹에 있으면 안 된다.
  - `fixFiles`: 그룹 PlanTarget들에 대응하는 baseline fix의 fixFiles 합집합, 고유, 오름차순.
  - `difficulty` ∈ `low|medium|high`. `estMinutes`: 정수 1~20.
  - `blocked`: boolean. `reason`: 문자열; `blocked === true`면 비어 있지 않고 `false`면 `""`. text-change fix가 있거나 fixFiles에 `css/themes.css`가 있으면 `blocked === true`, reason은 각각 `text change excluded` / `color change excluded (HOO-81 §16.3)`(둘 다면 그 순서로 `; ` 연결). 색 값·색 역할 변경이 필요한 css-rule 그룹도 reason `color change excluded (HOO-81 §16.3)`로 blocked.
- coverage(`--coverage`): baseline의 모든 (key, target)이 정확히 한 그룹에 있다. requireEmpty: `groups.length === 0`.
- `validateRemediationPlan` 오류 형식: `plan: not-object`, `plan: fields missing=[..] extra=[..]`, `plan: groups not-array`, `groups[{i}]: not-object|fields missing=[..] extra=[..]|bad-id|targets empty|fixFiles-mismatch|bad-difficulty|bad-estMinutes|bad-blocked|reason-required|reason-must-be-empty|blocked-required`, `groups[{i}].targets[{j}]: not-object|fields missing=[..] extra=[..]|unknown-target`, `groups[{i}]: targets duplicate|targets unsorted`, `plan: duplicate-id {id}`, `plan: groups unsorted`, `plan: target-in-multiple-groups {key}|{target}`, `plan: uncovered {key}|{target}`, `groups: expected empty, got {n}`.
- prune(`prunePlan`): collected에 없는 PlanTarget 제거 → fixFiles 재계산 → 빈 그룹 삭제 → 나머지 필드·순서 유지, 추가 없음. `checkGroupDone`·`checkCollectedCoverage`도 PlanTarget 단위로 비교한다.
- 테스트 fixture(step 33·34 공용, spec 안 상수):
  - FIXTURE_OK(정상 plan 검증 전용 baseline, 정확히 1 entry): `{ "key": "page:desktop-dark:aria-allowed-attr", "scenario": "page", "project": "desktop-dark", "ruleId": "aria-allowed-attr", "impact": "serious", "targets": ["aria-allowed-attr::#heroFeatured::대표 프로젝트"], "selectors": ["#heroFeatured"], "fixes": [{ "target": "aria-allowed-attr::#heroFeatured::대표 프로젝트", "fixKind": "static-markup", "fixFiles": ["index.html"] }], "fixFiles": ["index.html"] }`
  - FIXTURE_THEMES(`css/themes.css` blocked 검증 전용 baseline): §8.5 정상 예와 같은 내용.
  - 두 fixture는 `validateBaseline`이 `[]`를 반환해야 한다.
- 정상 예(FIXTURE_OK 기준, coverage 포함 통과): `{ "groups": [ { "id": "hero-featured-aria", "targets": [ { "key": "page:desktop-dark:aria-allowed-attr", "target": "aria-allowed-attr::#heroFeatured::대표 프로젝트" } ], "fixFiles": ["index.html"], "difficulty": "low", "estMinutes": 6, "blocked": false, "reason": "" } ] }`
- 오류 예(FIXTURE_OK 기준): target을 문자열로 쓰면 정확히 `groups[0].targets[0]: not-object`; `blocked: true`, `reason: ""`이면 정확히 `groups[0]: reason-required`.
- themes 예(FIXTURE_THEMES 기준): `{ "groups": [ { "id": "career-kicker-contrast", "targets": [ { "key": "page:desktop-dark:color-contrast", "target": "color-contrast::#career::## — Career" } ], "fixFiles": ["css/themes.css"], "difficulty": "low", "estMinutes": 5, "blocked": false, "reason": "" } ] }` → 정확히 `["groups[0]: blocked-required"]`; `blocked: true`, `reason: "color change excluded (HOO-81 §16.3)"`이면 `[]`.

## 9. 반응형 (§16 tokens 반영)

| 대상 | 375 | 768 | 1280 |
|---|---|---|---|
| hero `.hero-inner` | 1열(DOM 순서, 좌측 정렬) | 1열 | 2열 grid(§16.2) |
| `#heroStats` | 2×2 | 4×1 | 4×1(전체 폭) |
| `#heroFeatured` | 1열 | 2열 | 3열(전체 폭) |
| `#projectGrid` | 1열 | 2열 | 3열 |
| `#strengthsGrid` | 1열 | 2열 | 3열 |
| Career `.timeline-item` | 세로 | 가로(top 차 < 24px) | 가로 |
| 섹션 padding-top·bottom(career~contact) | 64px | 80px | 96px |
| card gap(`#heroFeatured`, `#projectGrid`, `#strengthsGrid` row·column) | 24px | 24px | 24px |

가로 스크롤 없음. hero 2열 전환 기준은 viewport 너비 1024px 이상(1023px 1열, 1024px 2열).

## 10. 인쇄와 PDF

- 히어로·대표 카드·본문 visible·opacity 1, 보이는 `.reveal` 비어 있지 않음. 토글·메뉴·scroll-hint·`#projectModal` display none. 인쇄에서는 line clamp 해제(blurb 전문).
- A(새 페이지): `.lightbox` 없거나 display none. B(overlay 열림): screen에서 `.lightbox` visible → print → `.lightbox`·`#projectModal` display none.
- PDF > 10240바이트, `buf.toString('latin1').match(/\/Type\s*\/Page\b/g)` 개수 ≥ 1.

## 11. 검증 체계 (Q5)

### 11.1 경로
- tracked source(빌더 허용): 사이트 `index.html`, `css/style.css`, `js/main.js`, `js/data.js`; tests `tests/package.json`, `tests/package-lock.json`, `tests/.gitignore`, `tests/playwright.config.js`, `tests/helpers/**`, `tests/specs/**`, `tests/fixtures/**`, `tests/scripts/**`(fixtures는 step이 명시한 파일만). `css/themes.css`는 읽기·guard 대상이며 빌더 허용 경로가 아니다(색 변경은 별도 재계획만).
- runtime(추적 금지): `tests/node_modules/**`, `tests/.npm-cache/**`, `tests/.pw-browsers/**`, `tests/.tmp/**`, `tests/test-results/**`, `tests/playwright-report/**`, 최종 step만 `tests/screenshots/**`.
- Harness managed·policy·lock·state 파일과 §16의 외부 evidence는 두 목록 모두에서 제외한다.
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

npm·node·playwright는 모두 이 래퍼로 실행한다. 하네스 testCommand(모든 step 공통): `sh tests/scripts/with-env.sh npm --prefix tests test`.

### 11.3 tests/package.json
- devDependencies `@playwright/test`, `@axe-core/playwright`. scripts: `test` `playwright test`, `browsers:install` `playwright install chromium`, `verify-scope` `node scripts/verify-scope.mjs`, `verify-scope:selftest` `node scripts/verify-scope.mjs --self-test`, `fixtures` `node scripts/make-fixtures.mjs`.

### 11.4 Playwright와 콘솔 수집
- webServer `python3 -m http.server 4173 --bind 127.0.0.1`(cwd `..`, reuseExistingServer), baseURL `http://127.0.0.1:4173`, testDir `./specs`, reporter list, retries 0, outputDir `./test-results`.
- 직렬화(고정): `workers: 1`, `fullyParallel: false`. bootstrap.spec.js가 검증한다.
- projects 6개: {mobile 375×812, tablet 768×1024, desktop 1280×800} × {dark, light}, 이름 `{viewport}-{theme}`.
- 테마 fixture는 `THEME_KEY`가 null일 때만 주입. 최초 방문 검사는 fixture 없는 별도 context.
- `collectConsoleErrors(page)`: 즉시 listener, pageerror 전부, console.error는 Google Fonts 두 도메인만 제외, `finish()`는 networkidle 후 `{ pageErrors, consoleErrors }`.

### 11.5 `tests/scripts/verify-scope.mjs`
- step 20 경로: `GIT_DIFF_PATH_ARGS = ['--no-renames', '--name-only']`, `GIT_DIFF_PATCH_ARGS = ['--no-renames', '--unified=0']`(data.js 4구간). `collectInput({ git = runGit })`(Git 읽기만). 경로 정책: 빌더 허용 = §11.1 tracked(`css/themes.css` 변경은 위반). 하네스 소유(`CLAUDE.md`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`, `.claude/**`, `.codex/**`, `.harness/harness.lock.json`, `.harness/policy.json`, 이 설계 문서, 레거시 `scripts/**`·`templates/**`·`harness-manifest.json`)은 committed 면제·미커밋 위반. 하네스 런타임 면제: 위 두 `.harness` 파일 외 `.harness/**`, `.venv/**`, `phases/HOO-81-portfolio-redesign/**`. runtime 경로 추적·루트 package.json은 위반.
- step 21 내용: `checkDataJsDiff(patch, { requireExactly3 })`, `--final`, index.html 3종 `Space+Grotesk`, gitignore(index, worktree).

### 11.6 통합 AC와 재검증 모드
- 모든 step: 첫 동작 §11.7 시작 snapshot, 종료 시 기본 testCommand 통과, AC 마지막 범위 gate.
- 종료 gate: step 0~11은 S `reused` 직후 inline C. step 12부터(재계획 `axe-remediation-{id}` 포함) CLI `scope-snapshot.mjs --check`.
- step 20 이후 기본: 자기 spec 단독 → `npm --prefix tests test` → `verify-scope` → 범위 gate. 사이트 CSS·마크업을 바꾸는 시각 step(39~44, 47, 48)과 55는 `python3 -I tests/scripts/design-intake-check.py`와 GUARD_SPECS(`css-parse.spec.js color-vocab.spec.js design-guard-color-rules.spec.js design-guard-color.spec.js design-guard-css.spec.js design-guard.spec.js`)를 AC에 포함한다.
- 재검증 모드(step 0~11): HEAD에 그 step의 tracked 허용 파일이 이미 commit되어 있으면 재검증 모드. 시작 snapshot → AC 실행 → 통과면 파일을 바꾸지 않고 범위 gate 실행, 로그 `reverify step{N}: no-op` → 불일치면 그 step의 허용 파일 안에서만 고쳐 통과시키고 로그 `reverify step{N}: fixed <파일 목록>`. 재검증 모드의 inline C 세 번째 인자(require-absent)는 `''`. step 0의 `step0 start clean` 조건은 최초 구축에만 적용. 기능 추가 없음.

### 11.7 시작 snapshot과 범위 gate

규칙:
- RUNTIME 접두어: §11.1 runtime 7개. SKIP = RUNTIME + `.git/` + `.venv/`. EXEMPT: `.harness/`, `.venv/`, `phases/HOO-81-portfolio-redesign/` (GUARDED `.harness/harness.lock.json`, `.harness/policy.json`은 면제 아님).
- 기록 대상 = status의 path·origPath ∪ `git ls-files -z` ∪ walk의 `tests/` 아래 파일(C·takeCurrent는 시작 snapshot files 키 포함) − SKIP. 값: regular file sha256, 없음 null.
- 저장소 상대 경로 계약(`rel_ok` = `isRepoRelative`): 문자열, 비어 있지 않음, NUL 없음, 런타임 path API 기준 절대 경로 아님, 구성요소가 비거나 `.`·`..`가 아님. 적용: snapshot `files` key(C는 `xy` key도), status parser의 path·origPath. 위반은 접근 없이 거부: S 생성 `bad git status`, S 재사용·loader `bad start snapshot: paths: <snapshot>`, C는 snapshot key `bad start snapshot: paths: <snapshot>`·status `bad git status`, CLI·`runCheck`는 loader 오류를 code 1로.
- status parser 계약(S·C·JS 동일): NUL 분할 후 마지막 빈 원소 하나만 버림; 각 레코드 길이 ≥ 4·세 번째 바이트 공백(빈 레코드 포함 위반은 형식 오류); XY·path·origPath는 엄격 UTF-8(디코드 실패는 형식 오류 — Python 본문은 `UnicodeDecodeError`를 잡아 `ValueError('bad status record')`로 다시 올린다); X 또는 Y가 `R`·`C`면 비어 있지 않은 다음 원소가 origPath(아니면 형식 오류); 경로 계약 위반은 경로 오류. Python `ValueError('bad status record')`/`ValueError('bad path')`, JS `Error('bad status record: …')`/`Error('bad path: …')`. S 생성 분기와 C는 모든 `ValueError`를 정확히 `bad git status`로 종료. S와 C의 `parse_status` 정의는 아래 블록 그대로 바이트 동일하며 설계 소유자만 바꾼다.
- projectRoot 유형: toplevel(또는 `root`)을 lstat해 `dir`가 아니면 `symlink:`/`missing:`/`non-regular:{root}`로 즉시 실패, 그다음 realpath 비교.
- 경로 유형 계약(lstat 전용): `kind(p)` ∈ `missing|file|dir|symlink|other`; `check(p, 허용 leaf)`는 조상부터 lstat. 허용 leaf: 기록 대상 `missing|file`; lock `file`; S의 `tests/.tmp` `missing|dir`·snapshot `missing|file`; C·loader·CLI의 snapshot `file`; after.z `missing|file`.
- 읽기 `O_RDONLY | O_NOFOLLOW | O_NONBLOCK` + fstat regular(아니면 `unsafe path: non-regular:{p}`). 쓰기: snapshot `O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW`, after.z는 unsafe 없을 때만 직전 `check` 후 `O_WRONLY | O_CREAT | O_TRUNC | O_NOFOLLOW | O_NONBLOCK`.
- 실행 전제(trusted-agent canary): snapshot 생성부터 종료 gate까지 다른 프로세스가 projectRoot 내부 경로·조상·snapshot·after.z를 생성·교체·삭제하지 않는다. 동시 경로 교체 공격은 범위 밖, dirfd/openat·경쟁 주입 테스트 없음.
- symlink 금지: SKIP 밖의 모든 symlink 엔트리(SKIP 디렉터리 엔트리 자체 포함) `symlink:{p}`, 어떤 면제도 없음, 대상은 따라가지 않는다.
- 실행 순서 — S: step id → toplevel → projectRoot 유형 → realpath → walk → status(parser)·ls-files → 경로 유형 검사(실패 `unsafe path: {정렬 목록}`) → BASE verify → lock → identity → 재사용 검증 또는 생성. C: toplevel → projectRoot → realpath → snapshot·after.z 유형 → snapshot 읽기·형식·key 경로 계약 → status(parser, 위반이면 이후 단계 없이 `bad git status`) → walk → 유형 검사 → unsafe 없을 때만 hash → unsafe면 after.z 미접촉 exit 1 → 판정 → after.z 재검사·쓰기 → 결과.
- 판정: hash 다르면 `tests-changed:{p}`/`outside-tests:{p}`, hash 같고 xy 다르면 `status-changed:{p}`, 새 RUNTIME status `runtime-visible:{p}`, require-absent 위반 `snapshot-not-first:{p}`. 순서: snapshot-not-first → 정렬 unsafe → 경로 오름차순 변경 → runtime-visible.
- Git은 `status`, `ls-files`, `rev-parse` 읽기만. python3 표준 라이브러리만.

schema (strict, schemaVersion 1): 모든 깊이의 중복 key·`NaN`·`Infinity`는 `invalid json`; 키 집합 정확히 `schemaVersion, stepId, projectRoot, head, base, harness, statusZHex, xy, files`; schemaVersion은 최상위 한 번·token `1`; stepId `step{N}`|`axe-remediation-{id}`|`parity-{숫자}`; harness = 중앙 3값 + `lockSha256`; statusZHex 짝수 길이 소문자 hex·parser 계약; xy = 파싱 결과; files 값 64hex|null, key 경로 계약, status 비SKIP 경로 포함. 검사 순서: invalid json → keys → schemaVersion → (loader만 stepId) → statusZHex → status parse/paths → xy → files → paths → files/status. 메시지 `bad start snapshot: {범주}: <path>`, `start snapshot identity mismatch: {field}`, `unsafe path: {…}`.

`scanJsonTopLevel(rawText)`(JS, step 2): 공백 skip, 문자열 slice(백슬래시 다음 1문자 skip), 스택, key `JSON.parse` 디코드·중복 throw `duplicate key: {key}`, 깊이 1 값 원문 token, 최상위 비객체 `[]`.

최초·재시도: 없으면 exclusive create(`created`), 있으면 재수집 없이 schema·identity 비교 후 `reused` 또는 exit 1. 기존 snapshot을 덮어쓰기·삭제·재기준화하지 않는다.

스크립트 S — step 0은 어떤 파일보다 먼저 `python3 -I - step0 <<'PY'` + 아래 본문 + `PY`로 실행하고, 같은 본문을 바이트 그대로 `tests/scripts/start-snapshot.py`에 저장한다. step 1 이후 첫 동작은 `python3 -I tests/scripts/start-snapshot.py step{N}`. 빌더는 이 본문과 이 문서를 바꾸지 않는다.

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
        try:
            code = rec[:2].decode()
            p = rec[3:].decode()
        except UnicodeDecodeError:
            raise ValueError('bad status record')
        if not rel_ok(p):
            raise ValueError('bad path')
        xy[p] = code
        if code[0] in 'RC' or code[1] in 'RC':
            if i >= len(recs) or not recs[i]:
                raise ValueError('bad status record')
            try:
                o = recs[i].decode()
            except UnicodeDecodeError:
                raise ValueError('bad status record')
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

inline 범위 검사 C — step 0~11 종료 검사. 반드시 직전에 S `reused`를 통과한 뒤 실행한다. 실행: `python3 -I - <stepId> '<allow 쉼표 목록>' '<require-absent 쉼표 목록>' <<'PY'` + 아래 본문 + `PY`. 아래 본문이 확정본이다: `parse_status` 정의는 S와 바이트 동일하며 빌더는 수정·재작성·우회하지 않는다.

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
        try:
            code = rec[:2].decode()
            p = rec[3:].decode()
        except UnicodeDecodeError:
            raise ValueError('bad status record')
        if not rel_ok(p):
            raise ValueError('bad path')
        xy[p] = code
        if code[0] in 'RC' or code[1] in 'RC':
            if i >= len(recs) or not recs[i]:
                raise ValueError('bad status record')
            try:
                o = recs[i].decode()
            except UnicodeDecodeError:
                raise ValueError('bad status record')
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

설계 블록 추출 규칙(테스트용, 읽기 전용): `스크립트 S`로 시작하는 줄 다음 첫 fenced code block이 S 본문, `inline 범위 검사 C`로 시작하는 줄 다음 첫 fenced code block이 C 본문(여는·닫는 ``` 줄 제외, 끝 개행 1개 포함). 함수 정의 추출: `def <이름>(` 줄부터 다음 들여쓰기 없는 줄 직전까지. 같은 방식으로 `### 16.1`의 첫 fenced block이 intake fixture JSON이다.

S·C exec harness(테스트 전용): `python3 -I -c '<harness>'`가 본문을 받아 `subprocess.run`(`rev-parse --show-toplevel`은 지정 경로, `status`는 지정한 bytes, 그 밖 git은 기록 후 예외), `os.lstat`·`os.walk`·`os.open`·`os.makedirs`·`builtins.open`을 기록용 래퍼로 감싸 `exec`하고 `SystemExit` 메시지·그 밖 예외 유형·호출 기록을 JSON으로 출력한다.

비교 도구 `tests/scripts/scope-snapshot.mjs` (S·C와 같은 판정, step별 추가만): step 1 상수(`HARNESS_IDENTITY` = S의 `HARNESS`와 같은 sourceCommit·manifestHash·distributionVersion 3값 포함)·`UnsafePathError`·`checkRoot`·`pathKind`·`checkPath`·`readRegular`; step 2 `isRepoRelative`·`parseStatusZ`(엄격 UTF-8)·`statusXyMap`·`scanJsonTopLevel`·`isSchemaVersion1`; step 3 `loadStartSnapshot`; step 4 `scanProject`·`hashPath`·`takeCurrent`; step 5·6 코드 없음; step 7 `computeIdentity`·`checkIdentity`·`diffAgainstStart`·`classifyChanges`·`checkRuntimeVisible`·`checkSnapshotFirst`·`evaluateGate`; step 8 `writeAfterZ`·`runCheck(opts, deps)`(deps `{ git, fs, root, impl? }`; `impl`은 테스트 전용으로 `checkRoot`, `loadStartSnapshot`, `computeIdentity`, `checkIdentity`, `takeCurrent`, `writeAfterZ`, `evaluateGate`를 바꿔 끼우는 객체, 없으면 실제 함수)·CLI `--check <start.json> --allow <list> [--require-absent <list>]`(인자 오류 exit 2); step 9~11 코드 없음. `HARNESS_IDENTITY` 3값은 step 0이 S와 함께 2.0.1로 동기화한다.

테스트 격리 규칙: 실제 저장소에는 runtime 경로(`tests/.tmp/start-snapshot-parity-{숫자}.json`과 after.z, `tests/.tmp/snapshot-probes/__retry_probe.txt`, `tests/.tmp/status-harness-<pid>/`, `tests/.tmp/design-intake-<pid>/`, `tests/.tmp/state-colors-<pid>/`)만 쓴다. 비runtime 검증은 합성 저장소 `tests/.tmp/synthetic-repos/<pid>/`(+`<pid>-outside`, `<pid>-link`, `<pid>-file`)에서 한다. subprocess timeout 10초(브라우저를 띄우는 `make-state-colors.mjs`는 60초).

## 12. 변경 허용 경로와 운영 경계

- index.json allowedPaths: `index.html`, `css/style.css`, `js/main.js`, `js/data.js`, `tests/`. `css/themes.css`, Harness managed·policy·lock·state, 외부 evidence는 제외. 각 step의 tracked 허용 파일 = 범위 gate `--allow`.
- `index.html` 구조 변경은 step 39·40·42만. 속성 변경은 remediation 그룹 step만 허용하며 예외는 step 42의 두 가지: (a) `.scroll-hint` `href`를 `#career`로, (b) §6 표대로 section `class`.
- 빌더 허용 명령: Git 읽기(rev-parse, diff, show, ls-files, ls-tree, status, log, `-w` 없는 hash-object), §11.7 snapshot·검사, §16.1 intake 검사(외부 evidence 읽기 전용). 하네스 전용: 프로젝트 저장소 Git 상태 변경, Harness 운영 명령, §17 preflight. main 직접 변경·merge·deploy 금지.
- 합성 저장소 예외: `tests/.tmp/synthetic-repos/<pid>/`에서만 `git -C <dir> init -q`, `add -A`/정확한 경로 add, `-c user.name=t -c user.email=t@example.invalid commit -q -m <msg>`.
- 빌더 수정 금지: `CLAUDE.md`, `docs/**`(이 설계 문서와 고정 S·C 본문 포함), `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`, `css/themes.css`, 시작 snapshot 파일, 외부 evidence.

## 13. Step 목록 (각 20분 이하, snapshot·gate·검증·디버깅 포함)

| # | name | 예상 | 종료 gate |
|---|---|---|---|
| 0 | tests-env-bootstrap (재검증) | 19 | S reused + C |
| 1 | scope-snapshot-paths (재검증) | 17 | S reused + C |
| 2 | scope-snapshot-parse (재검증) | 19 | S reused + C |
| 3 | scope-snapshot-loader (재검증) | 19 | S reused + C |
| 4 | scope-snapshot-state (재검증) | 19 | S reused + C |
| 5 | scope-snapshot-symlink (재검증) | 18 | S reused + C |
| 6 | scope-snapshot-special-files (재검증) | 19 | S reused + C |
| 7 | scope-snapshot-identity (재검증) | 18 | S reused + C |
| 8 | scope-snapshot-cli (재검증) | 18 | S reused + C |
| 9 | scope-snapshot-parity-core (재검증) | 19 | S reused + C |
| 10 | scope-snapshot-parity-paths (재검증) | 17 | S reused + C |
| 11 | scope-snapshot-parity-artifacts (재검증) | 19 | S reused + C |
| 12 | claude-design-intake | 15 | CLI (첫 CLI gate) |
| 13 | css-parser | 18 | CLI |
| 14 | color-vocab-graph | 17 | CLI |
| 15 | design-guard-color-rules | 20 | CLI |
| 16 | design-guard-color-tokens | 17 | CLI |
| 17 | design-guard-type-asset | 19 | CLI |
| 18 | design-guard-integration | 15 | CLI |
| 19 | tests-browser-smoke | 15 | CLI |
| 20 | scope-paths | 19 | CLI |
| 21 | scope-content | 19 | CLI |
| 22 | content-data-baseline | 16 | CLI |
| 23 | content-static-baseline | 17 | CLI |
| 24 | modal-regression | 18 | CLI |
| 25 | ui-regression | 17 | CLI |
| 26 | axe-canonical | 19 | CLI |
| 27 | axe-prepare-page | 15 | CLI |
| 28 | axe-prepare-modal | 18 | CLI |
| 29 | axe-prepare-lightbox | 19 | CLI |
| 30 | axe-collect-tooling | 19 | CLI |
| 31 | axe-baseline-regression | 19 | CLI |
| 32 | axe-baseline-projection | 17 | CLI |
| 33 | axe-remediation-plan-schema | 19 | CLI |
| 34 | axe-plan-executable | 15 | CLI |
| 35 | axe-current-checks | 17 | CLI |
| 36 | axe-regression-prune | 19 | CLI |
| 37 | axe-collect | 17 | CLI |
| 38 | axe-classify | ≤20 (초과 시 재계획) | CLI |
| 39 | featured-projects | 19 | CLI |
| 40 | hero-first-screen | 20 | CLI |
| 41 | hero-two-column | 19 | CLI |
| 42 | section-structure | 19 | CLI |
| 43 | section-layout | 17 | CLI |
| 44 | component-hit-open | 19 | CLI |
| 45 | state-sequence | 17 | CLI |
| 46 | state-colors-fixture | 18 | CLI |
| 47 | component-hover-active | 16 | CLI |
| 48 | component-clamp-stripe | 15 | CLI |
| 49 | focus-trap-modal | 17 | CLI |
| 50 | focus-trap-lightbox | 17 | CLI |
| 51 | print-pdf | 17 | CLI |
| 52 | axe-remediation-gate | 18 | CLI |
| (재계획) | axe-remediation-{id} | ≤20 | CLI |
| 53 | axe-remediation-recheck | 18 | CLI |
| 54 | axe-finalize | 16 | CLI |
| 55 | final-verification | 17 | CLI |

각 step의 선행은 그보다 작은 번호 전부(53은 재계획 그룹 포함).

## 14. 빌더 재량

§16.2 tokens 안의 비색 타이포 세부값, CSS 클래스 구조(명시된 id·data 속성·클래스 유지), 테스트 helper 내부 구조.

## 15. step 공통 절차

1. read-first: `CLAUDE.md`, `README.md`, 하위 `CLAUDE.md`·`AGENTS.md`, 선행 시각 설계, 지정 절. 선행 step completed 확인.
2. read-only: §12 수정 금지 목록.
3. 명령 권한: §12.
4. 실행: npm·node는 래퍼로, Playwright `workers: 1`, §11.7 실행 전제 준수.
5. 첫 동작: 시작 snapshot(`python3 -I tests/scripts/start-snapshot.py step{N}`, step 0은 heredoc S). `created`/`reused`가 아니면 중단·보고.
6. runtime 쓰기 기본 R0: `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`.
7. 공통 수정 금지: step 허용 목록 밖 파일, 이전 step 함수 동작, 이전 step spec, 시작 snapshot, 비runtime symlink·특수 파일, §16.3 제외 항목.
8. 종료 조건: 기본 testCommand 통과 + AC 마지막 범위 gate 통과.
9. step 0~11은 §11.6 재검증 모드.

## 16. Claude Design 반영

### 16.1 evidence와 intake

- 연결 검증: Claude Code 대화형 `/design`이 실제 인식되어 artifact까지 생성됐다. Claude Design 전용 MCP는 없고 이번 실행은 handoff ID 없이 로컬 bundle만 생성됐다.
- summary: `/Users/hoon/.hermes/company/development/product-management/HOO-81-evidence/claude-design-pattern-board-summary-2026-11-24.md`
- bundle dir: `/Users/hoon/.hermes/company/development/product-management/HOO-81-evidence/claude-design-pattern-board-2026-11-24/` — 정확히 9개 파일(아래 fixture의 `files`).
- 외부 경로는 allowedPaths·범위 gate 대상이 아니며 읽기 전용이다. bundle 참조 전에 항상 `python3 -I tests/scripts/design-intake-check.py`(DESIGN_HASH_CHECK)로 `design-intake: OK`를 확인한다. mockup 문구·숫자·placeholder는 콘텐츠로 쓰지 않는다.
- `tests/fixtures/claude-design-intake.json` (step 12, 파싱 결과가 아래와 deep-equal):

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

- `tests/scripts/design-intake-check.py [--fixture <path>]`(step 12, 표준 라이브러리, 쓰기 없음, 기본 fixture `tests/fixtures/claude-design-intake.json`): `summaryPath`·`bundleDir`·각 파일 lstat이 symlink·non-regular면 `design-intake: unsafe:{path}` → `os.listdir(bundleDir)` 정렬 목록 ≠ `files` key 9개면 `design-intake: files mismatch` → 각 sha256 ≠ fixture면 `design-intake: hash mismatch:{name}` → summary에 `` `{name}` — `{sha}` `` 줄이 없으면 `design-intake: summary mismatch:{name}` → 모두 exit 1. 통과 시 `design-intake: OK`, exit 0.

### 16.2 허용 패턴 (구현 기준)

- Explore surface: PROJECTS 13개 전체를 기존 순서로 card grid, card → modal 탐색 유지.
- hero(step 40·41): `.hero-inner` 직계 자식 8개. viewport ≥ 1024px(`@media (min-width: 1024px)`)에서 `display: grid`, `grid-template-columns: minmax(0, 5fr) minmax(0, 7fr)`, column-gap 48px, `grid-template-areas: "eyebrow summary" "name summary" "tagline summary" "role cta" "stats stats" "featured featured"`(DOM 순서 불변), 좌측 정렬. 1024px 미만 1열.
- hero 열 폭 계약(step 41): `.hero-inner`의 computed `grid-template-columns`가 px 값 두 개 a(왼쪽)·b(오른쪽)이고, content 폭 W = `clientWidth` − 좌우 padding일 때 |a − (W − 48) × 5/12| ≤ 1, |b − (W − 48) × 7/12| ≤ 1, |a + 48 + b − W| ≤ 1(px). viewport 1023px에서는 computed `grid-template-columns`가 px 값 한 개 이하(또는 `display`가 grid 아님)이고 직계 자식 8개 left = content-box left ±1px·top이 DOM 순서대로 증가, 1024px에서는 위 2열 계약 전체가 성립한다.
- 섹션 padding·card gap: §9 표.
- component state 측정 helper(step 44 신설, `tests/helpers/component-state.js`, step 45~48 재사용). 문서 전체 `document.getAnimations()` 대기는 쓰지 않는다.
  - `waitForFiniteAnimations(page, selectors, { timeoutMs = 5000 }) → Promise<void>`: selector마다 일치하는 모든 요소에서 `el.getAnimations({ subtree: true })`를 모으고, `effect.getComputedTiming().iterations !== Infinity`이며 `playState`가 `running` 또는 `pending`인 animation·transition만 남겨 `Promise.all(animation.finished)`을 기다린다(취소로 reject되면 끝난 것으로 본다). 무한 반복 장식 CSS 애니메이션(`.caret` blink, `.scroll-hint span` scrollDot 등)은 필터에서 제외되어 계속 실행되어도 측정이 진행된다(제거 요구 없음). `timeoutMs` 안에 끝나지 않으면 `Error('animation-timeout:{selector}')`.
  - `measureState(page, selector, { nth = 0 }) → { color, backgroundColor, borderColor, outlineColor, transform, opacity, box }`: 내부에서 먼저 `waitForFiniteAnimations(page, [selector])`를 호출한 뒤 `getComputedStyle`·`boundingBox`를 읽는다. 상태 진입 후 측정은 이 helper만 쓴다.
- component state(step 44~48): 대상 `.nav-link`, `#menuToggle`, `#themeToggle`, `.hero-cta .btn`, `.featured-card`, `#projectGrid .project-card`, `#projectModal .modal-close`, `#contactActions a`, `.scroll-hint`(보일 때). 색 3속성 = color·background-color·border-color.
  - step 44 hit target(6 project): 그 project에서 기본 상태로 보이는 대상의 bbox width·height ≥ 44px.
  - step 44 menu open(`mobile-dark` 전용, 다른 project는 `test.skip`): 열기 전 `#menuToggle` 색 3속성 측정 → `#menuToggle` click → `aria-expanded="true"`·`#navLinks.open` → 보이는 `.nav-link` 각각 bbox ≥ 44px → `#menuToggle` 색 3속성이 열기 전과 같음 → 다시 click → `aria-expanded="false"`.
  - step 44 modal open(6 project): 열기 전 `#projectGrid .project-card[data-project="0"]` 색 3속성 측정 → 그 카드 click → body `modal-open`·`#projectModal` visible → `#projectModal .modal-close` bbox ≥ 44px → button으로 닫기 → `modal-open` 해제 후 같은 카드 색 3속성이 열기 전과 같음.
  - step 44 애니메이션 회귀: `.caret`·`.scroll-hint span`의 iterations Infinity 애니메이션이 실행 중인 상태에서 `#hero`·`.scroll-hint` 대상 측정이 timeout 없이 끝난다.
  - step 45 상태 순서 측정 helper(`tests/helpers/state-sequence.js`): `measureStateSequence(context, { url, selector, nth = 0, beforeMeasure = null }) → { default, hover, active }`. step 46 BASE fixture generator와 step 47 현재 상태 spec은 이 함수 하나만 쓴다. 절차(고정): 대상마다 `context.newPage()` → `goto(url)` → `document.fonts.ready` → `beforeMeasure(page)`(주어졌을 때) → 대상 locator `scrollIntoViewIfNeeded()` → `waitForFiniteAnimations(page, [selector])` → `page.mouse.move(0, 0)` 후 default `measureState` → `locator.hover()` 후 hover `measureState` → `page.mouse.down()` 직후 active `measureState` → finally에서 `mouse.down()`이 실행됐으면 `page.mouse.up()`, 그다음 항상 `page.close()`. 각 상태 값은 `measureState` 결과 중 `{ color, backgroundColor, borderColor, outlineColor, transform, opacity }`. context는 테마 단위(또는 runner 단위)로 재사용할 수 있으나 page는 측정 대상마다 새로 만든다. `mouse.up()`으로 생길 수 있는 click(CTA 기본 이동·hash·scroll, 카드 modal·`modal-open`)은 그 page와 함께 폐기되어 다음 대상에 영향을 주지 않는다.
  - step 45 격리 회귀: `grid-card-0` 대상 순서 측정(active 후 up으로 modal이 열릴 수 있음)이 끝난 뒤 같은 context의 새 page에서 `grid-card-1` 측정이 완료되고, 그 호출의 `beforeMeasure` 시점에 `#projectModal`이 hidden이고 body에 `modal-open`이 없다. `.hero-cta .btn` 0번 측정 뒤 다음 대상 호출의 `beforeMeasure` 시점에 `location.hash === ''`이고 `scrollY === 0`이다. 각 호출은 page를 정확히 1개 열고, 호출 뒤 `context.pages().length`는 호출 전과 같다(실패 경로 포함).
  - step 46 BASE 상태 색 fixture `tests/fixtures/component-state-colors.json`(`tests/scripts/make-state-colors.mjs`가 BASE 파일을 route로 제공한 페이지에서 `measureStateSequence`로 생성): 키 `hero-cta-btn-{i}`(`.hero-cta .btn` i번째), `grid-card-0`·`grid-card-1`(`#projectGrid .project-card[data-project="0"|"1"]`), 상태 `default`·`hover`·`active`, 값 `{ color, backgroundColor, borderColor }`.
  - step 47 hover·active(`desktop-dark`·`desktop-light`): 현재 각 대상의 상태별 색 3속성 = fixture의 같은 키·같은 상태 값. 첫 `.featured-card`(data-project 1)의 상태별 색 3속성 = `grid-card-1`의 같은 상태 BASE 값. hover와 active 각각에서 transform 또는 opacity가 그 요소의 default와 다르다. outline-color는 그 요소 default와 같다.
  - step 48 line clamp: `.featured-blurb`와 `#projectGrid` 카드 blurb에 screen `-webkit-line-clamp: 3`(DOM 텍스트 전문 유지, 모달·print는 전문). strength 장식 stripe: BASE `.strength-card::before` 규칙은 제거 가능(선택).
- focus-visible은 기존 outline(step 50).
- typography hierarchy: font-size·line-height·letter-spacing·margin 위계만. font-weight는 BASE `css/style.css`에 쓰인 값(400·500·600·700)만. BASE의 `font-family`·`font` 선언은 위치(file·chain·selectors, featured 대응 확장만 허용)와 값을 그대로 유지한다.

### 16.3 제외(절대 반영 금지)

새 색상 값, 기존 색상의 역할·적용 위치 변경(특히 button/logo dark text `#0d0f12`, muted grey 재배정), 기존 규칙에 새 색 적용 선언 추가(같은 prop의 다른 값 추가 포함)와 기존 색 선언 순서 변경, 색 custom property의 추가·재정의·삭제·별칭 변경, named color·`currentColor`를 통한 색 역할 변경, 서체 family/weight asset 변경과 BASE `font-family`·`font` 선언의 삭제·이동·값 변경·featured 대응 외 선택자 확장, `@import` 추가·URL·조건 변경, 새 문구·수치·통계·섹션·이미지·아이콘, 프로젝트 순서·정보구조 변경, mockup placeholder 실콘텐츠화, `css/themes.css` 변경. bundle의 hero `min-height`·card thumb 비율 등 허용 목록 밖 제안도 반영하지 않는다.

### 16.4 design guard (step 13~18)

step 13 parser(`tests/helpers/css-parse.js`, 순수):
- `parseCssRules(text, file) → Rule[]`. 주석(`/* */`) 제거, 따옴표 문자열(`'…'`, `"…"`, 백슬래시 이스케이프) 안의 `{`·`}`·`;`·`,`는 구조로 보지 않음, `url(…)` 안의 `;` 무시, 중첩 at-rule(`@media`, `@supports`, `@layer`, `@container`) 재귀, 블록 없는 at-rule(`@import`, `@charset`)과 `@font-face`는 Rule로 기록.
- Rule = `{ file, chain: string[], selectors: string[], decls: Array<[prop, value]>, atRule: string|null, prelude: string|null, index }`. chain은 바깥 at-rule prelude(공백 정규화) 목록, selectors는 최상위 쉼표로만 분리(`:is(a, b)`·`[data-x="a,b"]` 안 쉼표는 분리하지 않음)하고 공백 정규화, prop은 소문자(custom property는 원문), value는 trim·공백 정규화, `!important` 유지. `prelude`: 일반 선언 규칙과 `@font-face`는 null, 블록 없는 at-rule(`@import`, `@charset`)은 at-keyword 뒤부터 `;` 앞까지를 trim·공백 정규화한 문자열(따옴표·`url()` 내용·미디어 조건 원문 유지).
- `splitSelectors(text)`, `normalizeValue(value)` export.

step 14 색 어휘·의존 그래프(`tests/helpers/color-vocab.js`, 순수, step 13 import):
- `NAMED_COLORS`: CSS Color 4 named color 148개 + `transparent`. `COLOR_LITERAL_RE`: `#[0-9a-fA-F]{3,8}\b`, `rgb(`, `rgba(`, `hsl(`, `hsla(`, `hwb(`, `lab(`, `lch(`, `oklab(`, `oklch(`, `color-mix(`.
- `COLOR_PROPS`(색을 적용하는 속성 전부): `color, background, background-color, background-image, border, border-top, border-right, border-bottom, border-left, border-color, border-top-color, border-right-color, border-bottom-color, border-left-color, border-block, border-block-start, border-block-end, border-block-color, border-block-start-color, border-block-end-color, border-inline, border-inline-start, border-inline-end, border-inline-color, border-inline-start-color, border-inline-end-color, outline, outline-color, column-rule, column-rule-color, text-decoration, text-decoration-color, text-emphasis, text-emphasis-color, -webkit-text-fill-color, -webkit-text-stroke, -webkit-text-stroke-color, fill, stroke, stop-color, flood-color, lighting-color, box-shadow, text-shadow, caret-color, accent-color, scrollbar-color`. 예외: shorthand(`border`, `border-top|right|bottom|left`, `-color`로 끝나지 않는 `border-block*`·`border-inline*`, `outline`, `column-rule`, `text-decoration`, `text-emphasis`, `-webkit-text-stroke`)의 값이 `0` 또는 `none`이면 비색.
- `valueIdentifiers(value)`: 문자열·`url()` 내용·`var()` 인자 이름을 제외한 식별자 목록. `varRefs(value)`: `var(--x)`·중첩 fallback의 `--x` 이름 목록.
- `isColorLiteralValue(value)`: 색 리터럴, `NAMED_COLORS` 식별자(대소문자 무시), `currentColor` 중 하나라도 있으면 true.
- `isColorDecl([prop, value])`: prop ∈ COLOR_PROPS(위 예외 반영). custom property(`--x`) 선언은 항상 false.
- `customPropertyDefs(rules) → Array<{ file, chain, selectors, name, value }>`.
- `colorTokenSet(rules) → Set<string>`: 정의를 노드, `varRefs` 참조를 간선으로 둔다. 시작 집합 = `isColorLiteralValue(value)`인 정의 이름 ∪ 색 선언이 `var()`로 참조하는 이름. 별칭 간선을 양방향(참조하는 쪽·참조되는 쪽)으로 따라가는 고정점이 color token 집합이다.
- `isColorValue(value, colorTokens)`: `isColorLiteralValue(value)` 또는 `varRefs(value)` 중 colorTokens에 있는 이름이 있음.

step 15 색 규칙 대응(`tests/helpers/design-guard-color-rules.js`, 순수, step 13·14 import). 이 step의 모든 규칙은 custom property(`--x`) 선언을 검사하지 않는다(정의의 추가·변경·삭제는 step 16 `checkColorTokens` 전담). "BASE 색 선언 배열"은 BASE Rule의 custom property가 아닌 색 선언(`isColorDecl` 참, prop·정규화 value)을 등장 순서대로 나열한 배열이다.
- `featuredCounterpart(selector)`: `.project-card`를 포함한 선택자의 모든 `.project-card`를 `.featured-card`로 바꾼 문자열(없으면 null).
- `pairColorRules(baseRules, currentRules) → Array<{ base, current|null }>`: BASE 색 Rule(custom property가 아닌 색 선언이 있는 Rule)마다 같은 file·chain에서 selectors ⊇ base.selectors인 현재 Rule을 찾는다. 같은 file·chain·selectors의 BASE Rule이 여러 개면 현재 후보를 등장 순서로 1:1 짝짓는다. 짝지어진 현재 Rule은 "짝 현재 Rule", 나머지는 "짝 없는 현재 Rule"이다.
- `checkColorRules({ baseRules, currentRules, colorTokens }) → string[]`. 진단 순서(고정, 정렬하지 않음): ① BASE 색 Rule을 BASE 등장 순서(index)로 돌며 각 Rule마다 규칙 1 → 2 → 3 → 4 → 5, ② 그다음 짝 없는 현재 Rule을 현재 등장 순서로 돌며 각 Rule마다 규칙 6 → 7. 한 Rule 안에서는 선언 순서. 같은 문자열은 처음 나온 것 하나만 남긴다.
  1. 짝이 없는 BASE 색 Rule: selectors가 모두 `.strength-card::before`이면 허용, 아니면 `color-rule-missing:{chain}|{selectors}`(chain은 ` > `로, selectors는 `, `로 연결; 대상 교체·미디어 조건 변경·삭제 포함).
  2. 짝 현재 Rule의 추가 선택자가 base selectors의 featured 대응 선택자가 아니면 `selector-extended:{현재 selectors}`.
  3. BASE 색 선언 배열의 원소 중 하나라도 짝 현재 Rule의 선언에 (prop, 정규화 value)로 없으면(값 변경·삭제) `color-decl-changed:{base selectors}`.
  4. 규칙 3이 성립하지 않은 짝에서, 짝 현재 Rule의 custom property가 아닌 선언 중 (prop, 정규화 value)가 BASE 색 선언 배열에 있는 것만 등장 순서대로 뽑은 부분열이 BASE 색 선언 배열과 다르면(같은 prop의 두 색 선언 순서 뒤바꿈 포함) `color-decl-reordered:{base selectors}`. 비색 선언의 추가·이동·삭제는 이 비교에 들어가지 않는다.
  5. 짝 현재 Rule의 선언 중 custom property가 아니고 (prop, 정규화 value) 쌍이 BASE Rule의 선언에 없는 모든 선언(prop 제한 없음: 같은 prop의 다른 값 후행 추가·값 교체 포함)에 대해 `isColorDecl`이 참이거나 `isColorValue(value, colorTokens)`가 참이면 `color-decl-new:{base selectors}`. 비색 선언 추가는 허용. 값 교체는 규칙 3과 5가 함께 성립해 `color-decl-changed` 다음 `color-decl-new`가 나온다(규칙 4는 판정하지 않음).
  6. 짝 없는 현재 Rule의 custom property가 아닌 선언 중 색 선언 또는 `isColorValue`가 참인 선언 → `color-decl-new:{selectors}`. 예외: selectors가 모두 `:focus-visible`을 포함하고 선언이 `outline`·`outline-offset`뿐이며 `isColorLiteralValue`가 거짓이고 `varRefs`가 모두 colorTokens에 있음.
  7. 짝 없는 현재 Rule의 custom property가 아닌 비색 선언 값에 `currentColor`·named color가 있고 같은 file·chain·selectors·선언이 BASE에 없으면 `color-decl-new:{selectors}`(규칙 6과 같은 문자열이면 중복 제거로 하나).

step 16 token 보존·통합(`tests/helpers/design-guard-color.js`, 순수, step 13~15 import):
- `checkColorTokens({ baseRules, currentRules, colorTokens }) → string[]`(custom property 정의만 검사):
  1. BASE color token 정의(file·chain·selectors·name·value)마다 현재에 같은 file·chain·selectors·name 정의가 정확히 하나: 없으면 `color-token-removed:--x`, value 다르면 `color-token-changed:--x`.
  2. BASE에 같은 file·chain·selectors·name이 없는 현재 정의: name이 colorTokens에 있으면 `color-token-redefined:--x`, 아니고 `isColorValue(value, colorTokens)`면 `color-token-added:--x`.
  3. BASE 비색 custom property의 값이 현재 `isColorValue`가 참으로 바뀌면 `color-token-added:--x`.
- `checkColors({ baseRules, currentRules }) = [...checkColorRules(...), ...checkColorTokens(...)]`(colorTokens = `colorTokenSet(baseRules)`).

step 17 서체·asset·token(`tests/helpers/design-guard-css.js`, 순수, step 13~16 import):
- `matchesBaseRule(baseRule, currentRule) → boolean`(export): 같은 file, chain 배열 동일, base.selectors의 모든 선택자가 current.selectors에 있고, current에만 있는 선택자는 모두 base 선택자 중 하나의 `featuredCounterpart`(step 15). 서체 보존·신규 판정은 이 helper 하나만 쓴다.
- `checkTypeAndAssets({ baseRules, currentRules }) → string[]`. 결과 순서: (1) 보존 위반 전부(BASE 등장 순) → (2) 신규 위반(현재 등장 순, Rule 안에서는 선언 순), 같은 문자열은 처음 것만.
  1. 보존(BASE → 현재): BASE Rule의 `font-family`·`font` 선언(prop·정규화 value)마다 `matchesBaseRule(baseRule, currentRule)`이 참이고 같은 prop·정규화 value 선언을 가진 현재 Rule이 없으면 `font-decl-missing:{chain}|{selectors}|{prop}`(BASE 기준, chain은 ` > `, selectors는 `, `로 연결). 삭제·선택자 이동·featured 대응 외 선택자 확장·미디어 조건 이동·값 변경 모두 해당.
  2. 신규(현재 → BASE): 현재 Rule의 `font-family`·`font` 선언마다 `matchesBaseRule(baseRule, currentRule)`이 참이고 같은 prop·정규화 value 선언을 가진 BASE Rule이 없으면 `font-asset:{현재 selectors}`(featured 대응 확장은 신규 아님); 현재 `@import` Rule마다 BASE에 같은 file·chain·atRule·prelude인 Rule이 없으면(신규·URL 변경·조건 변경) 정확히 `asset:@import` 하나(`font-asset`은 내지 않음); BASE에 같은 file·chain·atRule·선언으로 없는 `@font-face` → `font-asset:@font-face`, 그 선언의 새 `url(` → `asset:@font-face`; `font-weight` 값이 BASE style.css 값 집합 밖 → `font-weight:{value}`; 선언 규칙의 새 `url(` → `asset:{selectors}`; 새 `content` 값이 `none`·`''`·`""`·`normal` 밖 → `content:{selectors}`; `var(--x)`의 x가 BASE 두 파일과 현재의 비색 custom property 정의 어디에도 없으면 → `unknown-token:--x`.
- `checkCss({ baseCss, currentCss, baseThemes, currentThemes }) → string[]` = 네 텍스트를 parse해 `[...checkColors(...), ...checkTypeAndAssets(...)]`, 그리고 `currentThemes !== baseThemes`면 `themes-changed`.

step 18 markup·통합(`tests/helpers/design-guard.js`):
- `checkMarkupPatch(patch, kind)`: `git diff --unified=0` patch의 추가 줄에 `<img`, `<svg`, `<picture`, `<video`, `<i `, `<i>`, `<link`, `<script`, `<font`, `style=`, `.style.color`, `.style.background`, `.style.font`가 있으면 `markup-asset:{kind}:{n}`.
- `collectGuardInput({ git, fs })`: `git show <BASE>:css/style.css`, `git show <BASE>:css/themes.css`, worktree `css/style.css`·`css/themes.css`(읽기), `git diff --no-renames --unified=0 <BASE> -- index.html`, `-- js/main.js`.
- `runGuard(input) = [...checkCss(...), ...checkMarkupPatch(html, 'index.html'), ...checkMarkupPatch(js, 'js/main.js')]`. 이후 모든 step의 전체 testCommand에서 위반 0을 요구한다.

## 17. fresh runner preflight (대표 exact 승인 후, runner 시작 전, 하네스 수행 — source 구현 아님)

승인 대상 exact 경로 28개(삭제는 이 목록만):
- untracked stale 산출물 2개: `tests/helpers/theme.js`, `tests/specs/smoke.spec.js`
- 2.0.0 identity runtime snapshot 13개: `tests/.tmp/start-snapshot-step0.json`, `tests/.tmp/start-snapshot-step1.json`, `tests/.tmp/start-snapshot-step2.json`, `tests/.tmp/start-snapshot-step3.json`, `tests/.tmp/start-snapshot-step4.json`, `tests/.tmp/start-snapshot-step5.json`, `tests/.tmp/start-snapshot-step6.json`, `tests/.tmp/start-snapshot-step7.json`, `tests/.tmp/start-snapshot-step8.json`, `tests/.tmp/start-snapshot-step9.json`, `tests/.tmp/start-snapshot-step10.json`, `tests/.tmp/start-snapshot-step11.json`, `tests/.tmp/start-snapshot-step12.json`
- 같은 실행의 after.z 13개: `tests/.tmp/start-snapshot-step0-after.z`, `tests/.tmp/start-snapshot-step1-after.z`, `tests/.tmp/start-snapshot-step2-after.z`, `tests/.tmp/start-snapshot-step3-after.z`, `tests/.tmp/start-snapshot-step4-after.z`, `tests/.tmp/start-snapshot-step5-after.z`, `tests/.tmp/start-snapshot-step6-after.z`, `tests/.tmp/start-snapshot-step7-after.z`, `tests/.tmp/start-snapshot-step8-after.z`, `tests/.tmp/start-snapshot-step9-after.z`, `tests/.tmp/start-snapshot-step10-after.z`, `tests/.tmp/start-snapshot-step11-after.z`, `tests/.tmp/start-snapshot-step12-after.z`

절차:
1. 각 경로가 regular file인지 lstat으로 확인하고(symlink·디렉터리면 중단), 두 untracked 파일은 `git status --porcelain=v1 -z --untracked-files=all -- <path>`가 `??`인지 확인한다.
2. backup: `/Users/hoon/.hermes/company/development/product-management/HOO-81-evidence/preflight-<UTC 타임스탬프>/`에 같은 상대 경로로 `cp -p` 복사하고, 원본·복사본 sha256 manifest(`manifest.sha256`, 28줄)를 기록한다.
3. 원본과 복사본 sha256이 모두 같을 때만 `rm --` 뒤에 28개 경로를 명시적으로 나열해 제거한다. `git clean`, `git reset`, `git restore`, `git checkout`, glob·와일드카드·디렉터리 삭제는 쓰지 않는다.
4. 검증: 28개 경로가 모두 없음(lstat ENOENT), backup 28개가 manifest sha256과 일치, HEAD가 plan commit과 같음, `git status --porcelain=v1 --untracked-files=all`에 §11.5 하네스 런타임 면제 밖 항목 없음, `tests/.tmp`에 `start-snapshot-*` 파일 없음.
5. 위 목록 밖의 `start-snapshot-*` 파일이 발견되면 제거하지 않고 중단해 대표 지시를 받는다. 두 untracked 파일 내용은 승인된 구현이 아니며 step 19가 새로 작성한다.
6. Harness 2.0.1 migration·Chromium 선행 HOO-100은 완료 상태다.
