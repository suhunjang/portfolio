# Step 21 — content-static-baseline

- 목적: 정적 본문 추출과 허용 예외 판정.
- 예상 17분 / 선행 0~20 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §6, §7.2, §7.3; 셀렉터 `.nav-link`, `.hero-eyebrow`, `.hero-cta .btn`, `.section-kicker`, `.section-title`, `.section-sub`, `.about-text p`, `.about-points li`, `.about-meta dt`, `.contact-text`, `.footer-note`, `.footer-top`
- tracked 허용(exact): `tests/fixtures/content-exceptions.json`(신규), `tests/helpers/content.js`(`extractStatic` 추가만), `tests/specs/content-static.spec.js`(신규)
- runtime: R0
- 금지: §15.7, fixture 생성 스크립트·baseline 파일·content-data.spec, content.js 기존 함수

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step21`
2. `content-exceptions.json`: `kickers.base/final`, `titles.base/final`, `featured.indexes` [1,5,7], `subsectionTitleFinal`.
3. `extractStatic(page)`: 모두 norm, `navLabels`만 정렬.
4. spec(6 project): baseline-index.html을 `javaScriptEnabled: false` context `setContent`로 추출해 현재와 비교, kickers·sectionTitles base 또는 final(순서 포함), final이면 subsection h3 1개, 나머지 BASE와 같음; 합성 base 통과·final 통과·혼합 거부·한 글자 차이 거부.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- content-static.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step21.json --allow tests/fixtures/content-exceptions.json,tests/helpers/content.js,tests/specs/content-static.spec.js` → exit 0
