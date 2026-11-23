# 포트폴리오 레이아웃·구조 리디자인 설계 (HOO-81)

- 날짜: 2026-11-23 / 브랜치: `feat/HOO-81/portfolio-redesign` (base `main`)
- BASE: `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`
- 선행 시각 설계: `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md` (적용 완료, 계속 유효)
- 합의: Q1 Discord 1574196542901059632, Q2 1574197289084387379, Q3~Q5 1574197696334405756 (추천안 일괄 확정)
- 리뷰 반영: 1차 Astra `1432c5274b33`(12건, 승인 1574220980048634010), 2차 `570513f95a2f`(7), 3차 `9e8c69018dc0`(4), 4차 `8014bc034fb4`(3), 5차 `9277e222d6c3`(4), 6차 `5331b1167a3c`(6), 7차 `e849940ab365`(6), 8차 `77397ef36423`(6), 9차 `1890a28bd4a9`(7), 10차 `754f651120b1`(4), 11차 `2e850c809ca8`(5), 12차 `a26257befcd4`(4), 13차 `b2608d1436cb`(3), 14차 `acc631d51b74`(3), 15차 `927fc70c685a`(2), 16차 `0c7077b8904f`(2), 17차 `6632b4fe978d`(3), 18차 `496edfe61841`(4), 19차 `a37a0eca1d41`(3), 20차 `review-resume-central-a97eb68a108c-v16`(2: 최상위 token scanner·중복 key 거부, 비runtime symlink 거부), 21차 `review-resume-central-010809c8ba59-v17`(2: 고정 S·C·loader·CLI가 open/read/write 전에 projectRoot부터 모든 조상과 leaf 유형을 lstat로 검사하고 `O_NOFOLLOW`·`O_NONBLOCK`·`fstat`로만 읽음, S는 모든 유형 검사를 BASE·lock 읽기와 `tests/.tmp` 생성·snapshot 쓰기보다 먼저 끝냄, after.z 안전 쓰기. 특수 파일 실행 검증 step 4를 추가해 이후 step 번호가 1씩 밀림). 사용자 결정·콘텐츠·비목표는 바뀌지 않았다.
- Harness 실행 identity (중앙 release, `.harness/harness.lock.json`이 고정): sourceCommit `cb179f99acbb9ad32c5dcebab01ff19df7c3f4ae`, manifestHash `287201c44d766b0441470953005450b40f300de2718b246eeb44fd0e3c2f900a`, distributionVersion 2.0.0

## 1. 의도

2026-07-29 작업에서 색·서체·여백을 경영자의 절제 톤으로 정리했고 레이아웃 구조는 범위 밖이었다. 이번 작업은 그 톤을 유지한 채 구조를 다시 짠다. 채용·영입 의사결정자(임원 채용 담당자, 헤드헌터, 대표)가 30초 안에 (1) COO·CTO 포지셔닝, (2) 핵심 지표, (3) 대표 프로젝트 근거를 파악하게 한다.

## 2. 목표 / 비목표 / 실패 조건

- 목표: 1280×800 첫 화면에 이름·tagline·STATS 4개·대표 프로젝트 제목 3개. 섹션을 근거 우선 순서로 재배치. 섹션 리듬·카드·타임라인·모바일 배치 재구성. 기능·콘텐츠 보존을 자동 테스트와 범위 검사로 증명.
- 비목표: 색·서체 재설계, 빌드 도구 도입, 신규 기능, 배포·merge·main 직접 변경.
- 실패 조건(동작해도 실패): §7 예외 밖의 문구·수치·경력 사실 변경/생성, 빈 email·phone·social 채우기, 기존 기능 회귀, axe serious/critical 잔존, 그라데이션·글로우 장식 추가.

## 3. 현재 코드 사실 (read-first 대상)

- 저장소 지침: BASE에는 `README.md`만 있다. 현재 checkout의 하네스 파일은 `CLAUDE.md`, `.harness/harness.lock.json`, `.harness/policy.json`, `.harness/install-state.json`, `.claude/`, `.codex/`, `pytest.ini`, `.python-version`, `.gitattributes`. `.venv/`는 하네스 venv(루트 `.gitignore` 대상). Harness 공통 `scripts/`·`templates/`·`harness-manifest.json`은 중앙 store에 있다.
- `js/data.js`: 전역 const `PROFILE`, `STATS`(4), `CAREER`, `VIS_ACCENT`, `makeVisual`, `PROJECTS`(13, 모두 `detail`), `STRENGTHS`(6), `SKILLS`. `PROFILE.tagline`은 BASE에서 렌더링되지 않는다. email·phone·social.*은 빈 문자열. 대표 프로젝트 index: Motion AD=1, VigoRight(의료 AI/VR)=5, Lost Energy Intel=7.
- `js/main.js`: `setText(id, value)`(첫 인자 id 문자열). 렌더 대상 `#heroStats`(STATS 항목마다 지표 item 1개, item 안에 수치와 label), `#strengthsGrid`, `#timeline`(`.timeline-item` > `.timeline-period` + `.timeline-card`), `#projectGrid`, `#skillsGrid`, `#contactActions`. 카드: `article.project-card.has-detail[data-project=idx][tabindex=0][role=button]`.
- 모달: index.html `div.modal#projectModal[hidden]` > `.modal-backdrop[data-modal-close]` + `.modal-dialog` > (`button.modal-close[data-modal-close]` + `div.modal-body#modalBody`). `#modalBody` 렌더: `.modal-visual`/`.modal-thumb`, `h3#modalTitle.modal-title`, `.modal-meta`, `p.modal-blurb`, `.modal-section`(갤러리 `.shot-zoom` 포함). 제목·닫기 버튼 제외 본문 텍스트는 `#modalBody .modal-blurb`, `#modalBody .modal-section`. `openProjectModal(idx)`는 `lastFocused = document.activeElement` 후 닫기 버튼 포커스, body `modal-open`. 열기는 `#projectGrid` click/keydown 위임, 닫기는 `[data-modal-close]` 또는 Esc(lightbox가 열려 있으면 lightbox부터).
- lightbox: `ensureLightbox()` 최초 호출 때 `.lightbox[role=dialog]`(`button.modal-close` + `img`) 생성, `.shot-zoom`으로 연다. lightbox에만 Tab 고정 리스너가 있고 모달에는 포커스 트랩이 없다.
- 기타: 스크롤스파이 id 배열(about, strengths, career, projects, contact) + IntersectionObserver. reveal은 `.reveal`에 `.in`(reduced-motion이면 즉시). typing `runTyping`(reduced-motion이면 `roles[0]`). 테마 localStorage `THEME_KEY`(없으면 시스템). 메뉴 `#menuToggle`, `#navLinks.open`, `aria-expanded`. `@media print`. Google Fonts Space Grotesk 링크 제거 금지(data.js SVG가 사용).

## 4. 접근 방식

A(선택, Q1): 절제 톤 유지 + 레이아웃·구조 재구성. B(시각 전면 교체)는 선행 작업을 되돌리고, C(마감만)는 체감 변화가 부족하다.

## 5. 첫 화면과 대표 프로젝트 (Q2, Q3)

히어로 DOM 순서: 1 `.hero-eyebrow` → 2 `h1#heroName` → 3 `p.hero-tagline#heroTagline`(신규, 정확히 `setText('heroTagline', PROFILE.tagline)`) → 4 `h2.hero-role`(`#typed`, 보조 크기) → 5 `#heroSummary` → 6 `.hero-cta`(`.btn-primary` 프로젝트 보기, `.btn-ghost` 연락하기) → 7 `ul#heroStats` → 8 대표 프로젝트 컨테이너. 컨테이너 마크업은 정확히:

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

- 카드 안에는 span과 텍스트만 둔다(h1~h6, p, div, ul, ol, li, section, article 금지). 두 span은 `display: block`.
- 대표 카드와 grid 카드는 같은 `data-project`를 가진다. 테스트 helper는 grid 카드를 반드시 `#projectGrid .project-card[data-project="N"]`로 한정한다(§7.4, §8.4).
- 함수: `renderFeaturedProjects(): void`(원본 순서로 `featured === true`만, 새 문자열 하드코딩 금지, 그리드 렌더 직후 호출). `openProjectModal(projectIndex, triggerElement = document.activeElement)`(`lastFocused = triggerElement`, grid는 `(idx, card)`로 호출, `#heroFeatured` click 위임). `closeProjectModal()`은 모든 경로에서 `lastFocused`로 복귀.
- data.js: index 1, 5, 7의 `title:` 다음 줄에 `featured: true,` 총 3줄. 그 밖의 변경 금지.

첫 화면 AC (desktop 1280×800, hero.spec.js 단독 AC와 통합 AC 모두):
- 사전 조건: `document.fonts.ready` 완료, `scrollY === 0`.
- 대상: `#heroName`, `#heroTagline`, `#heroStats` 컨테이너, `.featured-title` 3개, 그리고 지표 item. `#heroStats` 안 지표 item은 정확히 4개이고 DOM 순서대로 `STATS[0..3]`에 대응한다. item마다 item 요소, 수치 요소(텍스트 norm = 해당 STATS 수치 필드), label 요소(텍스트 norm = 해당 STATS label 필드)를 각각 대상으로 한다. 셀렉터는 hero.spec.js 상단 상수 `STAT_ITEM`, `STAT_VALUE`, `STAT_LABEL`로 고정하며 read-first에서 main.js 렌더 코드로 확정한다.
- 각 대상 assertion: `toBeVisible()`, bounding box width·height > 0, 자신과 `document.documentElement`까지 모든 조상의 computed visibility `visible`·opacity `1`(`expect.poll`), left `x >= 0`, top `y >= 0`, right `x + width <= 1280`, bottom `y + height <= 800`.

## 6. 섹션 구조 (Q4)

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

## 7. 콘텐츠 보존과 예외

### 7.1 기준
- `BaselineData`: BASE data.js 평가 결과(step 9). `StaticContent`: BASE index.html 정적 본문(step 10).

### 7.2 허용 예외
1. index 1, 5, 7의 `featured: true`
2. `kickers`(DOM 순서)는 BASE [01 — About, 02 — Strengths, 03 — Career, 04 — Projects, 05 — Stack &amp; Contact] 또는 FINAL [01 — Career, 02 — Projects, 03 — Strengths, 04 — About, 05 — Contact] 중 정확히 하나
3. `sectionTitles`는 BASE [소개, 업무상 강점, 경력 &amp; 창업, 프로젝트 &amp; 제품, 기술 스택 &amp; 연락처] 또는 FINAL [경력 &amp; 창업, 프로젝트 &amp; 제품, 업무상 강점, 소개, 연락처]. FINAL이면 `h3.subsection-title` 기술 스택 정확히 1개
4. nav·섹션 순서(`navLabels`는 정렬 비교)
5. skill-group 제목 heading level
6. axe remediation 그룹 step에서 위반 요소의 aria-*, role, alt, lang, tabindex, for 속성 변경(텍스트 불변)
- 이 밖의 콘텐츠 변경(예: text-change)은 허용하지 않는다. 필요하면 Harness 재계획에서 설계 예외와 allowedPaths를 먼저 확정한다.

### 7.3 helper 계약 (`tests/helpers/content.js`)
- `norm(s) = String(s).replace(/\s+/g, ' ').trim()`
- `BaselineData = { PROFILE, STATS, CAREER, VIS_ACCENT, PROJECTS, STRENGTHS, SKILLS }` (JSON, 순서 유지, deep-equal)
- `StaticContent` (모두 norm): `title`, `metaDescription`, `navLabels`(정렬), `heroEyebrow`, `ctaLabels`, `kickers`, `sectionTitles`, `sectionSubs`(DOM 순서), `aboutParagraphs`(`.about-text p:not([id])`), `aboutPoints`, `aboutMetaTerms`, `contactHeading`, `contactText`, `footerNote`, `footerTop`
- step 9: `readLiveData(page)`, `normalizeFeatured(data)`(structuredClone, 지정 index만). step 10: `extractStatic(page)`

### 7.4 회귀 spec (step 11, 12)
- step 11 `modal-regression.spec.js` + `tests/helpers/modal.js`: 모달·lightbox. step 12 `ui-regression.spec.js` + `first-visit.spec.js`: 테마·최초 방문·메뉴·scrollspy·typing·reduced-motion.
- `modal.js`: `GRID_CARD = '#projectGrid .project-card'`; `gridCard(page, N)` = 정확히 `page.locator('#projectGrid .project-card[data-project="' + N + '"]')`; `openFirstProjectByClick`, `openFirstProjectByEnter`(GRID_CARD 범위); `closeVia(page, 'button'|'backdrop'|'esc')`(button `#projectModal .modal-close[data-modal-close]`, backdrop `{x:5, y:5}`); `expectFocused`; `modalTitle(page)` = `page.locator('#projectModal #modalTitle')`; `findProjectWithShots(page): number|null` — grid 카드만 DOM 순서로 열고(`modal-open` 확인) `.shot-zoom` 유무 확인 후 `closeVia('button')`로 닫고 `modal-open` 해제 확인, 첫 N 또는 null. grid 밖 같은 data-project 요소는 클릭하지 않는다.

## 8. 접근성

### 8.1 axe
- wcag2a·wcag2aa serious/critical 0건. 시나리오 10개: page 3 viewport × 2 테마, modal × dark/light, lightbox × dark/light. 수집·일반 모드 모두 `prepareForAxe` 통과 후에만 실행.

### 8.2 포커스 트랩 (step 30, 31)
- `trapFocus(container, { returnFocusTo? }): () => void` — 스택, 최상위만 Tab 순환, document Tab 핸들러 1개. `release()`는 스택 제거·returnFocusTo 포커스·직전 trap 재개, 다중 호출 안전.
- step 30: 구현 + 모달 열 때 push(trigger)/닫을 때 release, 경계 순환·경로별 복귀. lightbox 코드는 건드리지 않는다.
- step 31: lightbox 열 때 push(`.shot-zoom`), 열린 동안 모달 trap 일시정지, 닫히면 재개, 기존 lightbox Tab 리스너 제거, `:focus-visible` outline 유지·검증.
- h1은 1개, heading level을 건너뛰지 않는다.

### 8.3 axe 기준선·식별·해소

canonical target (step 13): `{ruleId}::{anchor}::{textSig}`. selectors는 정보용.
- anchor(자신부터 조상으로 처음): `[data-featured-card][data-project]`→`featured:{N}`, `[data-project]`→`project:{N}`, `[id]`→`#{id}`, landmark(header/nav/main/footer)→태그명, 없으면 `document`.
- textSig: norm(textContent), 비면 aria-label→alt→title→src 파일명. 숫자는 `#`, 80자 자름. 고정 alias: `## — Stack & Contact`→`## — Contact`, `기술 스택 & 연락처`→`연락처`.
- anchor와 대상의 조상 관계가 유지될 때만 같은 key를 보장한다(subtree 통째 이동은 유지, anchor 밖 이동은 다른 key).

entry key (step 17, 이후 공통): `makeEntryKey({ scenario, project, ruleId })` = `${scenario}:${project}:${ruleId}`(빈 값·`:` 포함 시 throw). (scenario, project, ruleId)마다 entry 1개, targets·selectors 중복 제거·오름차순. 다른 scenario/project의 같은 target은 별도 entry. (key, target) 쌍이 위반 1건. mergeCollected, baseline, validateBaseline, projectEntry, compareCollectedBaseline, checkRegression, checkCollectedRegression, countCollectedTargets, checkGroupDone, checkCollectedCoverage, prunePlan과 step 24 이후 모든 step이 따른다.

helper (`tests/helpers/axe.js`):
- step 13: `ALIASES`, `canonicalTargetInPage(el) → { anchor, text }`, `canonicalFromDescriptor({ ruleId, anchor, text })`, `runAxe(page, { include }) → Violation[]` (`{ ruleId, impact, selectors, targets }`)
- step 17: `makeEntryKey`; `COLLECT_DIR`(`tests/.tmp/axe-collected` 절대경로); `EXPECTED_FILES` 10개(`page-{mobile,tablet,desktop}-{dark,light}.json`, `modal-desktop-{dark,light}.json`, `lightbox-desktop-{dark,light}.json`); `resolveCollectDir(opts)`(opts.collectDir → `AXE_COLLECT_DIR` → COLLECT_DIR, `tests/.tmp/` 밖이면 `Error('collectDir must be under tests/.tmp')`); `resetCollected`; `writeCollected(scenario, project, violations, opts)`(목록 밖 파일명 throw); `mergeCollected({ collectDir, out })`(구성 불일치 `Error('collected files mismatch: missing=[...] extra=[...]')`, 파일명에서 scenario·project, key 정렬, out 기본 `tests/fixtures/axe-collected.json`, `MergedEntry = { key, scenario, project, ruleId, impact, targets, selectors }`). CLI `--reset [--dir]`, `--merge [--dir] [--out]`, throw면 stderr + exit 1.
- step 18: `BASELINE_PATH` `tests/fixtures/axe-baseline.json`, `COLLECTED_PATH` `tests/fixtures/axe-collected.json`, `PLAN_PATH` `tests/fixtures/axe-remediation-plan.json`; `FIX_FILES_BY_KIND` = css-token `[css/themes.css]`, css-rule `[css/style.css]`, js-render `[js/main.js]`, static-markup `[index.html]`, text-change `[]`; `baselineExists`; `loadBaseline`(없음·JSON 오류·비배열 throw); `resolveBaselineMode({ path, collectedPath, planPath } = 기본 경로) → 'check' | 'pending'` — 분류 대기 baseline 계약: baseline 파일이 있으면 `check`; baseline이 없고 collected가 있고 plan이 없으면(step 24 종료~step 25 시작 사이 상태) `pending`; 그 밖(collected 없음, 또는 baseline 없이 plan만 있음)은 `Error('axe baseline missing: tests/fixtures/axe-baseline.json')`. 환경변수로 우회하지 않는다. `validateBaseline`(key = makeEntryKey, 고유, targets 중복 없음·정렬, fixes[i].fixFiles = FIX_FILES_BY_KIND[fixKind], 항목 fixFiles = 합집합); `checkRegression(violations, baseline, scenario, project)`(순수, `new-key:{key}`, `new-target:{key}:{target}`); `assertEmptyFile`; CLI `--assert-empty [path]`.
- step 19: `PROJECTION_FIELDS = ['key','scenario','project','ruleId','impact','targets','selectors']`; `projectEntry`(7필드만, targets·selectors 정렬·중복 제거, 누락·key 불일치 throw); `compareCollectedBaseline(collected, baseline) → { ok, missingEntries, extraEntries, missingTargets, extraTargets, fieldMismatches }`(순수, 중복 key throw, 필드는 scenario·project·ruleId·impact·selectors); CLI `--check-baseline-match [--collected 기본 tests/fixtures/axe-collected.json] [--baseline]`.
- step 20: `GROUP_ID_RE = /^[a-z0-9]+(?:-[a-z0-9]+)*$/`; `loadPlan`; `validateRemediationPlan(plan, baseline, { coverage, requireEmpty })`(requireEmpty면 `groups: expected empty, got {n}`); CLI `--check-plan [--coverage] [--require-empty] [--plan] [--baseline]`.
- step 21: `validateRemediationExecutable(plan, baseline)`(순수, `blocked-group:{id}`, `text-change:{id}:{target}`, `empty-fixfiles:{id}`, groups `[]`면 `[]`); CLI `--check-executable`(실패 시 첫 줄 `Harness 재계획 필요: 실행 불가 remediation 그룹` + 목록, exit 1). 실패하면 remediation step 생성·진행을 멈춘다. `fixFiles = []` 실행 step은 만들지 않는다.
- step 22 (`--collected` 기본 `tests/.tmp/axe-current.json`): `checkGroupDone(collected, plan, id) → { done, remaining }`(비배열 `Error('invalid collected')`, 없는 id `Error('unknown group id: {id}')`); `checkCollectedCoverage → { ok, uncovered }`(자동 편입 없음); `countCollectedTargets`; CLI `--check-group-done <id>`, `--check-coverage`(실패 시 `재계획 필요: plan 밖 잔여 target`), `--assert-no-violations`.
- step 23: `checkCollectedRegression(collected, baseline)`(`bad-key:`, `new-key:`, `new-target:`); `prunePlan(plan, collected, baseline)`(순수, 사라진 target 제거, 빈 그룹 삭제, fixFiles 재계산 부분집합, id·difficulty·estMinutes·blocked·reason 유지, 추가 없음); CLI `--check-regression`, `--prune-plan`(먼저 3파일 읽고 회귀 검사, 실패 시 쓰지 않고 exit 1·bytes 불변, 통과 시 `JSON.stringify(plan, null, 2) + '\n'`). plan 파일은 `--prune-plan`으로만 바꾼다.

fixture:
- `axe-collected.json`(step 24): 병합 결과, tracked, 정보용.
- `axe-baseline.json`(step 25): `key, scenario, project, ruleId, impact, targets, selectors, fixes[{ target, fixKind, fixFiles }], fixFiles`. projectEntry 투영이 collected와 양방향 일치.
- `axe-remediation-plan.json`(step 25): `{ groups: [{ id, targets, fixFiles, difficulty: low|medium|high, estMinutes: 1~20, blocked, reason }] }`. id 고유·형식, target은 baseline 합집합의 부분집합·그룹 간 중복 없음, fixFiles 합집합, text-change면 blocked, `--coverage`면 모든 target이 정확히 한 그룹.

실행 모드:
- 공통: 시나리오마다 `prepareForAxe(page, { scenario })` 후 `runAxe(page, { include })`. 준비 실패는 테스트 실패.
- 수집(`AXE_COLLECT=1`): baseline을 읽지 않고 `writeCollected`만.
- 일반(기본 testCommand): `resolveBaselineMode()`. `check`면 checkRegression·validateBaseline(desktop-dark 1회)·plan이 있으면 validateRemediationPlan(coverage false). `pending`(분류 대기)이면 준비 절차까지만 실행하고 axe 판정은 `test.skip(true, 'axe classification pending (step 25)')`. 그 밖은 throw로 실패.
- 이 계약 덕분에 모든 step 종료 시 기본 testCommand `sh tests/scripts/with-env.sh npm --prefix tests test`가 별도 환경변수 없이 통과한다. step 25 이후에는 baseline이 존재하므로 항상 `check`이며, baseline 삭제는 각 step 범위 gate(§11.7)가 `tests-changed:`로 거부한다.
- COLLECT_CHAIN(순차 `&&`, 병렬 금지): `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset && AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge [--out <f>]`
- REGRESSION_GATE(plan 수정 전, COLLECT_CHAIN 직후): `sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-regression --collected tests/.tmp/axe-current.json`

단계:
- step 24: 10개 시나리오 구현, axe-collected.json 생성. 종료 시 baseline·plan 없음 + collected 있음 = `pending` 상태이므로 기본 testCommand가 통과한다.
- step 25: 예상 = 묶음별(2분 + target × 1분) 합 + 6분. 20분 초과면 즉시 재계획. AC에 `--check-baseline-match`, `--check-executable`. blocked 그룹이 있으면 실패로 끝나고 재계획. 종료 시 `check` 모드로 기본 testCommand 통과.
- step 26~32: 새 key/target은 실패(사라짐 허용, 자동 편입 금지). 해당 step이 만든 신규 위반은 그 step에서 고친다. 식별이 깨지면 중단·재계획.
- step 33 gate(순차): COLLECT_CHAIN(`--merge --out tests/.tmp/axe-current.json`) → REGRESSION_GATE → `--prune-plan --collected tests/.tmp/axe-current.json` → `--check-coverage --collected tests/.tmp/axe-current.json` → `--check-plan` → `--check-executable`. 모두 통과하고 그룹이 남으면 Harness가 그룹마다 `axe-remediation-{id}` step을 33과 34 사이에 재계획한다.
- 재계획 그룹 step: 생성 조건 `--check-executable` 통과·`blocked === false`·`fixFiles.length >= 1`. 소스 allowedPaths는 그룹 fixFiles만, runtime은 §15.6 기본. 20분 이하, plan 수정 금지. 첫 동작 `python3 -I tests/scripts/start-snapshot.py axe-remediation-{id}`. AC: COLLECT_CHAIN(`--out tests/.tmp/axe-current.json`) && REGRESSION_GATE && `--check-group-done {id} --collected tests/.tmp/axe-current.json` && `npm --prefix tests test` && verify-scope && `scope-snapshot.mjs --check tests/.tmp/start-snapshot-axe-remediation-{id}.json --allow {fixFiles}`(경로 유형·schema·identity 포함).
- step 34 recheck: gate를 같은 순서로 재실행 + `--check-plan --require-empty` + `--assert-no-violations --collected tests/.tmp/axe-current.json`.
- step 35 finalize: COLLECT_CHAIN·REGRESSION_GATE 재실행 → `--check-plan --require-empty && --assert-no-violations` 통과 후에만 baseline을 `[]`로. AC `--assert-empty` + 일반 axe 통과.

### 8.4 axe 시나리오 준비 (`tests/helpers/axe-prepare.js`)

- step 14 공통·page: `PREPARE_PREFIX = 'prepareForAxe: '`; `prepareError(code, cause?)`(message `prepareForAxe: {code}`, `.code`, `.cause`); `withPrepareCode(code, fn)`(실패를 prepareError로, 이미 prefix면 그대로); `preparePage(page, { timeoutMs = 10000 }) → { revealChecked, scrollSteps }` — fonts.ready 후 `status === 'loaded'`(`fonts-not-ready`), scrollY 0부터 `innerHeight × 0.8` 간격 끝까지 단계마다 2 frame, `scrollTo(0, 0)`, 모든 `.reveal`의 `.in`·visibility·opacity를 `expect.poll`(`reveal-hidden:{n}`). 테마·reduced-motion은 바꾸지 않는다.
- step 15 콘텐츠·modal: `MODAL_ROOT = '#projectModal'`, `MODAL_BODY_TEXT = '#modalBody .modal-blurb, #modalBody .modal-section'`. `assertContentLoaded(locator, timeoutMs, { textLocator = null } = {})` — locator 안 모든 img `complete && naturalWidth > 0`(`content-not-loaded:img`), 모든 svg bbox w·h > 0(`content-not-loaded:svg`), textLocator가 있으면 1개 이상이고 innerText 합의 norm 길이 > 0(`content-not-loaded:text`), null이면 텍스트 생략. 제목만 있고 본문이 비면 text로 실패. `prepareModal(page, { projectIndex = 0, timeoutMs })` — `gridCard(page, N)` 개수가 1이 아니면 `project-card-not-found:{N}`, click → body `modal-open`·visible·opacity 1(`modal-not-open`), `modalTitle` = `norm(PROJECTS[N].title)`(`modal-not-open`), `assertContentLoaded(page.locator(MODAL_ROOT), t, { textLocator: page.locator(MODAL_BODY_TEXT) })`, 반환 `{ include: '#projectModal', projectIndex }`.
- step 16 lightbox·결합: `prepareLightbox(page, { projectIndex?, timeoutMs })` — 기본 index `findProjectWithShots`(null → `no-shots-project`), prepareModal → 첫 `.shot-zoom` click(없거나 안 열리면 `lightbox-not-open`), `.lightbox` 1개·visible·opacity 1·activeElement 내부(`lightbox-not-open`), `assertContentLoaded(page.locator('.lightbox'), t, { textLocator: null })`, 반환 `{ include: '.lightbox', projectIndex }`. `prepareOverlay`(modal/lightbox, 그 밖 `unknown-scenario`). `prepareForAxe(page, { scenario, projectIndex?, timeoutMs })` — scenario 검증(`unknown-scenario`) → preparePage → page면 `{ include: 'body', projectIndex: null }`, 그 밖은 overlay 결과 병합(`scenario`, `revealChecked`, `scrollSteps` 포함).
- 합성 fixture: 동작 모달 fixture는 `window.PROJECTS`, `#projectGrid .project-card[data-project="N"]`, §3 모달 마크업을 최소 복제하고 grid click handler가 `#modalBody`에 `h3#modalTitle.modal-title`·`p.modal-blurb`·필요 시 `.modal-section`을 채우고 `modal-open`을 붙인다. 닫기 handler(`[data-modal-close]`, Esc)는 숨기고 떼어낸다. `window.__opens`, `__closes`, `__clicks` 기록. handler 없는 fixture는 `modal-not-open` 전용으로 따로 둔다.

## 9. 반응형

| 대상 | 375 | 768 | 1280 |
|---|---|---|---|
| `#heroStats` | 2×2 | 4×1 | 4×1 |
| `#heroFeatured` | 1열 | 2열 | 3열 |
| `#projectGrid` | 1열 | 2열 | 3열 |
| `#strengthsGrid` | 1열 | 2열 | 3열 |
| Career `.timeline-item` | 세로 | 가로(top 차 < 24px) | 가로 |

가로 스크롤 없음.

## 10. 인쇄와 PDF

- 히어로·대표 카드·본문 visible·opacity 1, 보이는 `.reveal` 비어 있지 않음. 토글·메뉴·scroll-hint·`#projectModal` display none.
- A(새 페이지): `.lightbox` 없거나 display none. B(overlay 열림): screen에서 `.lightbox` visible 확인 → print → `.lightbox`·`#projectModal` display none.
- PDF > 10240바이트, `buf.toString('latin1').match(/\/Type\s*\/Page\b/g)` 개수 ≥ 1(`/Pages` 제외), 파서 의존성 없음.

## 11. 검증 체계 (Q5)

### 11.1 경로
- tracked source: 사이트 `index.html`, `css/style.css`, `css/themes.css`, `js/main.js`, `js/data.js`; tests `tests/package.json`, `tests/package-lock.json`, `tests/.gitignore`, `tests/playwright.config.js`, `tests/helpers/**`, `tests/specs/**`, `tests/fixtures/**`, `tests/scripts/**`. (fixtures는 각 step이 명시한 정확한 파일만 허용한다. 디렉터리 전체 허용은 없다.)
- runtime(추적 금지): `tests/node_modules/**`, `tests/.npm-cache/**`, `tests/.pw-browsers/**`, `tests/.tmp/**`, `tests/test-results/**`, `tests/playwright-report/**`, 최종 step만 `tests/screenshots/**`.
- Harness managed·policy·lock·state 파일은 두 목록 모두에서 제외한다.
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
- 직렬화(고정): config에 `workers: 1`, `fullyParallel: false`를 명시한다. 실제 저장소를 읽는 parity·snapshot 테스트와 runtime probe를 쓰는 테스트가 동시에 실행되지 않도록 기본 testCommand와 spec 단독 실행 모두 이 config로 직렬 실행한다. CLI로 workers를 덮어쓰지 않는다. bootstrap.spec.js가 이 값을 검증한다.
- projects 6개: {mobile 375×812, tablet 768×1024, desktop 1280×800} × {dark, light}, 각각 colorScheme·metadata.theme.
- 테마 fixture는 `THEME_KEY`가 null일 때만 주입. 최초 방문 검사는 fixture 없는 별도 context.
- `collectConsoleErrors(page)`: 즉시 listener 등록, pageerror 전부, console.error는 location hostname이 정확히 Google Fonts 두 도메인일 때만 제외(파싱 실패 시 제외 안 함). `finish()`는 networkidle 후 `{ pageErrors, consoleErrors }` 사본(`ErrorRecord = { kind, message, url, line, column }`). 순서: collect → goto → 동작 → finish → 두 배열 `[]`.

### 11.5 `tests/scripts/verify-scope.mjs`
- step 7 경로: `GIT_DIFF_PATH_ARGS = ['--no-renames', '--name-only']`(committed·index·worktree·uncommittedHarness 경로 수집 전용), `GIT_DIFF_PATCH_ARGS = ['--no-renames', '--unified=0']`(data.js 4구간 BASE→HEAD, BASE→index, BASE→worktree, index→worktree 실제 patch 전용). 둘 다 export, 섞지 않음. `collectInput({ git = runGit })`(Git 읽기만), `input.dataJsDiffs`는 실제 patch 문자열. 경로 정책: 빌더 허용 = §11.1 tracked. 하네스 소유(`CLAUDE.md`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`, `.claude/**`, `.codex/**`, `.harness/harness.lock.json`, `.harness/policy.json`, 이 설계 문서, 레거시 `scripts/**`·`templates/**`·`harness-manifest.json`)은 committed 면제·미커밋 위반. 하네스 런타임 면제: 위 두 `.harness` 파일 외 `.harness/**`, `.venv/**`, `phases/HOO-81-portfolio-redesign/**`. runtime 경로 추적·루트 package.json은 위반.
- step 8 내용: `checkDataJsDiff(patch, { requireExactly3 })`(헤더 제외 삭제 줄 0, 추가 줄은 trim 후 `featured: true,`만, 3줄 이하, requireExactly3면 정확히 3). `--final`이면 BASE→HEAD/index/worktree 정확히 3, index→worktree는 공통 규칙만. index.html 3종 `Space+Grotesk` 포함. gitignore(index, worktree) §11.1. 합성: 가짜 git이 PATCH 인자에만 patch, PATH 인자엔 이름 목록을 돌려주고 그 patch가 판정에 쓰임을 확인.

### 11.6 통합 AC
- 모든 step: 첫 동작 §11.7 시작 snapshot, 종료 시 기본 testCommand 통과(환경변수 없음, §8.3 분류 대기 계약), AC 마지막 §11.7 범위 gate.
- 종료 gate의 경로 유형·identity 경유(필수): step 0~4는 `python3 -I tests/scripts/start-snapshot.py step{N}`(`reused` = 경로 유형 검사 + strict schema + 현재 identity 대조) 직후 inline C(경로 유형 검사 + 변경 판정). step 5 이후는 모두 CLI `scope-snapshot.mjs --check`이며, CLI가 snapshot 경로 유형 → strict schema → lock 경로 유형·현재 identity 대조 → 현재 상태 수집(경로 유형) → after.z 안전 쓰기 → 변경 판정 순서로 실행한다. identity가 하나라도 다르거나 경로 유형 검사가 실패하면 어떤 파일도 쓰지 않고 exit 1.
- step 7 이후 기본: 자기 spec 단독 → `npm --prefix tests test` → `verify-scope` → 범위 gate.
- step 35·36은 `--assert-empty`. step 36은 screenshots 단독 → 전체 → `verify-scope -- --final` → gate.

### 11.7 시작 snapshot과 범위 gate

규칙:
- RUNTIME 접두어: §11.1 runtime 7개 디렉터리. SKIP 접두어 = RUNTIME + `.git/` + `.venv/`(하네스 venv, 인터프리터 symlink를 포함): 이 디렉터리 안으로는 걷지 않고 그 아래 경로는 hash·기록하지 않는다. EXEMPT: `.harness/`, `.venv/`, `phases/HOO-81-portfolio-redesign/` (GUARDED `.harness/harness.lock.json`, `.harness/policy.json`은 면제 아님).
- 기록 대상 = status의 path·origPath ∪ `git ls-files -z` ∪ projectRoot walk에서 얻은 `tests/` 아래 파일(C·takeCurrent는 시작 snapshot의 files 키도 포함) − SKIP. 추적·미추적·ignore 무관. 경로별 값: regular file이면 sha256, 경로가 없으면 null. null은 '경로 없음'만 뜻하며 다른 유형을 null로 축약하지 않는다.
- 경로 유형 계약(lstat 전용, 링크를 따라가지 않음): `kind(p)` ∈ `missing`·`file`·`dir`·`symlink`·`other`(FIFO·socket·device 등). `check(p, 허용 leaf 유형)`은 projectRoot 기준 상대 경로 p의 조상을 앞에서부터 모두 lstat한다. 조상이 없으면 leaf를 `missing`으로 보고, 조상이 `dir`가 아니면 `symlink:{조상}` 또는 `non-regular:{조상}`이다. leaf 유형이 허용 목록 밖이면 `symlink:{p}`, `missing:{p}`, 그 밖(`dir`·`other`)은 `non-regular:{p}`.
- 경로별 허용 leaf: 기록 대상 `missing|file`; `.harness/harness.lock.json` `file`; S의 `tests/.tmp`는 `missing|dir`, S의 snapshot 파일은 `missing|file`; C·loader·CLI의 snapshot 파일은 `file`(조상 `tests`, `tests/.tmp`는 `dir`); after.z는 `missing|file`.
- 읽기: 위 검사를 통과한 경로만 `O_RDONLY | O_NOFOLLOW | O_NONBLOCK`으로 열고, 연 fd의 `fstat`가 regular가 아니면 `unsafe path: non-regular:{p}`로 실패한다(FIFO에서 멈추지 않고, 검사 뒤 경쟁 교체도 거부). 쓰기: 새 snapshot은 `O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW`, after.z는 쓰기 직전 `check` 재실행 후 `O_WRONLY | O_CREAT | O_TRUNC | O_NOFOLLOW | O_NONBLOCK`. 그 밖의 파일은 쓰지 않는다.
- symlink 금지(보수적): projectRoot부터 `lstat` 기준으로 트리 전체를 걷는다. 링크를 따라가지 않고 SKIP 디렉터리 내부는 들어가지 않는다. 추적·ignore 여부와 관계없이 발견한 모든 symlink 엔트리(파일·디렉터리·깨진 링크, SKIP 디렉터리 엔트리 자체 포함)는 `symlink:{p}`. allow·EXEMPT·GUARDED 어느 것도 면제하지 않는다. SKIP 내부(예: npm이 만드는 `tests/node_modules/.bin` 링크)는 걷지 않으므로 판정 대상이 아니다. symlink 대상은 resolve·readlink·open·read하지 않는다. realpath는 projectRoot 자체 비교에만 쓴다.
- 실행 순서
  - S: step id → projectRoot·cwd → walk → `git status`·`git ls-files`(Git 읽기) → 기록 대상 전체·lock·`tests/.tmp`·snapshot 경로 유형 검사 → 하나라도 실패면 `unsafe path: {정렬 목록}`으로 exit 1(이 시점까지 프로젝트 파일을 open·read·write·생성하지 않음) → `rev-parse --verify BASE` → lock 읽기 → identity → 재사용(snapshot 읽기·검증) 또는 생성(hash → `tests/.tmp` 생성 → exclusive create).
  - C: snapshot·after.z 경로 유형 검사(실패면 즉시 exit 1, after.z 미생성) → snapshot 읽기 → status → walk → 기록 대상 유형 검사 → unsafe가 없을 때만 hash → after.z 재검사(실패면 쓰지 않고 exit 1) → after.z 쓰기 → 판정.
  - loader·CLI: 아래 비교 도구 계약.
- 판정(시작·현재 합집합 p, allow·EXEMPT 제외): hash 다르면 tests 안 `tests-changed:{p}`, 밖 `outside-tests:{p}`(같은 ` M`에서 내용만 바뀜, 삭제, 시작 시 수정 상태의 원복 모두 거부). hash 같고 xy 다르면 `status-changed:{p}`. 시작에 없던 RUNTIME 경로가 status에 보이면 `runtime-visible:{p}`. `--require-absent` 경로가 시작 기록에 있으면 `snapshot-not-first:{p}`. 순서: snapshot-not-first → 정렬된 unsafe(있으면 이후 판정 생략) → 경로 오름차순 변경 → runtime-visible.
- Git은 `status`, `ls-files`, `rev-parse` 읽기만. python3 표준 라이브러리만.

schema (strict, schemaVersion 1) — 생성·재사용·loader가 모두 같은 규칙으로 검증한다:
- JSON 파싱 공통: 모든 깊이의 중복 key, `NaN`·`Infinity`·`-Infinity`는 `invalid json`. Python은 `json.loads(text, object_pairs_hook=no_dup, parse_constant=no_const)`, JS는 `JSON.parse` 성공 뒤 `scanJsonTopLevel`(중복 key throw)로 같은 판정을 낸다.
- 키 집합 정확히 `schemaVersion, stepId, projectRoot, head, base, harness, statusZHex, xy, files`.
- `schemaVersion`: 최상위 키로 정확히 한 번 있고 값의 lexical token이 정수 리터럴 `1`. Python은 `type(v) is int and v == 1`(중복 key를 거부한 상태에서 Python이 int 1을 만드는 JSON 토큰은 `1`뿐이므로 lexical 판정과 같다. true·1.0·1e0 거부). JS는 `Number.isInteger(v) && v === 1` 그리고 `scanJsonTopLevel` 결과에서 key가 `schemaVersion`인 항목이 정확히 1개이고 그 token이 정확히 `'1'`. 전역 정규식 검색은 쓰지 않으며 중첩 객체·문자열 안의 `schemaVersion`은 판정에 쓰지 않는다.
- stepId는 `step{N}` | `axe-remediation-{id}` | 테스트 전용 `parity-{숫자}`, 파일은 `tests/.tmp/start-snapshot-{stepId}.json`. projectRoot = `git rev-parse --show-toplevel` realpath(cwd가 다르면 실패). head = `git rev-parse HEAD`. base = BASE(`rev-parse --verify BASE^{commit}` 성공 필요). harness = 중앙 identity 3값 + `.harness/harness.lock.json` sha256(`lockSha256`), lock 내용에 3값이 모두 있어야 한다.
- `statusZHex`: 문자열, 짝수 길이, 소문자 hex만. 디코드한 bytes를 NUL 레코드로 엄격 파싱(각 레코드 길이 ≥ 4, 세 번째 바이트 공백, R/C면 비어 있지 않은 다음 필드가 origPath)한다.
- `xy`: 파싱 결과(path와 origPath 모두 → xy)와 정확히 같아야 한다.
- `files`: 객체, 값은 소문자 64자리 hex SHA-256 또는 null(경로 없음). 파싱된 status의 비SKIP 경로는 모두 `files`의 key여야 한다.
- 검증 실패 메시지: `bad start snapshot: {keys|schemaVersion|statusZHex|status parse|xy|files|files/status|invalid json}: <path>`, identity 차이 `start snapshot identity mismatch: {field}`, 경로 유형 `unsafe path: {symlink:p|non-regular:p|missing:p, ...}`.

`scanJsonTopLevel(rawText) → Array<{ key, token }>` (JS, step 1, `JSON.parse`가 성공한 텍스트에만 호출):
- 위치 i를 앞에서부터 한 번 훑는다. 공백(space, tab, LF, CR)은 건너뛴다. 큰따옴표를 만나면 백슬래시 다음 1문자를 건너뛰며 닫는 큰따옴표까지를 문자열 slice로 읽는다(문자열 안의 괄호·쉼표·콜론은 구조로 보지 않는다).
- 스택 원소는 `{ kind: 'object' | 'array', keys: Set, expectKey }`. `{`·`[`는 push, `}`·`]`는 pop. object에서 key 위치의 문자열 slice는 `JSON.parse(slice)`로 디코드하고(이스케이프된 `schema\u0056ersion`도 `schemaVersion`), 그 object의 keys에 이미 있으면 `Error('duplicate key: {key}')`.
- 스택 깊이 1(최상위 객체)의 멤버는 `:` 뒤 값 시작 위치부터 깊이 1로 돌아와 만나는 `,` 또는 `}` 직전까지를 trim한 원문 slice를 token으로 기록한다(값이 객체·배열이면 그 전체 원문).
- 최상위가 객체가 아니면 `[]`. 반환 순서는 원문 순서. 입력을 바꾸지 않는다.

최초 실행·재시도 계약:
- 최초: 파일이 없으면 경로 유형 검사를 모두 끝낸 뒤 수집하고 exclusive create, `start-snapshot: created <path>`.
- 재시도(중간 실패 뒤 포함): 파일이 있으면 같은 경로 유형 검사 후 새로 수집하지 않고 위 strict schema 전체와 identity 필드를 현재 값과 비교한다. 모두 같으면 최초 baseline을 그대로 재사용하고 `start-snapshot: reused <path>`, exit 0. 아니면 exit 1.
- 어떤 경우에도 기존 snapshot을 덮어쓰기·삭제·재기준화하지 않는다. 실패해도 bytes 불변. 불일치는 하네스 조치·재계획 사유로 보고한다.
- gate는 항상 최초 snapshot과 비교한다. step 0의 `tests/`·루트 package.json 부재와 `--require-absent`도 최초 snapshot 기준이다.

스크립트 S — step 0은 어떤 파일보다 먼저 `python3 -I - step0 <<'PY'` + 아래 본문 + `PY`로 실행하고, 같은 본문을 바이트 그대로 `tests/scripts/start-snapshot.py`에 저장한다. step 1 이후 첫 동작은 `python3 -I tests/scripts/start-snapshot.py step{N}`(재시도도 동일). 경로 유형 검사가 BASE 확인보다 먼저이므로 BASE가 없는 합성 저장소에서도 거부 동작을 실행 검증할 수 있다. 빌더는 이 본문을 바꾸지 않는다.

```
import hashlib, json, os, re, stat, subprocess, sys
RUNTIME = ('tests/node_modules/', 'tests/.npm-cache/', 'tests/.pw-browsers/', 'tests/.tmp/', 'tests/test-results/', 'tests/playwright-report/', 'tests/screenshots/')
SKIP = RUNTIME + ('.git/', '.venv/')
BASE = 'd0a8a6e462bc1366757b1401c3ba7aeb0fbf391d'
HARNESS = {'sourceCommit': 'cb179f99acbb9ad32c5dcebab01ff19df7c3f4ae', 'manifestHash': '287201c44d766b0441470953005450b40f300de2718b246eeb44fd0e3c2f900a', 'distributionVersion': '2.0.0'}
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
        xy[rec[3:].decode()] = code
        if code[0] in 'RC' or code[1] in 'RC':
            if i >= len(recs) or not recs[i]:
                raise ValueError('bad status record')
            xy[recs[i].decode()] = code
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
root = os.path.realpath(git('rev-parse', '--show-toplevel').decode().strip())
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
    except ValueError:
        fail('status parse')
    if parsed != oxy:
        fail('xy')
    if not isinstance(ofiles, dict) or any(not (v is None or (isinstance(v, str) and HEX64.fullmatch(v))) for v in ofiles.values()):
        fail('files')
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

inline 범위 검사 C — step 0~4 종료 검사. 반드시 직전에 S `reused`(경로 유형 + strict schema + 현재 identity 대조)를 통과한 뒤 실행한다. 실행: `python3 -I - <stepId> '<allow 쉼표 목록>' '<require-absent 쉼표 목록>' <<'PY'` + 아래 본문 + `PY`. 위반이면 stderr 목록 + exit 1, 아니면 `scope-snapshot: OK`. 현재 status 원문을 `<snapshot 이름>-after.z`에 쓴다(snapshot 자체는 쓰지 않음).

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
pre = [r for r in (check(START, ('file',)), check(AFTER, ('missing', 'file'))) if r]
if pre:
    sys.exit('unsafe path: ' + ','.join(sorted(set(pre))))
start = json.loads(read(START).decode('utf-8'), object_pairs_hook=no_dup)
if not isinstance(start, dict) or set(start) != KEYS or start['stepId'] != STEP:
    sys.exit('bad start snapshot: ' + START)
def git(*args):
    return subprocess.run(['git', *args], check=True, capture_output=True).stdout
status = git('status', '--porcelain=v1', '-z', '--untracked-files=all')
recs = status.split(bytes(1))
xy = {}
i = 0
while i < len(recs):
    rec = recs[i]
    i += 1
    if not rec:
        continue
    code = rec[:2].decode()
    xy[rec[3:].decode()] = code
    if code[0] in 'RC' or code[1] in 'RC':
        xy[recs[i].decode()] = code
        i += 1
unsafe, found = [], []
for top, dirs, names in os.walk('.'):
    rel = '' if top == '.' else top[2:] + '/'
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
files = {}
if not unsafe:
    files = {p: digest(p) for p in targets}
bad = ['snapshot-not-first:' + p for p in sorted(absent) if p in start['files'] or p in start['xy']]
if unsafe:
    bad += sorted(set(unsafe))
else:
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

설계 블록 추출 규칙(테스트용, 읽기 전용): 이 문서에서 `스크립트 S`로 시작하는 줄 다음 첫 fenced code block이 S 본문, `inline 범위 검사 C`로 시작하는 줄 다음 첫 fenced code block이 C 본문이다(여는·닫는 ``` 줄 제외, 끝 개행 1개 포함).

비교 도구 `tests/scripts/scope-snapshot.mjs` (S·C와 같은 판정·문자열·순서):
- step 1 (경로 유형·schema, CLI 없음): 상수 `RUNTIME_PREFIXES`, `SKIP_PREFIXES`, `EXEMPT_PREFIXES`, `GUARDED_PATHS`, `LOCK_PATH`, `SNAPSHOT_KEYS`, `STEP_ID_RE`, `HEX64_RE`, `BASE`, `HARNESS_IDENTITY`(3값), `STATUS_ARGS = ['status','--porcelain=v1','-z','--untracked-files=all']`, `LS_FILES_ARGS = ['ls-files','-z']`. `UnsafePathError`(`.item`). `pathKind(p, { fs, root })`(`lstatSync`만). `checkPath(p, leafKinds, { fs, root }) → string | null`(S의 `check`와 같은 조상·leaf 규칙과 문자열). `readRegular(p, { fs, root })`(`openSync(abs, O_RDONLY | O_NOFOLLOW | O_NONBLOCK)` → `fstatSync().isFile()` 아니면 `UnsafePathError('non-regular:{p}')` → 읽기 → close). `parseStatusZ(raw) → { xy, path, origPath }[]`(S의 `parse_status`와 같은 엄격 규칙, 오류 `Error('bad status record: ...')`). `statusXyMap(entries)`. `scanJsonTopLevel(rawText)`(위 정의). `isSchemaVersion1(value, token)` = `Number.isInteger(value) && value === 1 && token === '1'`. `loadStartSnapshot(file, { fs, root } = {})` 순서: `checkPath(file, ['file'])` 실패면 `Error('unsafe path: {item}')`(open·read 없음) → `readRegular` → `JSON.parse` 실패 `invalid json` → `scanJsonTopLevel`의 duplicate key `invalid json` → 키 집합 `keys` → 최상위 `schemaVersion` 항목 정확히 1개 && `isSchemaVersion1` 아니면 `schemaVersion` → stepId 형식·파일명 일치 → statusZHex → status parse → xy → files(64hex|null) → files/status(비SKIP). 오류는 `Error('bad start snapshot: {범주}: {file}')`, 반환 `{ stepId, identity: { schemaVersion, projectRoot, head, base, harness }, entries, xy, files }`.
- step 2 (상태 수집): `scanProject({ fs, root }) → { unsafe, testsFiles }`(root부터 `readdirSync(withFileTypes)`·`lstatSync`만, SKIP 디렉터리 미진입이나 그 엔트리 자체가 symlink면 기록, 정렬). `hashPath(p, { fs, root }) → string | null`(`pathKind` missing → null; file → `readRegular` sha256; 그 밖 `UnsafePathError`). `takeCurrent(start | null, { git, fs, root = process.cwd() }) → { entries, xy, files, unsafe }`(scanProject unsafe + 기록 대상마다 `checkPath(p, ['missing','file'])` 결과를 unsafe에 모음; unsafe가 하나라도 있으면 hash하지 않고 `files: {}`; 없으면 hashPath, 경쟁으로 생긴 UnsafePathError도 unsafe에 모으고 `files: {}`; 시작 경로는 status에서 사라져도 다시 hash).
- step 3·4: 코드 추가 없음. 합성 저장소·runtime 경로에서 symlink(step 3)와 특수 파일·조상 symlink(step 4) 거부를 S·C·JS로 실행 검증한다.
- step 5 (identity 대조·판정·CLI):
  - `computeIdentity({ git, fs, root = process.cwd() }) → { schemaVersion: 1, projectRoot, head, base, harness }` — `git rev-parse --show-toplevel` realpath가 root realpath와 다르면 throw → `checkPath(LOCK_PATH, ['file'])` 실패면 `UnsafePathError`(BASE 확인·lock 읽기 전) → `git rev-parse HEAD` → `git rev-parse --verify BASE^{commit}` 실패 시 throw → `readRegular(LOCK_PATH)`에 3값 포함 확인 → `lockSha256`.
  - `checkIdentity(start, current) → string[]` — `schemaVersion`, `projectRoot`, `head`, `base`, `harness`(4개 하위 필드 전부 비교) 순서로 다른 필드마다 `identity-mismatch:{field}`. 순수.
  - `diffAgainstStart(start, current) → Change[]`(`{ path, kind: new|deleted|content-changed|status-changed, xyBefore, xyAfter(null 허용) }`, 순수). `classifyChanges(changes, { allow })`. `checkRuntimeVisible(start, current)`. `checkSnapshotFirst(start, paths)`. `evaluateGate(start, current, { allow, requireAbsent })`(current.unsafe가 있으면 snapshot-not-first 다음 정렬된 unsafe만 반환하고 변경 판정 생략; allow는 unsafe를 면제하지 않음).
  - `writeAfterZ(startFile, statusBytes, { fs, root })`: after 경로 = snapshot 이름의 `.json`을 `-after.z`로. `checkPath(after, ['missing','file'])` 실패면 쓰지 않고 `UnsafePathError` → `openSync(abs, O_WRONLY | O_CREAT | O_TRUNC | O_NOFOLLOW | O_NONBLOCK, 0o644)` → `fstatSync().isFile()` 확인 → 쓰기.
  - CLI `--check <start.json> --allow <list> [--require-absent <list>]` 실행 순서: (1) `loadStartSnapshot`(경로 유형 + strict schema) → (2) `computeIdentity` + `checkIdentity` — (1)·(2) 실패면 stderr `unsafe path: …` / `bad start snapshot: …` / `start snapshot identity mismatch: {field}`로 exit 1, 어떤 파일도 쓰지 않는다 → (3) `takeCurrent` → (4) `writeAfterZ`(실패면 stderr `unsafe path: …`, exit 1) → (5) `evaluateGate`; 위반 시 stderr + exit 1, 아니면 `scope-snapshot: OK`. snapshot을 만들거나 고치지 않는다.

테스트 격리 규칙:
- 실제 저장소에 쓰는 테스트 산출물은 runtime 경로만 쓴다: snapshot 테스트는 `tests/.tmp/start-snapshot-parity-{숫자}.json`(거부 테스트용 symlink·FIFO·디렉터리 포함)과 그 `-after.z`, retry probe는 정확히 `tests/.tmp/snapshot-probes/__retry_probe.txt`. 실제 저장소의 비runtime 경로에 파일·symlink·FIFO를 만들지 않는다.
- 비runtime 파일 hash 수집, rename 상태, 비runtime symlink·특수 파일·조상 symlink 거부는 합성 저장소 `tests/.tmp/synthetic-repos/<pid>/`에서 검증한다(§12 예외). 외부 대상은 `tests/.tmp/synthetic-repos/<pid>-outside/`에 두고 고유 sentinel 문자열을 넣어 어떤 출력·snapshot·after.z에도 나타나지 않음을 확인한다. FIFO는 `mkfifo`(Python `os.mkfifo` 또는 `mkfifo` 명령)로만 만든다.
- S·C·CLI subprocess는 항상 timeout 10초로 실행한다(FIFO에서 멈추면 테스트 실패).
- 실제 저장소를 읽는 parity와 probe 테스트의 경합은 §11.4 `workers: 1`로 제거한다.

## 12. 변경 허용 경로와 운영 경계

- index.json allowedPaths: `index.html`, `css/style.css`, `css/themes.css`, `js/main.js`, `js/data.js`, `tests/` (Harness managed·policy·lock·state 제외). 각 step의 tracked 허용 파일 = 범위 gate `--allow`. fixtures는 정확한 파일 단위로만 허용한다.
- `index.html` 구조 변경은 step 26·27·28, 속성 변경은 remediation 그룹 step만. `css/themes.css`는 remediation 그룹 step만.
- 빌더 허용 명령: Git 읽기(rev-parse, diff, show, ls-files, ls-tree, status, log, `-w` 없는 hash-object), §11.7 snapshot·검사. 하네스 전용: 프로젝트 저장소의 Git 상태 변경(init, checkout, switch, add, commit, mv, push, reset, stash, merge, rebase, tag 등), Harness 운영 명령(`harness --project-root . check|plan-session|review-plan|approval|runner`). main 직접 변경·merge·deploy 금지. 고정 S·C 본문을 바꾸거나 우회하는 별도 권한은 없다.
- 합성 저장소 예외: 테스트 코드는 `tests/.tmp/synthetic-repos/<pid>/` 아래 일회용 저장소에서만 Git 변경 명령 `git -C <dir> init -q`, `git -C <dir> add -A` 또는 정확한 경로 지정 `add`, `git -C <dir> -c user.name=t -c user.email=t@example.invalid commit -q -m <msg>` 세 가지를 실행할 수 있다. `git mv`를 포함한 그 밖의 Git 변경 명령은 쓰지 않는다. 파일 이동·삭제·symlink·FIFO 생성은 Node `fs`·Python 파일시스템 API·`mkfifo`로 하고 필요하면 `add`로 stage한다. 권한 변경(chmod 등)은 하지 않는다. 프로젝트 저장소의 index·refs·worktree는 건드리지 않고, 테스트 종료 시 `<pid>`와 `<pid>-outside` 디렉터리를 지운다.
- 빌더 수정 금지: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`, 시작 snapshot 파일.

## 13. Step 목록 (각 20분 이하, snapshot·gate·검증·디버깅 포함, 종료 시 기본 testCommand 통과)

| # | name | 예상 | 선행 |
|---|---|---|---|
| 0 | tests-env-bootstrap | 18 | 없음 |
| 1 | scope-snapshot-schema | 19 | 0 |
| 2 | scope-snapshot-state | 19 | 0~1 |
| 3 | scope-snapshot-symlink | 16 | 0~2 |
| 4 | scope-snapshot-special-files | 19 | 0~3 |
| 5 | scope-snapshot-gate | 20 | 0~4 |
| 6 | tests-browser-smoke | 15 | 0~5 |
| 7 | scope-paths | 19 | 0~6 |
| 8 | scope-content | 19 | 0~7 |
| 9 | content-data-baseline | 16 | 0~8 |
| 10 | content-static-baseline | 17 | 0~9 |
| 11 | modal-regression | 18 | 0~10 |
| 12 | ui-regression | 17 | 0~11 |
| 13 | axe-canonical | 19 | 0~12 |
| 14 | axe-prepare-page | 15 | 0~13 |
| 15 | axe-prepare-modal | 18 | 0~14 |
| 16 | axe-prepare-lightbox | 19 | 0~15 |
| 17 | axe-collect-tooling | 19 | 0~16 |
| 18 | axe-baseline-regression | 19 | 0~17 |
| 19 | axe-baseline-projection | 17 | 0~18 |
| 20 | axe-remediation-plan-schema | 17 | 0~19 |
| 21 | axe-plan-executable | 15 | 0~20 |
| 22 | axe-current-checks | 17 | 0~21 |
| 23 | axe-regression-prune | 19 | 0~22 |
| 24 | axe-collect | 17 | 0~23 |
| 25 | axe-classify | ≤20 (초과 시 재계획) | 0~24 |
| 26 | featured-projects | 19 | 0~25 |
| 27 | hero-first-screen | 20 | 0~26 |
| 28 | section-structure | 19 | 0~27 |
| 29 | section-layout | 16 | 0~28 |
| 30 | focus-trap-modal | 17 | 0~29 |
| 31 | focus-trap-lightbox | 17 | 0~30 |
| 32 | print-pdf | 16 | 0~31 |
| 33 | axe-remediation-gate | 18 | 0~32 |
| (재계획) | axe-remediation-{id} | ≤20 | 33 |
| 34 | axe-remediation-recheck | 18 | 0~33 + 재계획 그룹 |
| 35 | axe-finalize | 16 | 0~34 |
| 36 | final-verification | 16 | 0~35 |

## 14. 빌더 재량

세부 시각 표현(선행 문서 토큰·accent 안), CSS 클래스 구조(명시된 id·data 속성·클래스 유지), 테스트 helper 분할.

## 15. step 공통 절차 (모든 stepN.md가 참조)

1. read-first: `CLAUDE.md`, `README.md`, 하위 디렉터리의 `CLAUDE.md`·`AGENTS.md`, 선행 시각 설계 문서, 이 문서의 step이 지정한 절. index.json에서 선행 step이 모두 completed인지 확인하고 아니면 중단한다.
2. read-only: §12 빌더 수정 금지 목록.
3. 명령 권한: §12.
4. 실행: npm·node는 `sh tests/scripts/with-env.sh <명령>`(step 0은 래퍼 작성 뒤부터). Playwright는 항상 config의 `workers: 1`로 실행한다.
5. 첫 동작: 어떤 파일도 쓰기 전에 §11.7 시작 snapshot(`python3 -I tests/scripts/start-snapshot.py step{N}`, step 0은 heredoc S). 출력이 `created` 또는 `reused`가 아니면(`unsafe path` 포함) 중단·보고. 재시도도 같은 명령으로 최초 baseline을 재사용한다.
6. runtime 쓰기 기본 R0: `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`. step이 추가 경로를 명시할 수 있다.
7. 공통 수정 금지: tests 밖 파일(step이 사이트 파일을 명시한 경우 그 범위만), step 허용 목록 밖 tests 파일, 이전 step이 만든 함수의 동작, 시작 snapshot, 비runtime 경로의 symlink·특수 파일 생성.
8. 종료 조건: 기본 testCommand `sh tests/scripts/with-env.sh npm --prefix tests test`가 환경변수 없이 통과하고, AC 마지막 §11.7 범위 gate가 경로 유형 검사·identity 대조를 거쳐 통과한다(`--allow` = step의 tracked 허용 파일 목록).
