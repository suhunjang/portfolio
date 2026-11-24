# Step 25 — content-static-baseline

- 목적: 정적 본문 추출과 §5 허용 예외 판정.
- 17분 / 선행 0~24 / 공통 §9 / gate GATE
- 허용(exact): `tests/fixtures/content-exceptions.json`(신규), `tests/helpers/content.js`(`extractStatic` 추가만), `tests/specs/content-static.spec.js`(신규)
- runtime: R0
- 추가 금지: fixture 생성 스크립트·baseline·content-data.spec, content.js 기존 함수

## 작업
1. `SNAP 25`
2. 셀렉터 `.nav-link`, `.hero-eyebrow`, `.hero-cta .btn`, `.section-kicker`, `.section-title`, `.section-sub`, `.about-text p`, `.about-points li`, `.about-meta dt`, `.contact-text`, `.footer-note`, `.footer-top`. `content-exceptions.json`: `kickers.base/final`, `titles.base/final`, `featured.indexes` [1,5,7], `subsectionTitleFinal`.
3. spec(6 project): baseline-index.html을 `javaScriptEnabled: false` `setContent`로 추출해 비교, kickers·sectionTitles base 또는 final, final이면 subsection h3 1개, 나머지 BASE와 같음; 합성 base·final 통과, 혼합·한 글자 차이 거부.

## AC
- `T content-static.spec.js && FULL && VS && GATE 25 tests/fixtures/content-exceptions.json,tests/helpers/content.js,tests/specs/content-static.spec.js`
