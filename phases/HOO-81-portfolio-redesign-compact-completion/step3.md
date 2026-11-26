# Compact Step 3 — hero-two-column (r20)

- 목적: hero를 5:7 2열로 바꾸고, 1023px과 1024px 사이에서 전환되게 한다(원 §11.2). CSS만 수정한다.
- 예상 16분, hard timeout 30분. 선행 step 2. 공통 선행조건 §C0.
- 허용 파일(exact):
  - `css/style.css`: `.hero`, `.hero-inner`, 직계 자식의 grid·정렬·간격, 그리고 `@media (min-width: 1024px)`만
  - `tests/specs/featured.spec.js`: 보강
- runtime: §C4
- 금지: `index.html`, `js/*`, DOM 순서, 색, hero `min-height`, scroll-hint

## 작업
1. `featured.spec.js`에 아래 assertion을 추가하고 RED를 확인한다.
   - 1280:
     - `display: grid`이고 areas가 tokens.`heroAreas`와 같다.
     - gap이 48px이다.
     - 열 비율이 5:7이고, 합계 오차가 1 이하다.
     - `#heroName`의 right가 `#heroSummary`의 left 이하다.
     - `.hero-cta`가 `#heroSummary`와 ±1 이내로 정렬된다.
     - `#heroStats`와 `#heroFeatured`의 폭이 W×0.95 이상이다.
   - 1023×800: 1열이다. 8개 요소의 left 차이가 ±1 이내이고, top이 증가한다.
   - 1024×800: 1280의 2열 계약이 그대로 성립한다.
   - 375·768: 1열이고 가로 스크롤이 없다.
2. 구현한다.

## AC
- `OWN_SPEC tests/specs/featured.spec.js`
- `T specs/featured.spec.js`
- `DI`
- `T <GS>`
