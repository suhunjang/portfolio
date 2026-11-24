# Step 39 — hero-two-column

- 목적: desktop(≥1024px) 2열 좌측 정렬 hero와 1열 전환(CSS만).
- 예상 17분 / 선행 0~38 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §5, §9, §16(DESIGN_HASH_CHECK 후 `Main.dc.html`·`DesktopTop.dc.html`·`Mobile.dc.html` 읽기 전용); fixture tokens
- tracked 허용(exact): `css/style.css`(`.hero`·`.hero-inner`와 직계 자식의 grid·정렬·간격만), `tests/specs/hero-layout.spec.js`(신규)
- runtime: R0
- 금지: §15.7, `index.html`, `js/*`, DOM 순서 변경, 색·서체 asset, hero `min-height`·scroll-hint 위치 변경

## 작업 (TDD)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step39` → `python3 -I tests/scripts/design-intake-check.py`
2. `hero-layout.spec.js`(6 project, tokens는 fixture): 1280 — `.hero-inner` computed `display: grid`, `grid-template-areas` = tokens.heroAreas(공백 정규화), column-gap 48px, `#heroName` 오른쪽 ≤ `#heroSummary` 왼쪽, `.hero-cta` 왼쪽 = `#heroSummary` 왼쪽 ±1px, `#heroStats`·`#heroFeatured` 폭 ≥ `.hero-inner` content 폭 × 0.95, `#heroName`·`#heroSummary` text-align `left`/`start`; 375·768 — 8개 직계 자식 left = content-box left ±1px, top이 DOM 순서대로 증가, 좌측 정렬; DOM 순서 불변; 가로 스크롤 없음.
3. style.css(≥1024px 미디어 쿼리).

## AC

- `python3 -I tests/scripts/design-intake-check.py && sh tests/scripts/with-env.sh npm --prefix tests test -- hero-layout.spec.js hero.spec.js css-parse.spec.js design-guard-color.spec.js design-guard-css.spec.js design-guard.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step39.json --allow css/style.css,tests/specs/hero-layout.spec.js --require-absent tests/specs/hero-layout.spec.js` → exit 0
