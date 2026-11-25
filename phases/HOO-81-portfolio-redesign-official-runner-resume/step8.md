# Step 8: hover-and-clamp

## Always-on invariants
Do not modify historical phase records/evidence. Preserve all copy, numbers, font assets/weights, information architecture, 3 featured project identities, all 13 PROJECTS and order. No new copy, section, image, icon, project or placeholder content. css/themes.css is read-only; if it or index.html is required outside the listed lane, stop and replan. Implementation workers must not commit, push, merge, edit the canonical phase index, or write outside their exact lane files. Run only focused tests in lanes; canonical FULL/UI/a11y run at steps 12 and 14.

## Exact work order
### Bound historical contract: `phases/HOO-81-portfolio-redesign-resume/step26.md`
SHA-256 `2d0b13219c2142c37995e87b8faf5f27f5d6f1bd83849d7ef50acc15bd0a8fca`

# Resume Step 26 — component-hover-active (원 step 49, §R10 분기)

- 목적: 원 §11.2 step 49 비색 hover·active와 상태별 BASE 색 보존.
- 16분 / 선행 0~25 / 공통 원 §9 + §R1·§R10 / gate `RGATE_B 26`
- 허용(exact): `css/style.css`(`.hero-cta .btn`·`.featured-card`·`#projectGrid .project-card`의 `:hover`·`:active`에서 transform·opacity·transition만), `tests/specs/component-hover.spec.js`(신규)
- 분기 R: `tests/specs/component-hover.spec.js`
- runtime: R0
- 추가 금지: `index.html`, `js/*`, 색 선언·순서, hit·clamp, focus-visible, helper·generator·fixture·기존 spec, `measureStateSequence` 밖 측정, page 단위 테마 주입, start snapshot 수정·재생성, existing 분기에서 R 파일 수정

## 작업
1. `RSNAP 26` → `RBRANCH 26 tests/specs/component-hover.spec.js`.
   - `existing`: 작업 2~3 생략, 쓰기 없는 AC 전체 실행 → 통과 시 `resume step26: no-op`, 실패 시 tracked 불변 중단·재계획.
   - `new`: 아래 진행. `branch-mixed`면 중단.
2. `DI`(`Components.dc.html` 읽기만). RED spec(`desktop-dark`·`desktop-light`, §THEME `test`의 `context`·url `/`, `measureStateSequence`만): `hero-cta-btn-{i}`·`grid-card-0`·`grid-card-1` 상태별 색 3속성 = fixture[project 테마]; 첫 `.featured-card` = `grid-card-1`; hover·active 각각 transform 또는 opacity ≠ default; outline-color = default.
3. style.css(guard 통과).

## AC
- `DI && W node tests/scripts/make-state-colors.mjs --check && T component-hover.spec.js state-sequence.spec.js state-colors.spec.js component-hit.spec.js GS && FULL && VS && RGATE_B 26 css/style.css,tests/specs/component-hover.spec.js tests/specs/component-hover.spec.js`


### Bound historical contract: `phases/HOO-81-portfolio-redesign-resume/step27.md`
SHA-256 `e92b00655ea81a66ac48f61a43e5e4fb9e7e648e5999c4ddfea096cf4b2c9edb`

# Resume Step 27 — component-clamp-stripe (원 step 50, §R10 분기)

- 목적: blurb line clamp 3, 본문 보존, 선택적 stripe 제거.
- 15분 / 선행 0~26 / 공통 원 §9 + §R1·§R10 / gate `RGATE_B 27`
- 허용(exact): `css/style.css`(`.featured-blurb`·`CARD_BLURB` line clamp 비색 규칙, BASE `.strength-card::before` 삭제만), `tests/specs/component-clamp.spec.js`(신규)
- 분기 R: `tests/specs/component-clamp.spec.js`
- runtime: R0
- 추가 금지: `index.html`, `js/*`, 색 선언·순서, 그 밖 strength 규칙, print(resume 30), helper·기존 spec, start snapshot 수정·재생성, existing 분기에서 R 파일 수정

## 작업
1. `RSNAP 27` → `RBRANCH 27 tests/specs/component-clamp.spec.js`.
   - `existing`: 작업 2~3 생략, 쓰기 없는 AC 전체 실행 → 통과 시 `resume step27: no-op`, 실패 시 tracked 불변 중단·재계획.
   - `new`: 아래 진행. `branch-mixed`면 중단.
2. `DI`(`DesktopExplore.dc.html`·`Components.dc.html` 읽기만). RED spec(6 project, 읽기 전 `waitForFiniteAnimations`, spec 상수 `CARD_BLURB`): `.featured-blurb` 3·grid 카드 13 `-webkit-line-clamp` = `3`; textContent(norm) = `PROJECTS[i].blurb`; 카드 0 모달 `.modal-blurb` clamp `none`·전문; `.strength-card` 6개 = `STRENGTHS` 순서·내용.
3. style.css.

## AC
- `DI && T component-clamp.spec.js component-hover.spec.js component-hit.spec.js GS && FULL && VS && RGATE_B 27 css/style.css,tests/specs/component-clamp.spec.js tests/specs/component-clamp.spec.js`


These remain serial inside one exact-file lane because both touch CSS state/clamp anchors. Re-run state-colors to catch semantic dependency regressions.

## Exact write boundary
hover-clamp: css/style.css, tests/specs/component-hover.spec.js, tests/specs/component-clamp.spec.js

## Acceptance
Run every argv in this step’s immutable `index.json.acceptanceCommands` in order. Any nonzero exit blocks the next step.
