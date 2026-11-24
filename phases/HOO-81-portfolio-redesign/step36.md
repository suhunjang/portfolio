# Step 36 — hero-two-column

- 목적: desktop(≥1024px) 2열 좌측 정렬 hero와 mobile·tablet 1열 전환(설계 §16.2, CSS만).
- 예상 17분 / 선행 0~35 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §5, §9, §16.1~§16.4(DESIGN_HASH_CHECK 후 `Main.dc.html` hero 행·`DesktopTop.dc.html`·`Mobile.dc.html` 읽기 전용); `tests/fixtures/claude-design-intake.json` tokens
- tracked 허용(exact): `css/style.css`(`.hero`·`.hero-inner`와 그 직계 자식의 grid·정렬·간격 규칙만), `tests/specs/hero-layout.spec.js`(신규)
- runtime: R0
- 금지: §15.7, `index.html`, `js/*`, `css/themes.css`, DOM 순서 변경, 색·서체 asset 변경, hero `min-height`·scroll-hint 위치 등 허용 목록 밖 bundle 제안

## 작업 (TDD)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step36` → `python3 -I tests/scripts/design-intake-check.py`
2. `hero-layout.spec.js`(6 project, tokens는 fixture에서 읽음) 먼저 실패 확인
   - 1280: `.hero-inner` computed `display: grid`, `grid-template-areas`가 tokens.heroAreas 6행과 같음(공백 정규화), column-gap 48px; `#heroName` 오른쪽 끝 ≤ `#heroSummary` 왼쪽 끝; `.hero-cta` 왼쪽이 `#heroSummary` 왼쪽과 ±1px; `#heroStats`·`#heroFeatured` 폭 ≥ `.hero-inner` content 폭 × 0.95; `#heroName`·`#heroSummary` computed `text-align`이 `left` 또는 `start`
   - 375·768: 8개 직계 자식의 left가 `.hero-inner` content-box left와 ±1px, top이 DOM 순서대로 증가, `text-align` `left`/`start`
   - DOM 순서 불변(직계 자식 순서 = §5), 가로 스크롤 없음
   - 첫 화면 AC(hero.spec.js)는 전체 실행에서 계속 통과
3. style.css: ≥1024px 미디어 쿼리에서 tokens 값 그대로 grid 정의, 그 외 1열.

## AC

- `python3 -I tests/scripts/design-intake-check.py && sh tests/scripts/with-env.sh npm --prefix tests test -- hero-layout.spec.js hero.spec.js design-guard.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step36.json --allow css/style.css,tests/specs/hero-layout.spec.js --require-absent tests/specs/hero-layout.spec.js` → exit 0
