# Step 13 — design-guard-css

- 목적: 설계 §16.4 step 13 CSS 판정(규칙 구조 비교)과 합성 단위 테스트. 실저장소 통합은 step 14.
- 예상 19분 / 선행 0~12 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §5(featured 색), §16.2~§16.4
- tracked 허용(exact): `tests/helpers/design-guard-css.js`(신규), `tests/specs/design-guard-css.spec.js`(신규)
- runtime: R0
- 금지: §15.7, 사이트 파일, Git·파일 시스템 접근(순수 함수만)

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step13`
2. `design-guard-css.js`: `COLOR_PROPS`, `COLOR_LITERAL_RE`, `parseCssRules(text)`, `featuredCounterpart(selector)`, `checkCss({ baseCss, currentCss, baseThemes, currentThemes })` — 설계 §16.4 규칙 1~4와 위반 문자열 형식 그대로.
3. `design-guard-css.spec.js`(node 전용, desktop-dark만, 합성 CSS 문자열만):
   - parser: 주석·문자열 안 괄호 무시, `@media` 중첩 chain, 쉼표 선택자 정규화
   - 허용: 변경 없음 `[]`; `.project-card { background: var(--card); }`에 `, .featured-card` 추가; `#projectGrid .project-card:hover` 규칙에 `#projectGrid .featured-card:hover` 추가; BASE `.strength-card::before { background: var(--accent); }` 삭제; 비색 선언(padding·gap·font-size·grid) 추가; `:focus-visible { outline: 2px solid var(--accent); }`(BASE 정의 토큰); 새 비색 custom property `--section-pad: 96px`와 그 사용; `font-weight: 600`
   - 거부: 대상 교체(`.project-card` 색 규칙을 `.card`로) → `color-rule-missing`; 임의 확장(`.project-card, .hero-name`) → `selector-extended`; 미디어 조건 변경(`@media (max-width: 768px)` 안 색 규칙을 `(max-width: 900px)`로 이동) → `color-rule-missing`; 색 값 변경(`var(--card)` → `var(--muted)`) → `color-decl-changed`; 새 규칙의 `color: var(--text)` → `color-decl-new`; `#0d0f12` 리터럴 → `color-decl-new`; `:focus-visible` outline에 리터럴 또는 미정의 토큰 → `color-decl-new`/`unknown-token`; `font-family` 추가·`@import`·`@font-face` → `font-asset`; `font-weight: 800` → `font-weight`; `url(` → `asset`; `content: '★'` → `content`; themes 문자열 변경 → `themes-changed`
   - 입력 불변

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- design-guard-css.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step13.json --allow tests/helpers/design-guard-css.js,tests/specs/design-guard-css.spec.js --require-absent tests/helpers/design-guard-css.js,tests/specs/design-guard-css.spec.js` → exit 0
