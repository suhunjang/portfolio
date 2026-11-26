# Resume Step 19 — hero-first-screen (원 step 42)

- 목적: 원 §3 hero DOM 순서·tagline·첫 화면 AC(2열은 resume 20).
- 20분 / 선행 0~18 / 공통 원 §9 + §R1·§R2 no-op·§R11 / gate `RGATE 19`
- 허용(exact): `index.html`(section#hero 내부: 직계 8개 순서·tagline·`#heroFeatured` 위치), `js/main.js`(정확히 `setText('heroTagline', PROFILE.tagline);` 1줄), `css/style.css`(hero 1열 간격·STATS·featured 반응형·`.hero-tagline` 비색 타이포만), `tests/specs/hero.spec.js`
- 필수 산출물(REQ): `tests/specs/hero.spec.js,index.html,js/main.js,css/style.css`
- runtime: R0
- 추가 금지: `js/data.js`, 원 §11.3, 문구 변경, 렌더 로직, 섹션·nav

## 작업
1. `RSNAP 19` → no-op 첫 probe `REQ 19 tests/specs/hero.spec.js,index.html,js/main.js,css/style.css`. PASS면 나머지 AC 실행 → 통과 시 `resume step19: no-op`. REQ FAIL 또는 AC 실패면 아래 작업 후 완전한 AC 재실행.
2. `DI`(`DesktopTop.dc.html`·`Mobile.dc.html` 읽기만). RED spec(6 project): 상수 `STAT_ITEM`·`STAT_VALUE`·`STAT_LABEL`; 직계 자식 원 §3 순서; `#heroTagline` = `PROFILE.tagline`; CTA·eyebrow·typed·`#heroFeatured` role·label 유지; STATS 375 2×2·768/1280 4×1, featured 1/2/3열; desktop-dark/light `expectInFirstScreen` = 원 §3 첫 화면 AC 전부.
3. 구현.

## AC
- `REQ 19 tests/specs/hero.spec.js,index.html,js/main.js,css/style.css && DI && T hero.spec.js GS && FULL && VS && RGATE 19 index.html,js/main.js,css/style.css,tests/specs/hero.spec.js`(첫 명령 stdout `required-artifacts step119: OK 4`)
