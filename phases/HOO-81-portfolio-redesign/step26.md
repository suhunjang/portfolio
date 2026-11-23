# Step 26 — hero-first-screen

- 목적: 히어로 순서·tagline·반응형과 첫 화면 AC(지표 item 4개 개별 검사 포함).
- 예상 20분 / 선행 0~25 / 공통 절차 설계 §15
- read-first: 설계 §3(렌더링), §5(히어로 순서, tagline, 첫 화면 AC), §9; main.js `#heroStats` 렌더 코드에서 지표 item·수치·label 셀렉터와 대응 STATS 필드명
- tracked 허용(exact): `index.html`(section#hero 내부만, `#heroFeatured` 마크업 유지), `js/main.js`(정확히 `setText('heroTagline', PROFILE.tagline);` 1줄 추가만), `css/style.css`(hero, `#heroStats`, `#heroFeatured` 배치만), `tests/specs/hero.spec.js`
- runtime: R0
- 금지: §15.7, `js/data.js`, `css/themes.css`, 대표 카드·모달·`#heroStats` 렌더 로직, `#heroFeatured` 속성, 섹션·nav

## 작업 (TDD)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step26`
2. `hero.spec.js`(6 project) 먼저 실패 확인
   - 상단 상수 `STAT_ITEM`, `STAT_VALUE`, `STAT_LABEL`
   - hero DOM 순서 §5 1~8; `p.hero-tagline` id `heroTagline`, 텍스트 = `PROFILE.tagline`; CTA·eyebrow·typed 유지; `#heroFeatured` role·aria-label 유지
   - 배치: STATS item 375 2×2, 768·1280 4×1; featured 1/2/3열
   - 첫 화면(desktop-dark/light, fonts.ready, scrollY 0): helper `expectInFirstScreen(locator)` = `toBeVisible()`, bbox w·h > 0, 자신과 `document.documentElement`까지 모든 조상 visibility `visible`·opacity `1`(`expect.poll`), left x ≥ 0, top y ≥ 0, right x+w ≤ 1280, bottom y+h ≤ 800
   - 적용: `#heroName`, `#heroTagline`, `#heroStats`, `.featured-title` 3개 각각
   - 지표: `#heroStats` 안 `STAT_ITEM` 개수 정확히 4. i = 0..3마다 item, item 안 `STAT_VALUE`(정확히 1개), `STAT_LABEL`(정확히 1개) 각각 `expectInFirstScreen`; VALUE 텍스트(norm) = `STATS[i]` 수치 필드, LABEL 텍스트(norm) = `STATS[i]` label 필드
3. index.html 순서 변경과 tagline 추가, main.js 1줄, style.css(eyebrow·typing 축소, 여백, STATS·featured 반응형, blurb 2줄 clamp, 토큰만, 문구 축소 금지).
4. axe 새 target은 step 25와 같은 규칙.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- hero.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step26.json --allow index.html,js/main.js,css/style.css,tests/specs/hero.spec.js` → exit 0
- hero.spec.js 단독 실행에 지표 item 4개 × (item, 수치, label)의 텍스트·가시성·크기·조상 visibility/opacity·viewport 네 경계 assertion이 포함되어 통과한다.
