# Compact Step 3 — hero-two-column (r20)

- 목적: hero를 2열(5:7)로 만들고 1023/1024px에서 전환한다(원 §11.2). CSS만 바꾼다.
- 예상 16분, hard timeout 30분. 선행: step 2. 공통 선행조건 §C0.
- 허용 파일(exact):
  - `css/style.css`: `.hero`·`.hero-inner`·직계 자식의 grid·정렬·간격, `@media (min-width: 1024px)`만
  - `tests/specs/featured.spec.js`: 보강
- runtime: §C4
- 금지: `index.html`, `js/*`, DOM 순서, 색, hero `min-height`, scroll-hint 위치

## 작업
1. `featured.spec.js`에 assertion을 보강하고 RED를 확인한다.
   - 1280에서:
     - `display: grid`이고 areas가 tokens.`heroAreas`와 같다(공백 정규화 후 비교).
     - column-gap은 48px이다.
     - columns는 2개이고 비율은 5:7이다. 합계 오차는 1 이하다.
     - `#heroName`의 오른쪽 끝이 `#heroSummary`의 왼쪽 끝 이하다.
     - `.hero-cta`의 left가 `#heroSummary`의 left와 ±1 이내다.
     - `#heroStats`와 `#heroFeatured`의 폭이 W×0.95 이상이다.
   - desktop 뷰포트를 1023×800으로 바꾸면 1열이다. 8개 요소의 left가 ±1 이내이고, top은 DOM 순서대로 증가한다.
   - 1024×800에서 1280의 2열 계약이 그대로 성립한다.
   - 375·768에서 1열이고 가로 스크롤이 없다.
2. 구현한다.

## AC
- `OWN_SPEC tests/specs/featured.spec.js`
- `T specs/featured.spec.js`
- `DI`
- `T <GS>`
