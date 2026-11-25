# Step 3: hero-and-structure-wave

## Current authoritative contract
Always-on: preserve historical phase/evidence, copy/numbers/fonts/IA, three featured identities and all 13 PROJECTS/order. No new content/framework/custom coordinator/unrelated refactor/palette. css/themes.css read-only. Workers do not commit/push/merge/edit phase metadata. Historical references are read-only context; only current index argv and current contract execute.

- Reference-only: `phases/HOO-81-portfolio-redesign-resume/step20.md`, SHA-256 `9af3100b185a664d99a3baf1785ebbf97469536e4df7064bbeecff6b83dd25d6`. Do **not** execute its legacy RSNAP/REQ/DI/RGATE/FULL/no-op commands; the current argv contract below replaces them.
- Reference-only: `phases/HOO-81-portfolio-redesign-resume/step21.md`, SHA-256 `20cdb7835e939c7e1c4562121ebf3e7ba226be28621fca6fb2817ff4bdc76b78`. Do **not** execute its legacy RSNAP/REQ/DI/RGATE/FULL/no-op commands; the current argv contract below replaces them.
### Current carried-forward requirements from historical boundary 20 (authoritative, not a command)
   - `existing`: 작업 2~3 생략, 쓰기 없는 AC 전체 실행 → 통과 시 `resume step20: no-op`, 실패(또는 `rbranch: existing-changed`) 시 tracked 불변 중단·재계획.
   - `new`: 아래 진행. `rbranch: branch-mixed`면 중단.
2. `DI`(`Main.dc.html`·`DesktopTop.dc.html`·`Mobile.dc.html` 읽기만). RED spec(6 project, tokens는 fixture; `heroColumns(page)` = computed `grid-template-columns` px 배열, `contentWidth(page)` = `clientWidth − paddingLeft − paddingRight`):
   - 1280: `display: grid`; areas = tokens.heroAreas(공백 정규화); column-gap 48px; columns 2개·원 §11.2 5:7·합 허용 오차 ≤1; `#heroName` 오른쪽 ≤ `#heroSummary` 왼쪽; `.hero-cta` 왼쪽 = `#heroSummary` 왼쪽 ±1; `#heroStats`·`#heroFeatured` 폭 ≥ W×0.95; `#heroName`·`#heroSummary` text-align `left`/`start`
   - desktop에서 `setViewportSize`: 1023×800 → columns ≤1 또는 grid 아님·8개 left ±1·top DOM 순 증가; 1024×800 → grid·2열 계약 전체(W 재측정)
   - 375·768: 8개 left ±1·top 증가·좌측 정렬; 모든 project DOM 순서 불변·가로 스크롤 없음
3. style.css(guard 통과).
### Current carried-forward requirements from historical boundary 21 (authoritative, not a command)
2. `DI`(`DesktopExplore.dc.html` 읽기만). RED spec(6 project): 섹션·nav·kicker·h2·section `class` 정확히 원 §4; subsection h3 1개; skillsGrid about 안·h4; contact; `.scroll-hint` `href === '#career'`; heading 계층; `#heroFeatured` 유지; 카드 13개 순서; 스크롤스파이 원 §4 문법(about).
3. subtree 통째 이동, axe canonical 점검(식별 손실이면 중단·재계획).
Current contract: hero CSS lane and section structure lane are independent at completed step2; preserve IDs/nav and render/event signatures; overlap blocks to serial replan. No legacy commands or no-op branch.

## Exact write boundary
hero-layout: css/style.css, tests/specs/hero-layout.spec.js; section-structure: index.html, js/main.js, tests/specs/structure.spec.js

## Output subject
The worker output subject is exclusively the execution.json lane-file diff. Official runner deterministic fan-in is the only committer. Acceptance output is only pass/fail evidence, except an exact `checks.mutation.targetPaths` artifact which official fan-in folds into the same source tree; it is never a separate worker commit.

## Acceptance
Run every immutable argv in index.json for this step in order. Nonzero blocks. emptyAllowed=false means each worker wave must produce its declared artifact/spec/source change; legacy no-op branches do not apply.
