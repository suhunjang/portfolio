# Step 35 — hero-first-screen

- 목적: 히어로 DOM 순서·tagline과 첫 화면 AC(지표 item 4개 개별 검사). 2열 배치는 step 36.
- 예상 20분 / 선행 0~34 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §3(hero 마크업), §5, §9, §16(DESIGN_HASH_CHECK 후 `DesktopTop.dc.html`·`Mobile.dc.html` 읽기 전용 참고); main.js `#heroStats` 렌더 코드
- tracked 허용(exact): `index.html`(section#hero 내부만: `.hero-inner` 직계 자식 8개 순서, tagline 추가, `#heroFeatured`를 `.hero-inner` 직계 자식으로 유지), `js/main.js`(정확히 `setText('heroTagline', PROFILE.tagline);` 1줄만), `css/style.css`(hero 1열 기준 간격·STATS·featured 반응형·`.hero-tagline` 타이포만), `tests/specs/hero.spec.js`
- runtime: R0
- 금지: §15.7, `js/data.js`, `css/themes.css`, 새 색·서체 weight 밖 값, 문구 축소·변경, 대표 카드·모달·`#heroStats` 렌더 로직, 섹션·nav

## 작업 (TDD)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step35` → `python3 -I tests/scripts/design-intake-check.py`
2. `hero.spec.js`(6 project) 먼저 실패 확인
   - 상단 상수 `STAT_ITEM`, `STAT_VALUE`, `STAT_LABEL`
   - `.hero-inner` 직계 자식이 정확히 §5 1~8 순서; `#heroTagline` 텍스트 = `PROFILE.tagline`; CTA·eyebrow·typed 유지; `#heroFeatured` role·aria-label 유지
   - 배치: STATS 375 2×2, 768·1280 4×1; featured 1/2/3열
   - 첫 화면(desktop-dark/light): `expectInFirstScreen(locator)` = 설계 §5 assertion 전부, 대상 `#heroName`, `#heroTagline`, `#heroStats`, `.featured-title` 3개, 지표 item 4개 × (item, VALUE, LABEL)와 텍스트 일치
3. index.html·main.js 1줄·style.css(문구 축소 금지, 색 선언 없음).
4. axe 새 target은 step 34 규칙.

## AC

- `python3 -I tests/scripts/design-intake-check.py && sh tests/scripts/with-env.sh npm --prefix tests test -- hero.spec.js design-guard.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step35.json --allow index.html,js/main.js,css/style.css,tests/specs/hero.spec.js` → exit 0
