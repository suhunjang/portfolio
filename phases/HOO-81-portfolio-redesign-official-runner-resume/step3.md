# Step 3: hero-and-structure-wave

## Always-on invariants
Do not modify historical phase records/evidence. Preserve all copy, numbers, font assets/weights, information architecture, 3 featured project identities, all 13 PROJECTS and order. No new copy, section, image, icon, project or placeholder content. css/themes.css is read-only; if it or index.html is required outside the listed lane, stop and replan. Implementation workers must not commit, push, merge, edit the canonical phase index, or write outside their exact lane files. Run only focused tests in lanes; canonical FULL/UI/a11y run at steps 12 and 14.

## Exact work order
### Bound historical contract: `phases/HOO-81-portfolio-redesign-resume/step20.md`
SHA-256 `9af3100b185a664d99a3baf1785ebbf97469536e4df7064bbeecff6b83dd25d6`

# Resume Step 20 — hero-two-column (원 step 43, §R10 분기)

- 목적: 원 §11.2 hero 2열·5:7 열 폭·1023/1024 전환(CSS만).
- 19분 / 선행 0~19 / 공통 원 §9 + §R1·§R10 / gate `RGATE_B 20`
- 허용(exact): `css/style.css`(`.hero`·`.hero-inner`·직계 자식 grid·정렬·간격, `@media (min-width: 1024px)`), `tests/specs/hero-layout.spec.js`(신규)
- 분기 R: `tests/specs/hero-layout.spec.js`
- runtime: R0
- 추가 금지: `index.html`, `js/*`, DOM 순서, 색·서체 asset, hero `min-height`·scroll-hint 위치, start snapshot 수정·재생성, existing 분기에서 R 파일 수정

## 작업
1. `RSNAP 20` → `RBRANCH 20 tests/specs/hero-layout.spec.js`.
   - `existing`: 작업 2~3 생략, 쓰기 없는 AC 전체 실행 → 통과 시 `resume step20: no-op`, 실패(또는 `rbranch: existing-changed`) 시 tracked 불변 중단·재계획.
   - `new`: 아래 진행. `rbranch: branch-mixed`면 중단.
2. `DI`(`Main.dc.html`·`DesktopTop.dc.html`·`Mobile.dc.html` 읽기만). RED spec(6 project, tokens는 fixture; `heroColumns(page)` = computed `grid-template-columns` px 배열, `contentWidth(page)` = `clientWidth − paddingLeft − paddingRight`):
   - 1280: `display: grid`; areas = tokens.heroAreas(공백 정규화); column-gap 48px; columns 2개·원 §11.2 5:7·합 허용 오차 ≤1; `#heroName` 오른쪽 ≤ `#heroSummary` 왼쪽; `.hero-cta` 왼쪽 = `#heroSummary` 왼쪽 ±1; `#heroStats`·`#heroFeatured` 폭 ≥ W×0.95; `#heroName`·`#heroSummary` text-align `left`/`start`
   - desktop에서 `setViewportSize`: 1023×800 → columns ≤1 또는 grid 아님·8개 left ±1·top DOM 순 증가; 1024×800 → grid·2열 계약 전체(W 재측정)
   - 375·768: 8개 left ±1·top 증가·좌측 정렬; 모든 project DOM 순서 불변·가로 스크롤 없음
3. style.css(guard 통과).

## AC
- `DI && T hero-layout.spec.js hero.spec.js GS && FULL && VS && RGATE_B 20 css/style.css,tests/specs/hero-layout.spec.js tests/specs/hero-layout.spec.js`


### Bound historical contract: `phases/HOO-81-portfolio-redesign-resume/step21.md`
SHA-256 `20cdb7835e939c7e1c4562121ebf3e7ba226be28621fca6fb2817ff4bdc76b78`

# Resume Step 21 — section-structure (원 step 44)

- 목적: 원 §4 FINAL 섹션·nav·kicker·heading.
- 19분 / 선행 0~20 / 공통 원 §9 + §R1·§R2 no-op·§R11 / gate `RGATE 21`
- 허용(exact): `index.html`(hero 밖 섹션 subtree 이동·kicker·Stack &amp; Contact 분리·nav 순서·scroll-hint, 속성은 원 §9 (a)·(b)만), `js/main.js`(스크롤스파이 배열·skill-group h4만), `tests/specs/structure.spec.js`
- 필수 산출물(REQ): `tests/specs/structure.spec.js,index.html,js/main.js`
- runtime: R0
- 추가 금지: `css/*`, `js/data.js`, hero 내부, 표에 없는 문구, (a)·(b) 밖 속성, 새 섹션·이미지·아이콘

## 작업
1. `RSNAP 21` → no-op 첫 probe `REQ 21 tests/specs/structure.spec.js,index.html,js/main.js`. PASS면 나머지 AC 실행 → 통과 시 `resume step21: no-op`. REQ FAIL 또는 AC 실패면 아래 작업 후 완전한 AC 재실행.
2. `DI`(`DesktopExplore.dc.html` 읽기만). RED spec(6 project): 섹션·nav·kicker·h2·section `class` 정확히 원 §4; subsection h3 1개; skillsGrid about 안·h4; contact; `.scroll-hint` `href === '#career'`; heading 계층; `#heroFeatured` 유지; 카드 13개 순서; 스크롤스파이 원 §4 문법(about).
3. subtree 통째 이동, axe canonical 점검(식별 손실이면 중단·재계획).

## AC
- `REQ 21 tests/specs/structure.spec.js,index.html,js/main.js && DI && T structure.spec.js GS && FULL && VS && RGATE 21 index.html,js/main.js,tests/specs/structure.spec.js`(첫 명령 stdout `required-artifacts step121: OK 3`; content-static.spec에서 final 성립)


The two lanes start from completed step2 and may not read each other's uncommitted changes. Hero lane owns only `.hero*` layout selectors and hero tests. Structure lane owns `index.html`, `js/main.js`, and structure tests for Career→Projects→Strengths→About→Contact; it must preserve IDs, navigation targets and render/event signatures. If an exact anchor overlaps, fail the lane and use serial fallback.

## Exact write boundary
hero-layout: css/style.css, tests/specs/hero-layout.spec.js; section-structure: index.html, js/main.js, tests/specs/structure.spec.js

## Acceptance
Run every argv in this step’s immutable `index.json.acceptanceCommands` in order. Any nonzero exit blocks the next step.
