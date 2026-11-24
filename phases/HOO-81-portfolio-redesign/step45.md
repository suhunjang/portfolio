# Step 45 — section-layout

- 목적: §7 섹션 padding·card gap·Career·그리드·비색 타이포 위계.
- 17분 / 선행 0~44 / 공통 §9 / gate GATE
- 허용(exact): `css/style.css`(섹션 padding, Career, 그리드 gap·열, 섹션 제목·`.subsection-title` 비색 타이포만), `tests/specs/layout.spec.js`
- runtime: R0
- 추가 금지: `index.html`, `js/*`, §11.3

## 작업
1. `SNAP 45` → `DI`(`DesktopExplore.dc.html`·`Mobile.dc.html`·`Foundations.dc.html` 읽기만).
2. RED spec(6 project, tokens): 가로 스크롤 없음; `#career`~`#contact` padding-top·bottom = tokens.sectionPaddingPx[viewport]; 세 grid row·column-gap 24px; projectGrid·strengthsGrid 3/2/1열; Career 375 세로·768/1280 가로(top 차 < 24); 375 highlights 보임; `.subsection-title` weight ≤ h2·size < h2.
3. style.css.

## AC
- `DI && T layout.spec.js GS && FULL && VS && GATE 45 css/style.css,tests/specs/layout.spec.js`
