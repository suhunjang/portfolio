# HOO-81 포트폴리오 레이아웃·구조 리디자인 설계 (compact v44)

- 날짜 2026-11-23(범위 변경 2026-11-24) / 브랜치 `feat/HOO-81/portfolio-redesign` / base `main` / BASE `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`
- 선행 시각 설계(유효): `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
- 합의: Q1 Discord 1574196542901059632, Q2 1574197289084387379, Q3~Q5 1574197696334405756. 범위 변경: `scope-change-claude-design-v27`·`scope-change-claude-design-v28-compact`(Claude Design의 레이아웃·컴포넌트·간격·타이포 위계만 반영). 이전 2.0.1 계획·리뷰·승인은 재사용하지 않는다.
- 리뷰 반영: 1~31차는 Git 이력. 32 `review-resume-c57f750bfd7a-v29`, 33 `review-resume-d032b938c536-v30`, 34 `review-resume-16ea71f32fac-v31`, 35 `review-resume-6a5d82a7db93-v32`(record `6a5d82a7db9327845ac1b1a429b2113f20fff779984eecc4fc27f7eba059c7b7`), 36 `review-resume-9c1f912760e7-v33`(`9c1f912760e7aba49329496be4ce22a53612f3498c7796f636a018bd1ec817b0`), 37 `review-resume-4a273c5a72dc-v34`(`4a273c5a72dc829f3819e328102c0d73235e74a36730dd2472acfbe16f5d0192`), 38 `review-resume-07753db669ba-v35`(`07753db669ba0d853347ef8f1315c077b1e18998cfe10e670989ffdeb6b6e593`), 39 `review-resume-194334d2d96f-v36`(`194334d2d96fbd34834e49b486a28bbd62e1d3a80584c8df95a2d3cea6b28275`), 40 `review-resume-e72caf27c285-v37`(`e72caf27c28507c265ab6f5579f6ddfa3e1b8fabf14c7321e3144d934772abcd`), 41 `review-resume-482d07084590-v38`(`482d070845902c9ad5f594dc6dbc6d4ad4b21b6681345c55c8ce636e55e18e95`), 42 `review-resume-36742c718c00-v39`(`36742c718c00c17fa60a41d21e3ccbb65337375e29b2c2bdf610f3d315b3fcfb`), 43 `review-resume-13bc4ab9a023-v40`(`13bc4ab9a023e1c6516b9afe4fcebf807e2a5c096432636875a3bc7a093e8a11`), 44 `compact-materialize-v41`(표현 압축), 45 `review-resume-0b2d97054226-v42`(`0b2d97054226866fb163e4673914b5fb0786c2a659ca80d2c9f03cefc861dc7e`: fix `requiresColorChange`), 46 `review-resume-01b6dbabb677-v43`(`01b6dbabb6774a4e22a04f4c733323ae26f2996c2e04f10aa7174ebb1bc798a9`: `requiredBlockReason`, prune 재계산·manual block), 47 `review-resume-79ede98edf95-v44`(`79ede98edf950d3d244b57936c64b42e61f539f573ecb13592e2c38dc0806e04`: CSS `color()` 함수를 색 리터럴로 판정, 대소문자 무시·identifier 경계).
- §ID Harness identity(`.harness/harness.lock.json` 직접 확인): sourceCommit `e7a03919a460f975149f7c55343ca4b34d3d2352`, manifestHash `b627e6a5ce4a903c24c400927ca2b49a14d0bd59632c691b2a5c2d74c6c08372`, distributionVersion `2.0.1`.
- §FLOW: materialize → plan commit → Astra `gpt-6-astra` 계획 리뷰 CLEAN → 대표 exact 승인(§12 경로 포함) → §12 preflight → fresh runner(step 0~57) → 전체 테스트 → exact-commit Astra CLEAN → feature push → OPEN PR. merge·deploy·main 직접 변경 없음.

## 1. 범위·실패 조건

- 유지: 색·서체·문구·수치, FINAL 정보구조(hero→Career→Projects→Strengths→About→Contact), 대표 3개(index 1·5·7), PROJECTS 13개 전부·순서. 반영: §11.2 허용 패턴만.
- 목표: 1280×800 첫 화면에 이름·tagline·STATS 4개·대표 제목 3개. 보존·제외는 자동 테스트·범위 검사로 증명.
- 비목표: 색·서체 재설계, 빌드 도구, 신규 기능, 배포·merge·main 변경.
- 실패(동작해도): §5 예외 밖 문구·수치·경력 변경/생성, 빈 email·phone·social 채우기, 기능 회귀, axe serious/critical 잔존, §11.3 반영, 그라데이션·글로우 추가.

## 2. 현재 코드 사실

- BASE 저장소 지침은 `README.md`. 하네스 파일: `CLAUDE.md`, `.harness/harness.lock.json`, `.harness/policy.json`, `.harness/install-state.json`, `.claude/`, `.codex/`, `pytest.ini`, `.python-version`, `.gitattributes`, `.venv/`.
- HEAD에는 기존 step 0~11 구현 commit이 있다(`tests/scripts/with-env.sh`, `start-snapshot.py`, `scope-snapshot.mjs`, `tests/helpers/synthetic-repo.js`, scope-snapshot spec들, `tests/package.json`·lock·`.gitignore`·`playwright.config.js`·`bootstrap.spec.js`). 커밋된 `start-snapshot.py`(2.0.0 identity, decode 변환 없는 `parse_status`)와 `scope-snapshot.mjs`의 `HARNESS_IDENTITY`(2.0.0)는 step 0이 동기화한다. untracked `tests/helpers/theme.js`, `tests/specs/smoke.spec.js`와 이전 snapshot 26개는 §12가 처리한다.
- `js/data.js`: `PROFILE`, `STATS`(4), `CAREER`, `VIS_ACCENT`, `makeVisual`, `PROJECTS`(13, 모두 `detail`), `STRENGTHS`(6), `SKILLS`. `PROFILE.tagline`은 BASE에서 미렌더. email·phone·social.* 빈 문자열. 대표 index: Motion AD=1, VigoRight=5, Lost Energy Intel=7.
- `index.html` hero: `section.hero#hero` > `div.container.hero-inner` > (`p.hero-eyebrow`, `h1.hero-name#heroName`, `h2.hero-role`, `p.hero-summary#heroSummary`, `div.hero-cta`, `ul.hero-stats#heroStats`) + `a.scroll-hint`(밖). `#themeToggle`. `.strength-card`(BASE 장식 `.strength-card::before`). 무한 장식 애니메이션: `.caret` blink, `.scroll-hint span` scrollDot.
- `js/main.js`: `setText(id, value)`. 렌더 `#heroStats`, `#strengthsGrid`, `#timeline`(`.timeline-item` > `.timeline-period` + `.timeline-card`), `#projectGrid`, `#skillsGrid`, `#contactActions`. 카드 `article.project-card.has-detail[data-project=idx][tabindex=0][role=button]`.
- 모달 `div.modal#projectModal[hidden]` > `.modal-backdrop[data-modal-close]` + `.modal-dialog` > (`button.modal-close[data-modal-close]` + `#modalBody`: `.modal-visual`/`.modal-thumb`, `h3#modalTitle.modal-title`, `.modal-meta`, `p.modal-blurb`, `.modal-section`(갤러리 `.shot-zoom`)). `openProjectModal(idx)`는 `lastFocused` 저장·닫기 버튼 포커스·body `modal-open`. 열기 `#projectGrid` 위임, 닫기 `[data-modal-close]`·Esc(lightbox 우선).
- lightbox: `ensureLightbox()`가 `.lightbox[role=dialog]`(`button.modal-close` + `img`)를 `.shot-zoom`으로 연다. lightbox에만 Tab 고정 리스너.
- 스크롤스파이 배열(about, strengths, career, projects, contact), reveal `.reveal`→`.in`, `runTyping`(reduced-motion이면 `roles[0]`), 테마 `THEME_KEY`, 메뉴 `#menuToggle`·`#navLinks.open`·`aria-expanded`, `@media print`. Google Fonts Space Grotesk 링크 제거 금지.

## 3. hero·대표 프로젝트

- `.hero-inner` 직계 자식 정확히 8개, 순서: `.hero-eyebrow` → `h1#heroName` → `p.hero-tagline#heroTagline`(정확히 `setText('heroTagline', PROFILE.tagline)`) → `h2.hero-role`(`#typed`) → `#heroSummary` → `.hero-cta` → `ul#heroStats` → 대표 컨테이너.
- 컨테이너 정확히: `<div id="heroFeatured" role="region" aria-label="대표 프로젝트"></div>`
- 카드: `<button type="button" class="featured-card" data-featured-card data-project="{원본 idx}"><span class="featured-title">{p.title}</span><span class="featured-blurb">{p.blurb}</span></button>`; 자손은 span·텍스트만, span `display: block`, grid 카드와 같은 `data-project`. helper는 grid 카드를 `#projectGrid .project-card[data-project="N"]`로 한정.
- 함수: `renderFeaturedProjects()`(원본 순서 `featured === true`, 그리드 직후), `openProjectModal(projectIndex, triggerElement = document.activeElement)`(grid `(idx, card)`, `#heroFeatured` click 위임), `closeProjectModal()`은 모든 경로에서 `lastFocused` 복귀.
- data.js: index 1·5·7의 `title:` 다음 줄 `featured: true,` 정확히 3줄.
- 대표 카드 색은 새 색 선언 없이 기존 `.project-card` 색 규칙 선택자 목록에 featured 대응 선택자(§11.4)를 추가해서만 얻는다.
- 첫 화면 AC(1280×800, 단독·통합): `document.fonts.ready` 후 `scrollY === 0`. 대상 `#heroName`, `#heroTagline`, `#heroStats`, `.featured-title` 3개, 지표 item 4개(DOM 순서 = `STATS[0..3]`)마다 item·수치(norm = STATS 수치)·label(norm = STATS label), 셀렉터 상수 `STAT_ITEM`·`STAT_VALUE`·`STAT_LABEL`. 각 대상 `toBeVisible()`, bbox w·h > 0, 자신·모든 조상 visibility `visible`·opacity `1`(`expect.poll`), x ≥ 0, y ≥ 0, x+w ≤ 1280, y+h ≤ 800.

## 4. 섹션 구조 (FINAL)

| 순서 | id | class | kicker | heading |
|---|---|---|---|---|
| 1 | hero | hero | 없음 | h1 `#heroName` |
| 2 | career | section | `01 — Career` | h2 경력 &amp; 창업 |
| 3 | projects | section section-alt | `02 — Projects` | h2 프로젝트 &amp; 제품 |
| 4 | strengths | section | `03 — Strengths` | h2 업무상 강점 (section-sub 유지) |
| 5 | about | section section-alt | `04 — About` | h2 소개 |
| 6 | contact | section | `05 — Contact` | h2 연락처 |

- about: 본문 뒤 `h3.subsection-title` 기술 스택 + `#skillsGrid`(skill-group 제목 h4). contact: `.contact-card`, h3 함께 만들어요 유지.
- nav·스크롤스파이 배열: career, projects, strengths, about, contact. `.scroll-hint` href `#career`.
- 스크롤스파이 테스트(정확히): `const link = page.locator('.nav-link[href="#projects"]'); await link.click(); await expect(link).toHaveClass(/active/);` (about 동일 형식).
- `#projectGrid`에 PROJECTS 13개를 data.js 순서로 렌더(Explore surface).

## 5. 콘텐츠 보존

- 기준: `BaselineData`(BASE data.js 평가, step 24), `StaticContent`(BASE index.html 정적 본문, step 25).
- 허용 예외: (1) index 1·5·7 `featured: true`; (2) `kickers`는 BASE [01 — About, 02 — Strengths, 03 — Career, 04 — Projects, 05 — Stack &amp; Contact] 또는 FINAL [01 — Career, 02 — Projects, 03 — Strengths, 04 — About, 05 — Contact] 중 정확히 하나; (3) `sectionTitles`는 BASE [소개, 업무상 강점, 경력 &amp; 창업, 프로젝트 &amp; 제품, 기술 스택 &amp; 연락처] 또는 FINAL [경력 &amp; 창업, 프로젝트 &amp; 제품, 업무상 강점, 소개, 연락처], FINAL이면 `h3.subsection-title` 기술 스택 정확히 1개; (4) nav·섹션 순서(`navLabels` 정렬 비교); (5) skill-group 제목 heading level; (6) remediation 그룹 step의 위반 요소 aria-*·role·alt·lang·tabindex·for 변경(텍스트 불변).
- `tests/helpers/content.js`: `norm(s) = String(s).replace(/\s+/g, ' ').trim()`; `BaselineData = { PROFILE, STATS, CAREER, VIS_ACCENT, PROJECTS, STRENGTHS, SKILLS }`; `StaticContent`(norm): `title`, `metaDescription`, `navLabels`(정렬), `heroEyebrow`, `ctaLabels`, `kickers`, `sectionTitles`, `sectionSubs`, `aboutParagraphs`(`.about-text p:not([id])`), `aboutPoints`, `aboutMetaTerms`, `contactHeading`, `contactText`, `footerNote`, `footerTop`. step 24 `readLiveData`·`normalizeFeatured`, step 25 `extractStatic`.
- 회귀(step 26 `modal-regression.spec.js` + `tests/helpers/modal.js`, step 27 `ui-regression.spec.js` + `first-visit.spec.js`). `modal.js`: `GRID_CARD = '#projectGrid .project-card'`; `gridCard(page, N)` = 정확히 `page.locator('#projectGrid .project-card[data-project="' + N + '"]')`; `openFirstProjectByClick`, `openFirstProjectByEnter`; `closeVia(page, 'button'|'backdrop'|'esc')`(button `#projectModal .modal-close[data-modal-close]`, backdrop `{x:5, y:5}`); `expectFocused`; `modalTitle(page)`; `findProjectWithShots(page): number|null`(grid만).

## 6. 접근성

### 6.1 axe·focus
- wcag2a·wcag2aa serious/critical 0. 시나리오 10개: page 3 viewport × 2 테마, modal·lightbox × dark/light. `prepareForAxe` 후에만 실행.
- focus trap: `trapFocus(container, { returnFocusTo? }): () => void` — 스택, 최상위만 Tab 순환, document Tab 핸들러 1개, `release()` 다중 호출 안전. step 51 구현+모달 push/release. step 52 lightbox push(`.shot-zoom`), 모달 trap 일시정지·재개, 기존 lightbox Tab 리스너 제거, `:focus-visible` outline 검증.
- canonical target(step 28): `{ruleId}::{anchor}::{textSig}`. anchor: `[data-featured-card][data-project]`→`featured:{N}`, `[data-project]`→`project:{N}`, `[id]`→`#{id}`, landmark→태그명, 없으면 `document`. textSig: norm(textContent) → aria-label → alt → title → src 파일명, 숫자 `#`, 80자. alias: `## — Stack & Contact`→`## — Contact`, `기술 스택 & 연락처`→`연락처`.
- entry key(step 32): `makeEntryKey({ scenario, project, ruleId })` = `${scenario}:${project}:${ruleId}`(빈 값·`:` throw). (key, target) = 위반 1건.

### 6.2 `tests/helpers/axe.js` (step별 추가)
- 28: `ALIASES`, `canonicalTargetInPage`, `canonicalFromDescriptor`, `runAxe(page, { include }) → Violation[]`.
- 32: `makeEntryKey`, `COLLECT_DIR`(`tests/.tmp/axe-collected`), `EXPECTED_FILES` 10개, `resolveCollectDir`, `resetCollected`, `writeCollected`, `mergeCollected({ collectDir, out })`(MergedEntry = §6.4 앞 7필드, key 정렬), CLI `--reset`, `--merge [--dir] [--out]`.
- 33: `BASELINE_PATH`, `COLLECTED_PATH`, `PLAN_PATH`, `FIX_FILES_BY_KIND`, `baselineExists`, `loadBaseline`, `resolveBaselineMode`(`check`/`pending`/throw, 환경변수 우회 없음), `validateBaseline`(§6.4, `requiresColorChange` 포함), `checkRegression(violations, baseline, scenario, project)`(`new-key:{key}`, `new-target:{key}:{target}`), `assertEmptyFile`, CLI `--assert-empty`.
- 34: `PROJECTION_FIELDS = ['key','scenario','project','ruleId','impact','targets','selectors']`(fixes·fixFiles·fix의 `requiresColorChange`는 projection과 collected 비교에서 명시적으로 제외), `projectEntry`, `compareCollectedBaseline(collected, baseline) → { ok, missingEntries, extraEntries, missingTargets, extraTargets, fieldMismatches }`(collected에만/baseline에만 있는 key, 같은 key의 collected에만/baseline에만 있는 `{key, target}`, scenario·project·ruleId·impact·selectors 중 다른 `{key, field}`; 모두 정렬; ok = 다섯 배열 빔), CLI `--check-baseline-match [--collected] [--baseline]`(불일치 stderr `missing-entry:{key}`, `extra-entry:{key}`, `missing-target:{key}|{target}`, `extra-target:{key}|{target}`, `field-mismatch:{key}|{field}` 이 순서, exit 1).
- 35: `GROUP_ID_RE`, `loadPlan`, `requiredBlockReason(groupTargets: PlanTarget[], baseline) → string`(§6.5, 공용; step 38 재사용), `validateRemediationPlan(plan, baseline, { coverage = false, requireEmpty = false }) → string[]`(§6.5, 필수 reason은 `requiredBlockReason`으로만 계산), CLI `--check-plan [--coverage] [--require-empty] [--plan] [--baseline]`.
- 36: `validateRemediationExecutable(plan, baseline) → string[]`(전제: 같은 입력이 `validateRemediationPlan`에서 `[]`; blocked 그룹만 거부: `blocked-group:{id}`, `text-change:{id}:{key}:{target}`, `empty-fixfiles:{id}`), CLI `--check-executable`(첫 줄 `Harness 재계획 필요: 실행 불가 remediation 그룹`). 잘못 분류된 그룹(`requiresColorChange === true`인데 blocked false)은 `--check-plan`이 먼저 차단하므로 AC는 항상 `--check-plan` 다음 `--check-executable`.
- 37: `checkGroupDone(collected, plan, id) → { done, remaining: PlanTarget[] }`, `checkCollectedCoverage → { ok, uncovered: PlanTarget[] }`, `countCollectedTargets`, CLI `--check-group-done <id>`, `--check-coverage`, `--assert-no-violations`(`--collected` 기본 `tests/.tmp/axe-current.json`).
- 38: `checkCollectedRegression`, `prunePlan(plan, collected, baseline) → plan`(§6.5 prune: 제거 → 빈 그룹 삭제 → `requiredBlockReason` 재사용해 fixFiles·blocked·reason 재계산, manual block 보존 규칙), CLI `--check-regression`, `--prune-plan`(회귀 실패 시 쓰지 않음, 통과 시 `JSON.stringify(plan, null, 2) + '\n'`).
- 실행 모드: `prepareForAxe` → `runAxe`. 수집(`AXE_COLLECT=1`)은 `writeCollected`만. 일반: `resolveBaselineMode()`; `check`면 checkRegression·validateBaseline(desktop-dark 1회)·plan 있으면 validateRemediationPlan(coverage false); `pending`이면 `test.skip(true, 'axe classification pending (step 40)')`.
- 단계: step 39 수집(pending 종료) → 40 분류(예상 = 묶음별(2분 + target×1분) + 6분, 20분 초과면 재계획) → 41~53 새 key/target 실패(색 변경 없이 그 step에서 해결) → 54 gate(COLLECT_CHAIN `--out tests/.tmp/axe-current.json` → REGRESSION_GATE → `--prune-plan` → `--check-coverage` → `--check-plan` → `--check-executable`; 그룹이 남으면 하네스가 54와 55 사이에 `axe-remediation-{id}` 재계획) → 55 recheck(+`--require-empty`, `--assert-no-violations`) → 56 finalize(baseline `[]`).
- 재계획 그룹 step: `--check-plan`·`--check-executable` 통과·`blocked === false`·`fixFiles.length >= 1`일 때만, allowedPaths = 그룹 fixFiles(`css/themes.css` 포함이면 생성 안 함), 20분 이하, 첫 동작 `python3 -I tests/scripts/start-snapshot.py axe-remediation-{id}`, AC: COLLECT_CHAIN && REGRESSION_GATE && `AXE --check-group-done {id}` && FULL && VS && `W node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-axe-remediation-{id}.json --allow {fixFiles}`.

### 6.3 `tests/helpers/axe-prepare.js`
- 29: `PREPARE_PREFIX = 'prepareForAxe: '`, `prepareError(code, cause?)`, `withPrepareCode(code, fn)`, `preparePage(page, { timeoutMs = 10000 })`(`fonts-not-ready`, `reveal-hidden:{n}`).
- 30: `MODAL_ROOT`, `MODAL_BODY_TEXT = '#modalBody .modal-blurb, #modalBody .modal-section'`, `assertContentLoaded(locator, timeoutMs, { textLocator = null })`(`content-not-loaded:img|svg|text`), `prepareModal(page, { projectIndex = 0 })`(`project-card-not-found:{N}`, `modal-not-open`).
- 31: `prepareLightbox`(`no-shots-project`, `lightbox-not-open`), `prepareOverlay`(`unknown-scenario`), `prepareForAxe(page, { scenario, projectIndex? })`.
- 합성 fixture: 동작 모달 fixture(`window.__opens`·`__closes`·`__clicks`), handler 없는 fixture.

### 6.4 baseline schema (고정, step 33 이전 확정)
- JSON 배열, key 오름차순(코드 유닛)·고유, 빈 배열 허용. entry 필드 정확히 `key, scenario, project, ruleId, impact, targets, selectors, fixes, fixFiles`.
- `scenario` ∈ `page|modal|lightbox`; `project` ∈ `mobile-dark|mobile-light|tablet-dark|tablet-light|desktop-dark|desktop-light`; `ruleId` 비어 있지 않고 `:` 없음; `key === makeEntryKey(...)`; `impact` ∈ `serious|critical`; `targets` 비어 있지 않은 문자열·고유·오름차순; `selectors` 문자열·고유·오름차순.
- `fixes`: targets와 같은 길이, `fixes[j].target === targets[j]`, Fix 필드 정확히 `target, fixKind, fixFiles, requiresColorChange`; `fixKind` ∈ `css-token|css-rule|js-render|static-markup|text-change`; `fixFiles` = `FIX_FILES_BY_KIND[fixKind]`(css-token `["css/themes.css"]`, css-rule `["css/style.css"]`, js-render `["js/main.js"]`, static-markup `["index.html"]`, text-change `[]`); `requiresColorChange`: boolean, 그 target 수정에 기존 색 값 또는 색 역할 변경이 필요하면 true, 아니면 false; css-token은 true만, css-rule은 true/false(실제 수정 성격), js-render·static-markup·text-change는 false만. entry `fixFiles` = fixes fixFiles 합집합·고유·오름차순.
- `validateBaseline → string[]`(발견 순): `baseline: not-array`; `baseline[{i}]: not-object`; `baseline[{i}]: fields missing=[a,b] extra=[c]`; `baseline[{i}]: bad-scenario|bad-project|bad-ruleId|key-mismatch|bad-impact`; `baseline[{i}]: targets empty|not-string|duplicate|unsorted`; `baseline[{i}]: selectors not-string|duplicate|unsorted`; `baseline[{i}]: fixes count`; `baseline[{i}].fixes[{j}]: not-object|fields missing=[..] extra=[..]|target-mismatch|bad-fixKind|fixFiles-mismatch|bad-requiresColorChange`(bad-requiresColorChange = 필드가 있으나 boolean 아님, 또는 fixKind가 유효할 때 위 kind별 값 위반; 필드 누락은 `fields missing=[requiresColorChange] extra=[]`); `baseline[{i}]: fixFiles union-mismatch`(fix 오류 없는 entry만); `baseline: duplicate-key {key}`; `baseline: unsorted`.
- 정상 예(= FIXTURE_THEMES):

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
    "fixes": [{ "target": "color-contrast::#career::## — Career", "fixKind": "css-token", "fixFiles": ["css/themes.css"], "requiresColorChange": true }],
    "fixFiles": ["css/themes.css"]
  }
]
```

- 오류 예 A: entry에 `"note": "x"` 추가 → 정확히 `["baseline[0]: fields missing=[] extra=[note]"]`. B: fix `fixKind`만 `css-rule`(fixFiles·`requiresColorChange: true` 유지) → `["baseline[0].fixes[0]: fixFiles-mismatch"]`. C: fix 정상, entry `fixFiles`만 `["css/style.css"]` → `["baseline[0]: fixFiles union-mismatch"]`. D: fix `requiresColorChange`만 false → `["baseline[0].fixes[0]: bad-requiresColorChange"]`. E: fix에서 `requiresColorChange` 삭제 → `["baseline[0].fixes[0]: fields missing=[requiresColorChange] extra=[]"]`.
- step 40만 이 계약으로 생성, step 33·34·35·38·56이 같은 계약을 쓴다.

### 6.5 remediation plan schema (고정)
- 객체, 필드 정확히 `groups`(배열, id 오름차순·고유). Group 필드 정확히 `id, targets, fixFiles, difficulty, estMinutes, blocked, reason`.
- `id` `/^[a-z0-9]+(?:-[a-z0-9]+)*$/`; `targets` 비어 있지 않은 PlanTarget(필드 정확히 `key, target`, 문자열) 배열, (key, target) 오름차순·그룹 내 중복 없음·baseline에 존재·두 그룹 중복 금지; `fixFiles` = 대응 fix fixFiles 합집합·고유·오름차순; `difficulty` ∈ `low|medium|high`; `estMinutes` 정수 1~20; `blocked` boolean; `reason` 문자열.
- `requiredBlockReason(groupTargets, baseline) → string`(순수, 입력 불변): groupTargets 각 (key, target)의 baseline fix를 모아 text-change가 있으면 조각 `text change excluded`, `requiresColorChange === true`가 있으면 조각 `color change excluded (HOO-81 §16.3)`; 이 순서로 `; ` 연결(둘 다 → `text change excluded; color change excluded (HOO-81 §16.3)`), 조각 없으면 `""`. baseline에 없는 target은 무시(검증은 `unknown-target`이 담당).
- validator의 blocked·reason: R = `requiredBlockReason(group.targets, baseline)`. R ≠ `""`이면 `blocked === true`(아니면 `blocked-required`)이고 reason = R(빈 문자열 `reason-required`, 다르면 `reason-mismatch`). R = `""`이면 blocked true/false 모두 허용(manual block), blocked true면 reason 비어 있지 않음(`reason-required`), false면 `""`(`reason-must-be-empty`). css-token은 항상 true이므로 `css/themes.css` 그룹은 항상 blocked.
- coverage: baseline 모든 (key, target)이 정확히 한 그룹. requireEmpty: `groups.length === 0`.
- 오류: `plan: not-object`, `plan: fields missing=[..] extra=[..]`, `plan: groups not-array`, `groups[{i}]: not-object|fields missing=[..] extra=[..]|bad-id|targets empty|fixFiles-mismatch|bad-difficulty|bad-estMinutes|bad-blocked|reason-required|reason-must-be-empty|reason-mismatch|blocked-required`, `groups[{i}].targets[{j}]: not-object|fields missing=[..] extra=[..]|unknown-target`, `groups[{i}]: targets duplicate|targets unsorted`, `plan: duplicate-id {id}`, `plan: groups unsorted`, `plan: target-in-multiple-groups {key}|{target}`, `plan: uncovered {key}|{target}`, `groups: expected empty, got {n}`.
- prune(`prunePlan(plan, collected, baseline)`, 순수·입력 불변·결정적): 그룹마다 (1) collected에 없는 PlanTarget 제거(남은 targets 순서 유지); (2) 빈 그룹 삭제(남은 그룹 순서 유지); (3) 남은 targets로 `fixFiles` = 대응 fix fixFiles 합집합·정렬, R' = `requiredBlockReason(남은 targets, baseline)`; (4) R' ≠ `""`이면 `blocked = true`, `reason = R'`; (5) R' = `""`이면, prune 전 `blocked === true`이고 prune 전 reason이 비어 있지 않으며 `requiredBlockReason(prune 전 targets, baseline)`과 다르면 manual block으로 보고 blocked·reason 유지, 그 밖에는 `blocked = false`, `reason = ""`; (6) id·difficulty·estMinutes 유지, 필드 추가 없음. 결과는 `validateRemediationPlan(…, { coverage: false })`에서 `[]`. 필수 reason과 manual reason이 섞인 그룹은 validator가 이미 거부(`reason-mismatch`)하므로 유효 입력이 아니다. `checkGroupDone`·`checkCollectedCoverage`도 PlanTarget 단위.
- fixture(step 33·35·36·38 공용 spec 상수, 모두 `validateBaseline` → `[]`):
  - FIXTURE_OK = 1 entry `{ "key": "page:desktop-dark:aria-allowed-attr", "scenario": "page", "project": "desktop-dark", "ruleId": "aria-allowed-attr", "impact": "serious", "targets": ["aria-allowed-attr::#heroFeatured::대표 프로젝트"], "selectors": ["#heroFeatured"], "fixes": [{ "target": "aria-allowed-attr::#heroFeatured::대표 프로젝트", "fixKind": "static-markup", "fixFiles": ["index.html"], "requiresColorChange": false }], "fixFiles": ["index.html"] }`
  - FIXTURE_THEMES = §6.4 정상 예(`requiresColorChange: true`).
  - FIXTURE_RULE_PLAIN = 1 entry `{ "key": "page:desktop-dark:target-size", "scenario": "page", "project": "desktop-dark", "ruleId": "target-size", "impact": "serious", "targets": ["target-size::#themeToggle::#"], "selectors": ["#themeToggle"], "fixes": [{ "target": "target-size::#themeToggle::#", "fixKind": "css-rule", "fixFiles": ["css/style.css"], "requiresColorChange": false }], "fixFiles": ["css/style.css"] }`
  - FIXTURE_RULE_COLOR = §6.4 정상 예에서 fix를 `{ "fixKind": "css-rule", "fixFiles": ["css/style.css"], "requiresColorChange": true }`, entry `fixFiles` `["css/style.css"]`로 바꾼 것.
  - FIXTURE_MIXED = 1 entry `{ "key": "page:desktop-dark:color-contrast", "scenario": "page", "project": "desktop-dark", "ruleId": "color-contrast", "impact": "serious", "targets": ["color-contrast::#career::## — Career", "color-contrast::#projects::## — Projects"], "selectors": ["#career .section-kicker", "#projects .section-kicker"], "fixes": [{ "target": "color-contrast::#career::## — Career", "fixKind": "css-rule", "fixFiles": ["css/style.css"], "requiresColorChange": true }, { "target": "color-contrast::#projects::## — Projects", "fixKind": "text-change", "fixFiles": [], "requiresColorChange": false }], "fixFiles": ["css/style.css"] }`
  - FIXTURE_COLOR_PLAIN = FIXTURE_RULE_COLOR ∪ FIXTURE_RULE_PLAIN(key 순서: color-contrast, target-size).
- 예(정확한 결과):
  - FIXTURE_OK + `{ "groups": [ { "id": "hero-featured-aria", "targets": [ { "key": "page:desktop-dark:aria-allowed-attr", "target": "aria-allowed-attr::#heroFeatured::대표 프로젝트" } ], "fixFiles": ["index.html"], "difficulty": "low", "estMinutes": 6, "blocked": false, "reason": "" } ] }` → coverage 포함 `[]`; target 문자열 → `groups[0].targets[0]: not-object`; `blocked: true`·`reason: ""` → `groups[0]: reason-required`.
  - FIXTURE_THEMES + `{ "groups": [ { "id": "career-kicker-contrast", "targets": [ { "key": "page:desktop-dark:color-contrast", "target": "color-contrast::#career::## — Career" } ], "fixFiles": ["css/themes.css"], "difficulty": "low", "estMinutes": 5, "blocked": false, "reason": "" } ] }` → `["groups[0]: blocked-required"]`; `blocked: true`, `reason: "color change excluded (HOO-81 §16.3)"` → `[]`; `blocked: true`, `reason: "x"` → `["groups[0]: reason-mismatch"]`.
  - FIXTURE_RULE_PLAIN + 그룹 `theme-toggle-size`(fixFiles `["css/style.css"]`, low, 6, blocked false, `""`) → `[]`; 같은 그룹 blocked true·`manual hold` → `[]`.
  - FIXTURE_RULE_COLOR + 그룹 `career-kicker-rule`(fixFiles `["css/style.css"]`, low, 5, blocked false, `""`) → `["groups[0]: blocked-required"]`; blocked true·`color change excluded (HOO-81 §16.3)` → `[]`.
  - FIXTURE_MIXED + 그룹 `kicker-mixed`(두 target, fixFiles `["css/style.css"]`, low, 6): blocked true·`text change excluded; color change excluded (HOO-81 §16.3)` → `[]`; reason `color change excluded (HOO-81 §16.3)` → `["groups[0]: reason-mismatch"]`; blocked false·`""` → `["groups[0]: blocked-required"]`.

## 7. 반응형·인쇄

| 대상 | 375 | 768 | 1280 |
|---|---|---|---|
| `.hero-inner` | 1열(DOM 순서, 좌측) | 1열 | 2열 grid(§11.2) |
| `#heroStats` | 2×2 | 4×1 | 4×1(전체 폭) |
| `#heroFeatured` | 1열 | 2열 | 3열(전체 폭) |
| `#projectGrid`·`#strengthsGrid` | 1열 | 2열 | 3열 |
| Career `.timeline-item` | 세로 | 가로(top 차 < 24px) | 가로 |
| 섹션 padding-top·bottom(career~contact) | 64px | 80px | 96px |
| card gap(`#heroFeatured`, `#projectGrid`, `#strengthsGrid` row·column) | 24px | 24px | 24px |

- 가로 스크롤 없음. hero 2열은 viewport ≥ 1024px(1023 1열, 1024 2열).
- 인쇄: hero·대표·본문 visible·opacity 1, 보이는 `.reveal` 비어 있지 않음, 토글·메뉴·scroll-hint·`#projectModal` display none, line clamp 해제. A(새 페이지): `.lightbox` 없거나 none. B: screen에서 `.lightbox` visible → print에서 `.lightbox`·`#projectModal` none. PDF > 10240바이트, `buf.toString('latin1').match(/\/Type\s*\/Page\b/g)` 개수 ≥ 1.

## 8. 검증 체계

### 8.1 경로
- tracked(빌더 허용): `index.html`, `css/style.css`, `js/main.js`, `js/data.js`, `tests/package.json`, `tests/package-lock.json`, `tests/.gitignore`, `tests/playwright.config.js`, `tests/helpers/**`, `tests/specs/**`, `tests/fixtures/**`(step 명시 파일만), `tests/scripts/**`. `css/themes.css`는 읽기·guard 대상, 변경 금지.
- runtime(추적 금지): `tests/node_modules/**`, `tests/.npm-cache/**`, `tests/.pw-browsers/**`, `tests/.tmp/**`, `tests/test-results/**`, `tests/playwright-report/**`, `tests/screenshots/**`(step 57만).
- Harness managed·policy·lock·state와 외부 evidence는 두 목록 모두 제외.
- `tests/.gitignore` 정확히 7줄(끝 개행만 정규화):

```
node_modules/
.npm-cache/
.pw-browsers/
.tmp/
test-results/
playwright-report/
screenshots/
```

### 8.2 `tests/scripts/with-env.sh`

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

### 8.3 package·Playwright
- `tests/package.json`: `private`, `type: module`, devDependencies `@playwright/test`, `@axe-core/playwright`; scripts `test` `playwright test`, `browsers:install` `playwright install chromium`, `verify-scope` `node scripts/verify-scope.mjs`, `verify-scope:selftest` `node scripts/verify-scope.mjs --self-test`, `fixtures` `node scripts/make-fixtures.mjs`.
- config: webServer `python3 -m http.server 4173 --bind 127.0.0.1`(cwd `..`, reuseExistingServer), baseURL `http://127.0.0.1:4173`, testDir `./specs`, reporter list, retries 0, outputDir `./test-results`, `workers: 1`, `fullyParallel: false`, projects 6개 {mobile 375×812, tablet 768×1024, desktop 1280×800} × {dark, light} 이름 `{viewport}-{theme}`.
- 테마 fixture는 `THEME_KEY` null일 때만 주입, 최초 방문은 fixture 없는 context. `collectConsoleErrors(page)`: 즉시 listener, pageerror 전부, console.error는 Google Fonts 두 도메인 제외, `finish()`는 networkidle 후 `{ pageErrors, consoleErrors }`.

### 8.4 `tests/scripts/verify-scope.mjs`
- step 22 경로: `GIT_DIFF_PATH_ARGS = ['--no-renames', '--name-only']`, `GIT_DIFF_PATCH_ARGS = ['--no-renames', '--unified=0']`(data.js 4구간), `collectInput({ git = runGit })`(읽기만). 빌더 허용 = §8.1 tracked(`css/themes.css` 변경 위반). 하네스 소유(`CLAUDE.md`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`, `.claude/**`, `.codex/**`, `.harness/harness.lock.json`, `.harness/policy.json`, 이 설계 문서, 레거시 `scripts/**`·`templates/**`·`harness-manifest.json`)은 committed 면제·미커밋 위반. 런타임 면제: 그 두 파일 외 `.harness/**`, `.venv/**`, `phases/HOO-81-portfolio-redesign/**`. runtime 추적·루트 package.json 위반.
- step 23 내용: `checkDataJsDiff(patch, { requireExactly3 })`, `--final`, index.html 3종 `Space+Grotesk`, gitignore(index, worktree).

### 8.5 명령 약어·AC 규칙 (step 문서는 이 약어를 그대로 펼쳐 실행)
- `W` = `sh tests/scripts/with-env.sh`; testCommand(모든 step) = `W npm --prefix tests test`(= `FULL`).
- `SNAP N` = `python3 -I tests/scripts/start-snapshot.py stepN`(step 0만 heredoc S, §8.7).
- `T <specs>` = `W npm --prefix tests test -- <specs>`; `VS` = `W npm --prefix tests run verify-scope`; `DI` = `python3 -I tests/scripts/design-intake-check.py`(stdout `design-intake: OK`); `AXE <args>` = `W node tests/helpers/axe.js <args>`.
- `GATE N <A> [<R>]` = `W node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-stepN.json --allow <A> [--require-absent <R>]`(A·R은 쉼표 목록).
- `CGATE N <A>` = `python3 -I - stepN '<A>' '' <<'PY'` + §8.7 C 본문 그대로 + `PY`.
- `GS`(GUARD_SPECS) = `css-parse.spec.js color-vocab.spec.js design-guard-color-pairs.spec.js design-guard-color-rules.spec.js design-guard-color.spec.js design-guard-font.spec.js design-guard-css.spec.js design-guard.spec.js`.
- `COLLECT_CHAIN [--out f]` = `T axe-helper.spec.js && AXE --reset && AXE_COLLECT=1 T axe.spec.js && AXE --merge [--out f]`; `REGRESSION_GATE` = `AXE --check-regression --collected tests/.tmp/axe-current.json`.
- AC는 적힌 순서로 한 셸에서 `&&` 실행, 모두 exit 0. 종료 gate: step 0~11 `SNAP N`(reused) 직후 `CGATE`; step 12부터(재계획 포함) `GATE`. step 22 이후 기본: `T 자기 spec` → `FULL` → `VS` → `GATE`. 시각 step(41~46, 49, 50)과 57은 처음에 `DI`, `T`에 `GS` 포함.

### 8.6 재검증 모드 (step 0~11)
- HEAD에 그 step의 허용 파일이 commit되어 있으면 재검증 모드: `SNAP` → AC → 통과면 파일 불변·로그 `reverify step{N}: no-op`, 실패면 허용 파일 안에서만 고쳐 통과·로그 `reverify step{N}: fixed <파일 목록>`. CGATE require-absent는 `''`. 기능 추가 없음. step 0의 `step0 start clean`은 최초 구축에만.

### 8.7 시작 snapshot과 범위 gate

- RUNTIME = §8.1 runtime 7개 접두어. SKIP = RUNTIME + `.git/` + `.venv/`. EXEMPT = `.harness/`, `.venv/`, `phases/HOO-81-portfolio-redesign/`(GUARDED `.harness/harness.lock.json`, `.harness/policy.json`은 면제 아님).
- 기록 대상 = status path·origPath ∪ `git ls-files -z` ∪ walk의 `tests/` 파일(C·takeCurrent는 start files 키 포함) − SKIP. 값 regular sha256, 없음 null.
- 경로 계약(`rel_ok` = `isRepoRelative`): 문자열, 비어 있지 않음, NUL 없음, 절대 경로 아님, 구성요소가 비거나 `.`·`..` 아님. 적용: snapshot `files` key(C는 `xy`도), status path·origPath. 위반: S 생성 `bad git status`, S 재사용·loader `bad start snapshot: paths: <snapshot>`, C는 key `bad start snapshot: paths: <snapshot>`·status `bad git status`, CLI·`runCheck`는 loader 오류 code 1.
- status parser(S·C·JS 동일): NUL 분할 후 마지막 빈 원소 하나만 버림; 레코드 길이 ≥ 4·세 번째 바이트 공백(위반은 형식 오류); XY·path·origPath 엄격 UTF-8(Python은 `UnicodeDecodeError`를 `ValueError('bad status record')`로); X 또는 Y가 `R`·`C`면 비어 있지 않은 다음 원소가 origPath; 경로 위반은 경로 오류. Python `ValueError('bad status record')`/`ValueError('bad path')`, JS `Error('bad status record: …')`/`Error('bad path: …')`. S 생성·C는 모든 `ValueError`를 `bad git status`로 종료. S·C `parse_status`는 아래 블록 그대로 바이트 동일, 설계 소유자만 변경.
- projectRoot: toplevel(또는 `root`) lstat이 `dir` 아니면 `symlink:`/`missing:`/`non-regular:{root}` 즉시 실패, 그다음 realpath 비교.
- 경로 유형(lstat만): `kind(p)` ∈ `missing|file|dir|symlink|other`; `check(p, leaf)`는 조상부터. 허용 leaf: 기록 대상 `missing|file`; lock `file`; S의 `tests/.tmp` `missing|dir`·snapshot `missing|file`; C·loader·CLI snapshot `file`; after.z `missing|file`.
- 읽기 `O_RDONLY | O_NOFOLLOW | O_NONBLOCK` + fstat regular(아니면 `unsafe path: non-regular:{p}`). 쓰기: snapshot `O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW`; after.z는 unsafe 없을 때만 직전 `check` 후 `O_WRONLY | O_CREAT | O_TRUNC | O_NOFOLLOW | O_NONBLOCK`.
- 실행 전제(trusted-agent canary): snapshot~gate 사이 다른 프로세스가 내부 경로·조상·snapshot·after.z를 바꾸지 않는다. 경쟁 공격·dirfd/openat 테스트 없음.
- symlink 금지: SKIP 밖 모든 symlink 엔트리(SKIP 디렉터리 엔트리 자체 포함) `symlink:{p}`, 면제 없음, follow 없음.
- 순서 S: step id → toplevel → projectRoot → realpath → walk → status·ls-files → 유형 검사(`unsafe path: {정렬}`) → BASE verify → lock → identity → 재사용 검증 또는 생성. C: toplevel → projectRoot → realpath → snapshot·after.z 유형 → snapshot 읽기·형식·key 경로 → status(위반 시 즉시 `bad git status`) → walk → 유형 → unsafe 없을 때만 hash → unsafe면 after.z 미접촉 exit 1 → 판정 → after.z 재검사·쓰기 → 결과.
- 판정: hash 다름 `tests-changed:{p}`/`outside-tests:{p}`, hash 같고 xy 다름 `status-changed:{p}`, 새 RUNTIME status `runtime-visible:{p}`, require-absent `snapshot-not-first:{p}`. 순서: snapshot-not-first → 정렬 unsafe → 경로순 변경 → runtime-visible.
- Git은 `status`·`ls-files`·`rev-parse` 읽기만, python3 표준 라이브러리만.
- schema(strict, v1): 모든 깊이 중복 key·`NaN`·`Infinity` → `invalid json`; 키 정확히 `schemaVersion, stepId, projectRoot, head, base, harness, statusZHex, xy, files`; schemaVersion 최상위 1회·token `1`; stepId `step{N}`|`axe-remediation-{id}`|`parity-{숫자}`; harness = §ID 3값 + `lockSha256`; statusZHex 짝수 길이 소문자 hex·parser 계약; xy = 파싱 결과; files 값 64hex|null·key 경로 계약·status 비SKIP 경로 포함. 검사 순서: invalid json → keys → schemaVersion → (loader만 stepId) → statusZHex → status parse/paths → xy → files → paths → files/status. 메시지 `bad start snapshot: {범주}: <path>`, `start snapshot identity mismatch: {field}`, `unsafe path: {…}`.
- `scanJsonTopLevel(rawText)`(JS, step 2): 공백 skip, 문자열 slice(백슬래시 다음 1문자 skip), 스택, key `JSON.parse` 디코드·중복 throw `duplicate key: {key}`, 깊이 1 값 원문 token, 최상위 비객체 `[]`.
- 최초 없으면 exclusive create(`created`), 있으면 재수집 없이 schema·identity 비교 후 `reused` 또는 exit 1. 덮어쓰기·삭제·재기준화 없음.

스크립트 S — step 0은 어떤 파일보다 먼저 `python3 -I - step0 <<'PY'` + 아래 본문 + `PY`로 실행하고, 같은 본문을 바이트 그대로 `tests/scripts/start-snapshot.py`에 저장한다. 빌더는 이 본문과 이 문서를 바꾸지 않는다.

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

inline 범위 검사 C — step 0~11 종료 검사. 반드시 직전에 S `reused`를 통과한 뒤 `CGATE`(§8.5)로 실행한다. 확정본이며 빌더는 수정·재작성·우회하지 않는다.

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

- 블록 추출(테스트용, 읽기만): `스크립트 S`로 시작하는 줄 다음 첫 fenced block = S 본문, `inline 범위 검사 C`로 시작하는 줄 다음 첫 fenced block = C 본문(``` 줄 제외, 끝 개행 1개 포함). 함수 정의: `def <이름>(` 줄부터 다음 들여쓰기 없는 줄 직전까지. `### 11.1`의 첫 fenced block = intake fixture JSON.
- S·C exec harness(테스트 전용): `python3 -I -c '<harness>'`가 본문을 받아 `subprocess.run`(`rev-parse --show-toplevel`은 지정 경로, `status`는 지정 bytes, 그 밖 git은 기록 후 예외), `os.lstat`·`os.walk`·`os.open`·`os.makedirs`·`builtins.open`을 기록 래퍼로 감싸 `exec`, `SystemExit` 메시지·예외 유형·호출 기록을 JSON 출력.
- 비교 도구 `tests/scripts/scope-snapshot.mjs`(S·C와 같은 판정): step 1 `HARNESS_IDENTITY`(§ID 3값)·`UnsafePathError`·`checkRoot`·`pathKind`·`checkPath`·`readRegular`; step 2 `isRepoRelative`·`parseStatusZ`·`statusXyMap`·`scanJsonTopLevel`·`isSchemaVersion1`; step 3 `loadStartSnapshot`; step 4 `scanProject`·`hashPath`·`takeCurrent`; step 7 `computeIdentity`·`checkIdentity`·`diffAgainstStart`·`classifyChanges`·`checkRuntimeVisible`·`checkSnapshotFirst`·`evaluateGate`; step 8 `writeAfterZ`·`runCheck(opts, deps)`(deps `{ git, fs, root, impl? }`, `impl`은 테스트 전용으로 `checkRoot`, `loadStartSnapshot`, `computeIdentity`, `checkIdentity`, `takeCurrent`, `writeAfterZ`, `evaluateGate` 대체)·CLI `--check <start.json> --allow <list> [--require-absent <list>]`(인자 오류 exit 2). step 5·6·9~11 코드 없음.
- 테스트 격리: 실제 저장소에는 runtime(`tests/.tmp/start-snapshot-parity-{숫자}.json`·after.z, `tests/.tmp/snapshot-probes/__retry_probe.txt`, `tests/.tmp/status-harness-<pid>/`, `tests/.tmp/design-intake-<pid>/`, `tests/.tmp/state-colors-<pid>/`)만 쓴다. 비runtime 검증은 `tests/.tmp/synthetic-repos/<pid>/`(+`<pid>-outside`, `<pid>-link`, `<pid>-file`). subprocess timeout 10초(`make-state-colors.mjs` 60초, 그 spec의 subprocess test마다 `test.setTimeout(75000)`).

## 9. 경계·공통 금지 (§G)

- index.json allowedPaths `index.html`, `css/style.css`, `js/main.js`, `js/data.js`, `tests/`. 각 step 허용 파일 = gate `--allow`.
- `index.html` 구조 변경은 step 41·42·44만. 속성 변경은 remediation 그룹만, 예외는 step 44의 (a) `.scroll-hint` href `#career`, (b) §4 section `class`.
- 빌더 명령: Git 읽기(rev-parse, diff, show, ls-files, ls-tree, status, log, `-w` 없는 hash-object), §8.7 snapshot·검사, `DI`(외부 evidence 읽기). 하네스 전용: Git 상태 변경, Harness 운영 명령, §12. 합성 저장소 `tests/.tmp/synthetic-repos/<pid>/`에서만 `git -C <dir> init -q`, `add -A`/정확한 add, `-c user.name=t -c user.email=t@example.invalid commit -q -m <msg>`.
- 금지(모든 step 공통): main 직접 변경·merge·deploy·push, OpenRouter, root/sudo/권한 변경, 데이터 삭제, `git clean/reset/restore/checkout`·광범위 삭제, SDD 경로; `CLAUDE.md`, `docs/**`(이 문서·S·C 본문), `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`, `css/themes.css`, 시작 snapshot, 외부 evidence 수정; step 허용 목록 밖 파일, 이전 step 함수 동작·spec 변경, 비runtime symlink·특수 파일, §11.3 항목.
- step 공통 절차: read-first(`CLAUDE.md`, `README.md`, 하위 `CLAUDE.md`·`AGENTS.md`, 선행 시각 설계, 지정 절), 선행 completed 확인, npm·node는 `W`, 첫 동작 `SNAP`(created/reused 아니면 중단·보고), runtime 기본 R0 = `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`, 종료 = `FULL` 통과 + AC 마지막 gate 통과.

## 10. Step 목록 (각 20분 이하, 선행 = 작은 번호 전부, 55는 재계획 그룹 포함)

| # | name | 분 | gate |
|---|---|---|---|
| 0 | tests-env-bootstrap (재검증) | 19 | CGATE |
| 1 | scope-snapshot-paths (재검증) | 17 | CGATE |
| 2 | scope-snapshot-parse (재검증) | 19 | CGATE |
| 3 | scope-snapshot-loader (재검증) | 19 | CGATE |
| 4 | scope-snapshot-state (재검증) | 19 | CGATE |
| 5 | scope-snapshot-symlink (재검증) | 18 | CGATE |
| 6 | scope-snapshot-special-files (재검증) | 19 | CGATE |
| 7 | scope-snapshot-identity (재검증) | 18 | CGATE |
| 8 | scope-snapshot-cli (재검증) | 18 | CGATE |
| 9 | scope-snapshot-parity-core (재검증) | 19 | CGATE |
| 10 | scope-snapshot-parity-paths (재검증) | 17 | CGATE |
| 11 | scope-snapshot-parity-artifacts (재검증) | 19 | CGATE |
| 12 | claude-design-intake | 15 | GATE(첫 CLI) |
| 13 | css-parser | 18 | GATE |
| 14 | color-vocab-graph | 18 | GATE |
| 15 | color-rule-pairs | 18 | GATE |
| 16 | color-decl-rules | 18 | GATE |
| 17 | design-guard-color-tokens | 19 | GATE |
| 18 | font-preservation | 18 | GATE |
| 19 | design-guard-css | 18 | GATE |
| 20 | design-guard-integration | 15 | GATE |
| 21 | tests-browser-smoke | 15 | GATE |
| 22 | scope-paths | 19 | GATE |
| 23 | scope-content | 19 | GATE |
| 24 | content-data-baseline | 16 | GATE |
| 25 | content-static-baseline | 17 | GATE |
| 26 | modal-regression | 18 | GATE |
| 27 | ui-regression | 17 | GATE |
| 28 | axe-canonical | 19 | GATE |
| 29 | axe-prepare-page | 15 | GATE |
| 30 | axe-prepare-modal | 18 | GATE |
| 31 | axe-prepare-lightbox | 19 | GATE |
| 32 | axe-collect-tooling | 19 | GATE |
| 33 | axe-baseline-regression | 19 | GATE |
| 34 | axe-baseline-projection | 17 | GATE |
| 35 | axe-remediation-plan-schema | 20 | GATE |
| 36 | axe-plan-executable | 15 | GATE |
| 37 | axe-current-checks | 17 | GATE |
| 38 | axe-regression-prune | 20 | GATE |
| 39 | axe-collect | 17 | GATE |
| 40 | axe-classify | ≤20 | GATE |
| 41 | featured-projects | 19 | GATE |
| 42 | hero-first-screen | 20 | GATE |
| 43 | hero-two-column | 19 | GATE |
| 44 | section-structure | 19 | GATE |
| 45 | section-layout | 17 | GATE |
| 46 | component-hit-open | 19 | GATE |
| 47 | state-sequence | 18 | GATE |
| 48 | state-colors-fixture | 19 | GATE |
| 49 | component-hover-active | 16 | GATE |
| 50 | component-clamp-stripe | 15 | GATE |
| 51 | focus-trap-modal | 17 | GATE |
| 52 | focus-trap-lightbox | 17 | GATE |
| 53 | print-pdf | 17 | GATE |
| 54 | axe-remediation-gate | 18 | GATE |
| (재계획) | axe-remediation-{id} | ≤20 | §6.2 |
| 55 | axe-remediation-recheck | 18 | GATE |
| 56 | axe-finalize | 16 | GATE |
| 57 | final-verification | 17 | GATE |

빌더 재량: §11.2 tokens 안의 비색 타이포 세부값, CSS 클래스 구조(명시 id·data·클래스 유지), 테스트 helper 내부 구조.

## 11. Claude Design

### 11.1 evidence와 intake

- `/design`이 artifact까지 생성했고 전용 MCP·handoff ID 없이 로컬 bundle만 있다. summary `/Users/hoon/.hermes/company/development/product-management/HOO-81-evidence/claude-design-pattern-board-summary-2026-11-24.md`, bundle dir `/Users/hoon/.hermes/company/development/product-management/HOO-81-evidence/claude-design-pattern-board-2026-11-24/`(정확히 9개). 외부 경로는 읽기 전용·gate 대상 아님. bundle 참조 전 항상 `DI`. mockup 문구·숫자·placeholder는 콘텐츠로 쓰지 않는다.
- `tests/fixtures/claude-design-intake.json`(step 12, 파싱 결과 deep-equal):

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

- `tests/scripts/design-intake-check.py [--fixture <path>]`(표준 라이브러리, 쓰기 없음, 기본 위 fixture): `summaryPath`·`bundleDir`·각 파일 lstat이 symlink·non-regular면 `design-intake: unsafe:{path}` → `os.listdir(bundleDir)` 정렬 ≠ `files` key 9개면 `design-intake: files mismatch` → sha256 ≠ fixture면 `design-intake: hash mismatch:{name}` → summary에 `` `{name}` — `{sha}` `` 줄이 없으면 `design-intake: summary mismatch:{name}`; 모두 exit 1. 통과 `design-intake: OK` exit 0.

### 11.2 허용 패턴

- Explore surface: PROJECTS 13개 기존 순서 card grid, card → modal 유지.
- hero(step 42·43): ≥1024px(`@media (min-width: 1024px)`) `display: grid`, `grid-template-columns: minmax(0, 5fr) minmax(0, 7fr)`, column-gap 48px, `grid-template-areas: "eyebrow summary" "name summary" "tagline summary" "role cta" "stats stats" "featured featured"`(DOM 순서 불변), 좌측 정렬; 미만 1열.
- 열 폭 계약(step 43): computed `grid-template-columns` px 두 개 a·b, W = `clientWidth` − 좌우 padding일 때 |a − (W − 48)×5/12| ≤ 1, |b − (W − 48)×7/12| ≤ 1, |a + 48 + b − W| ≤ 1. 1023px: px 값 ≤ 1개 또는 grid 아님, 직계 자식 8개 left = content-box left ±1px, top이 DOM 순 증가. 1024px: 2열 계약 전체.
- 섹션 padding·card gap: §7.
- 측정 helper(step 46, `tests/helpers/component-state.js`, 47~50 재사용, 문서 전체 `document.getAnimations()` 대기 금지):
  - `waitForFiniteAnimations(page, selectors, { timeoutMs = 5000 })`: selector 일치 요소마다 `el.getAnimations({ subtree: true })` 중 `effect.getComputedTiming().iterations !== Infinity`이고 `playState` ∈ `running|pending`만 `Promise.all(animation.finished)`(취소 reject는 완료). 무한 장식(`.caret`, `.scroll-hint span`)은 제외되어 제거 요구 없음. 초과 시 `Error('animation-timeout:{selector}')`.
  - `measureState(page, selector, { nth = 0 }) → { color, backgroundColor, borderColor, outlineColor, transform, opacity, box }`: 먼저 `waitForFiniteAnimations(page, [selector])`. 상태 측정은 이 helper만.
- component state 대상: `.nav-link`, `#menuToggle`, `#themeToggle`, `.hero-cta .btn`, `.featured-card`, `#projectGrid .project-card`, `#projectModal .modal-close`, `#contactActions a`, `.scroll-hint`(보일 때). 색 3속성 = color·background-color·border-color.
  - step 46 hit target(6 project): 기본 상태로 보이는 대상 bbox w·h ≥ 44px.
  - step 46 menu open(`mobile-dark`만, 나머지 `test.skip`): 열기 전 `#menuToggle` 색 3속성 → click → `aria-expanded="true"`·`#navLinks.open` → 보이는 `.nav-link` bbox ≥ 44 → `#menuToggle` 색 3속성 동일 → click → `aria-expanded="false"`.
  - step 46 modal open(6 project): 열기 전 `#projectGrid .project-card[data-project="0"]` 색 3속성 → click → `modal-open`·`#projectModal` visible → `.modal-close` bbox ≥ 44 → button 닫기 → `modal-open` 해제 후 색 3속성 동일.
  - step 46 애니메이션 회귀: `.caret`·`.scroll-hint span` Infinity 애니메이션 실행 중 `#hero`·`.scroll-hint` 측정이 timeout 없이 끝남.
  - step 47 `tests/helpers/state-sequence.js`: `measureStateSequence(context, { url, selector, nth = 0, beforeMeasure = null }) → { default, hover, active }`(step 48 generator·step 49 spec은 이것만). 고정 절차: `context.newPage()` → `goto(url)` → `document.fonts.ready` → `beforeMeasure(page)` → `scrollIntoViewIfNeeded()` → `waitForFiniteAnimations` → `page.mouse.move(0, 0)` 후 default `measureState` → `locator.hover()` 후 hover → `page.mouse.down()` 직후 active → finally에서 down 실행됐으면 `page.mouse.up()`, 항상 `page.close()`. 상태 값 = `{ color, backgroundColor, borderColor, outlineColor, transform, opacity }`. page는 대상마다 새로.
  - step 47 격리·실패: `grid-card-0` 측정 뒤 `grid-card-1` 호출의 `beforeMeasure` 시점 `#projectModal` hidden·`modal-open` 없음; `.hero-cta .btn` 0 측정 뒤 다음 호출 `beforeMeasure`에서 `location.hash === ''`·`scrollY === 0`; 호출마다 page 정확히 1개, 전후 `context.pages().length` 동일; (c) 없는 selector와 (e) active 직전 요소 제거는 `beforeMeasure`에서 먼저 `page.setDefaultTimeout(500)`((e)는 이어 pointerdown 제거 listener) → reject, page 수 원복, 다음 정상 측정 성공; spec `test.setTimeout(60000)`.
  - step 48 `tests/fixtures/component-state-colors.json`(`tests/scripts/make-state-colors.mjs`가 BASE 파일 route 페이지에서 `measureStateSequence`로 생성): 키 `hero-cta-btn-{i}`, `grid-card-0`·`grid-card-1`, 상태 `default`·`hover`·`active`, 값 `{ color, backgroundColor, borderColor }`. spec은 정상 `--check`와 변형 사본 `--check --fixture`를 별도 Playwright test 2개로 나누고, 각 test는 subprocess timeout 60초 유지·준비·정리 포함 첫 줄 `test.setTimeout(75000)`(단독·전체 동일).
  - step 49 hover·active(`desktop-dark`·`desktop-light`): 상태별 현재 색 3속성 = fixture 같은 키·상태; 첫 `.featured-card`(data-project 1) = `grid-card-1` 같은 상태; hover·active 각각 transform 또는 opacity가 default와 다름; outline-color는 default와 같음.
  - step 50: `.featured-blurb`·`#projectGrid` 카드 blurb screen `-webkit-line-clamp: 3`(DOM 전문 유지, 모달·print 전문). BASE `.strength-card::before` 제거 가능(선택).
- focus-visible은 기존 outline(step 52).
- 타이포 위계: font-size·line-height·letter-spacing·margin만. font-weight는 BASE `css/style.css` 값(400·500·600·700)만. BASE `font-family`·`font` 선언은 위치(file·chain·selectors, featured 대응 확장만 허용)·값 유지.

### 11.3 제외(반영 금지)

새 색 값, 기존 색 역할·적용 위치 변경(button/logo dark text `#0d0f12`, muted grey 재배정), 기존 색 규칙 상대 순서 변경, 기존 규칙에 새 색 선언 추가(같은 prop 다른 값 포함)·색 선언 순서 변경, 색 custom property 추가·재정의·삭제·별칭 변경·같은 위치 중복 정의, named color·`currentColor`로 색 역할 변경, 서체 family/weight asset 변경과 BASE `font-family`·`font` 삭제·이동·값 변경·featured 외 확장, `@import` 추가·URL·조건 변경, 새 문구·수치·통계·섹션·이미지·아이콘, 프로젝트 순서·IA 변경, placeholder 실콘텐츠화, `css/themes.css` 변경, hero `min-height`·thumb 비율 등 허용 밖 제안.

### 11.4 design guard (step 13~20)

- step 13 `tests/helpers/css-parse.js`(순수): `parseCssRules(text, file) → Rule[]`, `splitSelectors(text)`, `normalizeValue(value)`. 주석 제거, 따옴표 문자열(이스케이프 포함) 안 `{`·`}`·`;`·`,` 비구조, `url(…)` 안 `;` 무시, `@media`·`@supports`·`@layer`·`@container` 재귀, `@import`·`@charset`·`@font-face`는 Rule. Rule = `{ file, chain, selectors, decls, atRule, prelude, index }`: chain = 바깥 at-rule prelude(공백 정규화, 예 `@media (max-width: 768px)`), selectors = 최상위 쉼표만 분리(`:is(a, b)`·`[data-x="a,b"]` 유지)·공백 정규화, prop 소문자(custom property 원문), value trim·공백 정규화·`!important` 유지, index = file 안 등장 순서(중첩 포함, 0부터), prelude = 일반 규칙·`@font-face` null, `@import`·`@charset`은 at-keyword 뒤~`;` 앞 trim + 연속 공백 1칸(문자열·`url()` 내용·비공백 문자 원문).
- step 14 `tests/helpers/color-vocab.js`: `NAMED_COLORS`(CSS Color 4 148개 + `transparent`); `COLOR_LITERAL_RE` = hex `#[0-9a-fA-F]{3,8}\b` 또는 색 함수 `(?<![A-Za-z0-9_-])(?:rgb|rgba|hsl|hsla|hwb|lab|lch|oklab|oklch|color|color-mix)\s*\(`(플래그 `i`: 함수명 ASCII 대소문자 무시, identifier 경계 앞 조건으로 `mycolor(` 거부, 함수명 뒤 선택적 공백 허용, 괄호 깊이 파싱 없이 바깥 함수 토큰 탐지); `COLOR_PROPS` = `color, background, background-color, background-image, border, border-top, border-right, border-bottom, border-left, border-color, border-top-color, border-right-color, border-bottom-color, border-left-color, border-block, border-block-start, border-block-end, border-block-color, border-block-start-color, border-block-end-color, border-inline, border-inline-start, border-inline-end, border-inline-color, border-inline-start-color, border-inline-end-color, outline, outline-color, column-rule, column-rule-color, text-decoration, text-decoration-color, text-emphasis, text-emphasis-color, -webkit-text-fill-color, -webkit-text-stroke, -webkit-text-stroke-color, fill, stroke, stop-color, flood-color, lighting-color, box-shadow, text-shadow, caret-color, accent-color, scrollbar-color`(shorthand `border`, `border-top|right|bottom|left`, `-color` 아닌 `border-block*`·`border-inline*`, `outline`, `column-rule`, `text-decoration`, `text-emphasis`, `-webkit-text-stroke` 값이 `0`·`none`이면 비색), `valueIdentifiers`(문자열·`url()`·`var()` 인자 제외), `varRefs`(중첩 fallback 포함), `isColorLiteralValue(value)`(따옴표 문자열과 `url(…)` 내용을 먼저 제거한 나머지에서 `COLOR_LITERAL_RE` 일치, named color 식별자(대소문자 무시), `currentColor` 중 하나라도 있으면 true; 문자열·`url()` 안의 `color(` 등은 색 아님), `isColorDecl([prop, value])`(custom property는 항상 false), `customPropertyDefs(rules) → [{ file, chain, selectors, name, value }]`, `colorTokenSet(rules)`(시작 = 리터럴 정의 이름 ∪ 색 선언이 `var()`로 참조하는 이름, 별칭 간선 양방향 고정점), `isColorValue(value, colorTokens)`.
- step 15 `tests/helpers/design-guard-color-pairs.js`(custom property 선언·선언 내용 비교 제외). BASE 색 Rule = 비-custom 색 선언이 있는 BASE Rule. `featuredCounterpart(selector)`(`.project-card`를 모두 `.featured-card`로, 없으면 null); `pairColorRules(baseRules, currentRules) → [{ base, current|null }]`(같은 file·chain에서 selectors ⊇ base.selectors, 같은 file·chain·selectors BASE Rule 여럿이면 등장 순 1:1); `checkColorRulePairs({ baseRules, currentRules })` 순서: BASE 색 Rule을 (file, index) 순으로 규칙 1→2, 그다음 file별 규칙 3, 같은 문자열 처음만, 정렬 없음.
  1. 짝 없는 BASE 색 Rule: selectors가 모두 `.strength-card::before`면 허용, 아니면 `color-rule-missing:{chain}|{selectors}`(chain ` > `, selectors `, `).
  2. 짝 현재 Rule의 추가 선택자가 featured 대응이 아니면 `selector-extended:{현재 selectors}`.
  3. 같은 file에서 짝 있는 BASE 색 Rule을 BASE index 순으로 나열, 인접 P·Q의 current(Q).index < current(P).index면 `color-rule-reordered:{P base selectors}|{Q base selectors}`. 짝 없는 BASE Rule은 빠지고, 새 Rule 삽입·featured 확장은 영향 없음.
- step 16 `tests/helpers/design-guard-color-rules.js`(custom property 제외). BASE 색 선언 배열 = BASE Rule의 비-custom 색 선언(prop, 정규화 value) 등장 순. `checkColorRules({ baseRules, currentRules, colorTokens })` = `checkColorRulePairs` 결과 + 선언 진단(짝 있는 BASE 색 Rule을 BASE 순으로 4→5→6, 그다음 짝 없는 현재 Rule을 현재 순으로 7→8, Rule 안 선언 순), 전체 같은 문자열 처음만, 정렬 없음.
  4. BASE 색 선언 배열 원소가 짝 현재 Rule에 (prop, value)로 없으면 `color-decl-changed:{base selectors}`.
  5. 4가 아닐 때, 짝 현재 Rule 비-custom 선언 중 BASE 색 선언 배열에 있는 것의 등장 순 부분열 ≠ BASE 배열이면 `color-decl-reordered:{base selectors}`(비색 선언 무관).
  6. 짝 현재 Rule의 비-custom 선언 중 (prop, value)가 BASE Rule에 없는 모든 선언(prop 제한 없음)에서 `isColorDecl` 또는 `isColorValue`가 참이면 `color-decl-new:{base selectors}`(값 교체는 4 다음 6).
  7. 짝 없는 현재 Rule의 비-custom 색 선언 또는 `isColorValue` 참 → `color-decl-new:{selectors}`; 예외: selectors 모두 `:focus-visible` 포함, 선언이 `outline`·`outline-offset`뿐, `isColorLiteralValue` 거짓, `varRefs` 모두 colorTokens.
  8. 짝 없는 현재 Rule의 비색 선언 값에 `currentColor`·named color가 있고 같은 file·chain·selectors·선언이 BASE에 없으면 `color-decl-new:{selectors}`.
- step 17 `tests/helpers/design-guard-color.js`. 위치 키 = (file, chain, selectors, name); 같은 Rule 반복 선언과 같은 file·chain·selectors 별도 Rule을 같은 키로 센다. `checkColorTokens({ baseRules, currentRules, colorTokens })` 순서: 규칙 0 전부(현재 키 첫 등장 순) → 1(BASE 순) → 2(현재 순) → 3(BASE 순), 같은 문자열 처음만, 정렬 없음.
  0. 현재 키 개수 N ≥ 2이고 (name ∈ colorTokens 또는 그 키 값 중 하나라도 `isColorValue`)면 값이 같든 다르든 정확히 `색 토큰 중복 정의: <name> @ <file> <chain> <selectors> (count=<N>)`(chain ` > ` 연결, 비면 `-`; selectors `, ` 연결). 이 키는 규칙 1~3에서 제외(정확히 하나일 때만 값·위치 검사).
  1. BASE color token 정의마다 현재 같은 키 개수 0 → `color-token-removed:--x`, 1이고 value 다름 → `color-token-changed:--x`.
  2. BASE에 없는 키이고 현재 정확히 하나: name ∈ colorTokens → `color-token-redefined:--x`, 아니고 `isColorValue` → `color-token-added:--x`.
  3. BASE 비색 custom property(현재 정확히 하나)의 값이 `isColorValue` 참으로 → `color-token-added:--x`.
  - `checkColors({ baseRules, currentRules }) = [...checkColorRules, ...checkColorTokens]`(colorTokens = `colorTokenSet(baseRules)`).
- step 18 `tests/helpers/design-guard-font.js`(atRule null 선언 규칙만): `matchesBaseRule(baseRule, currentRule)`(같은 file·chain, base selectors ⊆ current, current에만 있는 선택자는 모두 base 선택자의 `featuredCounterpart`); `checkFontDecls({ baseRules, currentRules })` = (1) 보존(BASE 순): BASE `font-family`·`font` 선언마다 matchesBaseRule 참이고 같은 prop·value를 가진 현재 Rule이 없으면 `font-decl-missing:{chain}|{selectors}|{prop}`, (2) 신규(현재 순·선언 순): 현재 `font-family`·`font` 선언마다 matchesBaseRule 참이고 같은 prop·value를 가진 BASE Rule이 없으면 `font-asset:{현재 selectors}`; 같은 문자열 처음만. 두 방향 모두 matchesBaseRule만 사용.
- step 19 `tests/helpers/design-guard-css.js`: `checkTypeAndAssets({ baseRules, currentRules })` = `checkFontDecls` 결과 + 현재 등장 순(선언 순) 신규 위반, 전체 중복 제거: BASE에 같은 file·chain·atRule·prelude 없는 `@import` → 정확히 `asset:@import`(정규화 후 같으면 위반 아님); BASE에 같은 file·chain·atRule·선언 없는 `@font-face` → `font-asset:@font-face`, 그 새 `url(` → `asset:@font-face`; BASE style.css 밖 `font-weight` → `font-weight:{value}`; 선언 규칙 새 `url(` → `asset:{selectors}`; 새 `content` ∉ `none`·`''`·`""`·`normal` → `content:{selectors}`; 비색 custom property 정의(BASE 두 파일·현재) 어디에도 없는 `var(--x)` → `unknown-token:--x`. `checkCss({ baseCss, currentCss, baseThemes, currentThemes })` = parse(style `css/style.css`, themes `css/themes.css`) 후 `[...checkColors, ...checkTypeAndAssets]` + `currentThemes !== baseThemes`면 `themes-changed`.
- step 20 `tests/helpers/design-guard.js`: `checkMarkupPatch(patch, kind)`(추가 줄에 `<img`, `<svg`, `<picture`, `<video`, `<i `, `<i>`, `<link`, `<script`, `<font`, `style=`, `.style.color`, `.style.background`, `.style.font` → `markup-asset:{kind}:{n}`); `collectGuardInput({ git, fs })`(`git show <BASE>:css/style.css`, `git show <BASE>:css/themes.css`, worktree 두 CSS 읽기, `git diff --no-renames --unified=0 <BASE> -- index.html`, `-- js/main.js`); `runGuard(input) = [...checkCss, ...checkMarkupPatch(html, 'index.html'), ...checkMarkupPatch(js, 'js/main.js')]`. 이후 모든 `FULL`에서 위반 0.

## 12. fresh runner preflight (승인 후 runner 전, 하네스 수행)

- exact 경로 28개만: `tests/helpers/theme.js`, `tests/specs/smoke.spec.js`; N = 0,1,2,3,4,5,6,7,8,9,10,11,12 각각 `tests/.tmp/start-snapshot-stepN.json`(13개)과 `tests/.tmp/start-snapshot-stepN-after.z`(13개).
- 절차: (1) 각 경로 lstat regular 확인(symlink·디렉터리면 중단), 두 untracked는 `git status --porcelain=v1 -z --untracked-files=all -- <path>`가 `??`; (2) `/Users/hoon/.hermes/company/development/product-management/HOO-81-evidence/preflight-<UTC>/`에 같은 상대 경로로 `cp -p`, `manifest.sha256`(28줄); (3) 원본·복사본 sha256이 모두 같을 때만 `rm --` + 28개 명시 나열(`git clean/reset/restore/checkout`, glob·디렉터리 삭제 금지); (4) 검증: 28개 ENOENT, backup = manifest, HEAD = plan commit, status에 §8.4 런타임 면제 밖 항목 없음, `tests/.tmp`에 `start-snapshot-*` 없음; (5) 목록 밖 `start-snapshot-*` 발견 시 제거하지 않고 중단·대표 지시. 두 untracked 내용은 승인 구현이 아니며 step 21이 새로 작성. Harness 2.0.1 migration·HOO-100(Chromium) 완료.
