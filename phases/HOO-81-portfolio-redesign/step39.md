# Step 39 — section-layout

- 목적: 섹션 padding(64/80/96px), card gap 24px, Career·그리드 반응형, 비색 타이포 위계.
- 예상 17분 / 선행 0~38 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §6, §9, §16(DESIGN_HASH_CHECK 후 `DesktopExplore.dc.html`·`Mobile.dc.html`·`Foundations.dc.html` 읽기 전용); fixture tokens
- tracked 허용(exact): `css/style.css`(섹션 padding, Career, 그리드 gap·열, 섹션 제목·`.subsection-title` 비색 타이포만), `tests/specs/layout.spec.js`
- runtime: R0
- 금지: §15.7, `index.html`, `js/*`, 색·서체 asset, BASE 밖 font-weight

## 작업 (TDD)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step39` → `python3 -I tests/scripts/design-intake-check.py`
2. `layout.spec.js`(6 project, tokens는 fixture): 가로 스크롤 없음; `#career`~`#contact` padding-top·bottom = tokens.sectionPaddingPx; `#heroFeatured`·`#projectGrid`·`#strengthsGrid` row-gap·column-gap 24px; 3/2/1열; Career 375 세로·768/1280 가로; 375 highlights 보임; `.subsection-title` weight ≤ h2, size < h2.
3. style.css.

## AC

- `python3 -I tests/scripts/design-intake-check.py && sh tests/scripts/with-env.sh npm --prefix tests test -- layout.spec.js design-guard-css.spec.js design-guard.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step39.json --allow css/style.css,tests/specs/layout.spec.js` → exit 0
