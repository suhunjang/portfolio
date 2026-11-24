# Resume Step 6 — hero-first-screen (원 step 42)

- 목적: 원 §3 hero DOM 순서·tagline·첫 화면 AC(2열은 resume 7).
- 20분 / 선행 0~5 / 공통 원 §9 + §R1·§R2 no-op / gate `RGATE 6`
- 허용(exact): `index.html`(section#hero 내부: 직계 8개 순서·tagline·`#heroFeatured` 위치), `js/main.js`(정확히 `setText('heroTagline', PROFILE.tagline);` 1줄), `css/style.css`(hero 1열 간격·STATS·featured 반응형·`.hero-tagline` 비색 타이포만), `tests/specs/hero.spec.js`
- runtime: R0
- 추가 금지: `js/data.js`, 원 §11.3, 문구 변경, 렌더 로직, 섹션·nav

## 작업
1. `RSNAP 6` → `DI`(`DesktopTop.dc.html`·`Mobile.dc.html` 읽기만).
2. RED spec(6 project): 상수 `STAT_ITEM`·`STAT_VALUE`·`STAT_LABEL`; 직계 자식 원 §3 순서; `#heroTagline` = `PROFILE.tagline`; CTA·eyebrow·typed·`#heroFeatured` role·label 유지; STATS 375 2×2·768/1280 4×1, featured 1/2/3열; desktop-dark/light `expectInFirstScreen` = 원 §3 첫 화면 AC 전부.
3. 구현.

## AC
- `DI && T hero.spec.js GS && FULL && VS && RGATE 6 index.html,js/main.js,css/style.css,tests/specs/hero.spec.js`
