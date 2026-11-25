# Step 4: section-layout

## Always-on invariants
Do not modify historical phase records/evidence. Preserve all copy, numbers, font assets/weights, information architecture, 3 featured project identities, all 13 PROJECTS and order. No new copy, section, image, icon, project or placeholder content. css/themes.css is read-only; if it or index.html is required outside the listed lane, stop and replan. Implementation workers must not commit, push, merge, edit the canonical phase index, or write outside their exact lane files. Run only focused tests in lanes; canonical FULL/UI/a11y run at steps 12 and 14.

## Exact work order
### Bound historical contract: `phases/HOO-81-portfolio-redesign-resume/step22.md`
SHA-256 `5ecdf9c81f328bb57cd7be24d222ef5dc2cbc2f13e0520c5933707ac0e92d36a`

# Resume Step 22 — section-layout (원 step 45)

- 목적: 원 §7 섹션 padding·card gap·Career·그리드·비색 타이포 위계.
- 17분 / 선행 0~21 / 공통 원 §9 + §R1·§R2 no-op·§R11 / gate `RGATE 22`
- 허용(exact): `css/style.css`(섹션 padding, Career, 그리드 gap·열, 섹션 제목·`.subsection-title` 비색 타이포만), `tests/specs/layout.spec.js`
- 필수 산출물(REQ): `tests/specs/layout.spec.js,css/style.css`
- runtime: R0
- 추가 금지: `index.html`, `js/*`, 원 §11.3

## 작업
1. `RSNAP 22` → no-op 첫 probe `REQ 22 tests/specs/layout.spec.js,css/style.css`. PASS면 나머지 AC 실행 → 통과 시 `resume step22: no-op`. REQ FAIL 또는 AC 실패면 아래 작업 후 완전한 AC 재실행.
2. `DI`(`DesktopExplore.dc.html`·`Mobile.dc.html`·`Foundations.dc.html` 읽기만). RED spec(6 project, tokens): 가로 스크롤 없음; `#career`~`#contact` padding-top·bottom = tokens.sectionPaddingPx[viewport]; 세 grid row·column-gap 24px; projectGrid·strengthsGrid 3/2/1열; Career 375 세로·768/1280 가로(top 차 < 24); 375 highlights 보임; `.subsection-title` weight ≤ h2·size < h2.
3. style.css.

## AC
- `REQ 22 tests/specs/layout.spec.js,css/style.css && DI && T layout.spec.js GS && FULL && VS && RGATE 22 css/style.css,tests/specs/layout.spec.js`(첫 명령 stdout `required-artifacts step122: OK 2`)


Runs after structure fan-in. Own only section layout selectors and layout spec; no color declaration changes.

## Exact write boundary
section-layout: css/style.css, tests/specs/layout.spec.js

## Acceptance
Run every argv in this step’s immutable `index.json.acceptanceCommands` in order. Any nonzero exit blocks the next step.
