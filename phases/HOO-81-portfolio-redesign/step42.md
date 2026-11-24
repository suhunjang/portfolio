# Step 42 — hero-two-column

- 목적: desktop(≥1024px) 2열 좌측 정렬 hero(정확한 5:7 열 폭)와 1023/1024px 1열↔2열 전환(CSS만).
- 예상 19분 / 선행 0~41 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §5, §9, §16.2(hero, hero 열 폭 계약), §16(DESIGN_HASH_CHECK 후 `Main.dc.html`·`DesktopTop.dc.html`·`Mobile.dc.html` 읽기 전용); fixture tokens
- tracked 허용(exact): `css/style.css`(`.hero`·`.hero-inner`와 직계 자식의 grid·정렬·간격만, `@media (min-width: 1024px)`), `tests/specs/hero-layout.spec.js`(신규)
- runtime: R0
- 금지: §15.7, `index.html`, `js/*`, DOM 순서 변경, 색·서체 asset, hero `min-height`·scroll-hint 위치 변경

## 작업 (TDD)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step42` → `python3 -I tests/scripts/design-intake-check.py`
2. `hero-layout.spec.js`(6 project, tokens는 fixture; helper `heroColumns(page)` = `.hero-inner` computed `grid-template-columns`를 공백으로 나눠 px 숫자 배열로, `contentWidth(page)` = `clientWidth − paddingLeft − paddingRight`) 먼저 실패 확인:
   - 1280(desktop-dark/light 기본 viewport): `.hero-inner` computed `display: grid`; `grid-template-areas` = tokens.heroAreas(공백 정규화); column-gap = tokens.heroColumnGapPx(48px); `heroColumns` 길이 2, a·b와 W = `contentWidth`에 대해 |a − (W − 48) × 5/12| ≤ 1, |b − (W − 48) × 7/12| ≤ 1, |a + 48 + b − W| ≤ 1; `#heroName` 오른쪽 ≤ `#heroSummary` 왼쪽; `.hero-cta` 왼쪽 = `#heroSummary` 왼쪽 ±1px; `#heroStats`·`#heroFeatured` 폭 ≥ W × 0.95; `#heroName`·`#heroSummary` text-align `left`/`start`
   - 전환 경계(desktop-dark/light에서 `page.setViewportSize`): width 1023(height 800) → `heroColumns` 길이 ≤ 1 또는 display가 grid 아님, 8개 직계 자식 left = content-box left ±1px, top이 DOM 순서대로 증가; width 1024(height 800) → display grid, `heroColumns` 길이 2와 위 5:7·gap 허용 오차 계약 전체(W는 1024에서 다시 측정)
   - 375·768(mobile·tablet project): 8개 직계 자식 left = content-box left ±1px, top이 DOM 순서대로 증가, 좌측 정렬
   - 모든 project: DOM 순서 불변, 가로 스크롤 없음
3. style.css(≥1024px 미디어 쿼리, guard 통과).

## AC

- `python3 -I tests/scripts/design-intake-check.py && sh tests/scripts/with-env.sh npm --prefix tests test -- hero-layout.spec.js hero.spec.js css-parse.spec.js color-vocab.spec.js design-guard-color-pairs.spec.js design-guard-color-rules.spec.js design-guard-color.spec.js design-guard-css.spec.js design-guard.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step42.json --allow css/style.css,tests/specs/hero-layout.spec.js --require-absent tests/specs/hero-layout.spec.js` → exit 0 (전체 `npm --prefix tests test`에 hero-layout.spec.js가 포함되어 이후 모든 step에서 누적 검증)
