# Resume Step 7 — hero-two-column (원 step 43)

- 목적: 원 §11.2 hero 2열·5:7 열 폭·1023/1024 전환(CSS만).
- 19분 / 선행 0~6 / 공통 원 §9 + §R1·§R2 no-op / gate `RGATE 7`
- 허용(exact): `css/style.css`(`.hero`·`.hero-inner`·직계 자식 grid·정렬·간격, `@media (min-width: 1024px)`), `tests/specs/hero-layout.spec.js`(신규)
- runtime: R0
- 추가 금지: `index.html`, `js/*`, DOM 순서, 색·서체 asset, hero `min-height`·scroll-hint 위치

## 작업
1. `RSNAP 7` → `DI`(`Main.dc.html`·`DesktopTop.dc.html`·`Mobile.dc.html` 읽기만).
2. RED spec(6 project, tokens는 fixture; `heroColumns(page)` = computed `grid-template-columns` px 배열, `contentWidth(page)` = `clientWidth − paddingLeft − paddingRight`):
   - 1280: `display: grid`; areas = tokens.heroAreas(공백 정규화); column-gap 48px; columns 2개·원 §11.2 5:7·합 허용 오차 ≤1; `#heroName` 오른쪽 ≤ `#heroSummary` 왼쪽; `.hero-cta` 왼쪽 = `#heroSummary` 왼쪽 ±1; `#heroStats`·`#heroFeatured` 폭 ≥ W×0.95; `#heroName`·`#heroSummary` text-align `left`/`start`
   - desktop에서 `setViewportSize`: 1023×800 → columns ≤1 또는 grid 아님·8개 left ±1·top DOM 순 증가; 1024×800 → grid·2열 계약 전체(W 재측정)
   - 375·768: 8개 left ±1·top 증가·좌측 정렬; 모든 project DOM 순서 불변·가로 스크롤 없음
3. style.css(guard 통과).

## AC
- `DI && T hero-layout.spec.js hero.spec.js GS && FULL && VS && RGATE 7 css/style.css,tests/specs/hero-layout.spec.js tests/specs/hero-layout.spec.js`
