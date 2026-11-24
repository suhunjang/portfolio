# Step 40 — hero-first-screen

- 목적: 히어로 DOM 순서·tagline과 첫 화면 AC(지표 item 4개 개별). 2열은 step 41.
- 예상 20분 / 선행 0~39 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §3, §5, §9, §16(DESIGN_HASH_CHECK 후 `DesktopTop.dc.html`·`Mobile.dc.html` 읽기 전용); main.js `#heroStats` 렌더
- tracked 허용(exact): `index.html`(section#hero 내부만: 직계 자식 8개 순서·tagline·`#heroFeatured` 위치), `js/main.js`(정확히 `setText('heroTagline', PROFILE.tagline);` 1줄), `css/style.css`(hero 1열 간격·STATS·featured 반응형·`.hero-tagline` 비색 타이포만), `tests/specs/hero.spec.js`
- runtime: R0
- 금지: §15.7, `js/data.js`, 새 색·BASE 밖 font-weight·font-family 이동, 문구 축소·변경, 렌더 로직, 섹션·nav

## 작업 (TDD)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step40` → `python3 -I tests/scripts/design-intake-check.py`
2. `hero.spec.js`(6 project) 먼저 실패 확인: 상수 `STAT_ITEM`·`STAT_VALUE`·`STAT_LABEL`; `.hero-inner` 직계 자식 §5 순서; `#heroTagline` 텍스트 = `PROFILE.tagline`; CTA·eyebrow·typed·`#heroFeatured` role·aria-label 유지; STATS 375 2×2·768/1280 4×1, featured 1/2/3열; 첫 화면(desktop-dark/light) `expectInFirstScreen` = §5 assertion 전부, 대상 `#heroName`·`#heroTagline`·`#heroStats`·`.featured-title` 3개·지표 item 4개 × (item, VALUE, LABEL) 및 텍스트 일치.
3. 구현.

## AC

- `python3 -I tests/scripts/design-intake-check.py && sh tests/scripts/with-env.sh npm --prefix tests test -- hero.spec.js css-parse.spec.js color-vocab.spec.js design-guard-color-rules.spec.js design-guard-color.spec.js design-guard-css.spec.js design-guard.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step40.json --allow index.html,js/main.js,css/style.css,tests/specs/hero.spec.js` → exit 0
