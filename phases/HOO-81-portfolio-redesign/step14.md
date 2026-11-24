# Step 14 — design-guard-color

- 목적: 선택자·at-rule 규칙 대응과 색·color token 의존 보존 검사(설계 §16.4 step 14)와 합성 테스트.
- 예상 19분 / 선행 0~13 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §5(featured 색), §16.2~§16.4; `tests/helpers/css-parse.js`(import만)
- tracked 허용(exact): `tests/helpers/design-guard-color.js`(신규), `tests/specs/design-guard-color.spec.js`(신규)
- runtime: R0
- 금지: §15.7, 사이트 파일, `css-parse.js`·`css-parse.spec.js` 수정, Git·파일 시스템 접근

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step14`
2. `design-guard-color.js`: `NAMED_COLORS`, `COLOR_PROPS`, `isColorValue(value, colorTokens)`, `colorTokenSet(rules)`, `featuredCounterpart(selector)`, `checkColors({ baseRules, currentRules })` — 설계 §16.4 step 14 규칙 1~5와 위반 문자열 그대로.
3. `design-guard-color.spec.js`(node 전용, desktop-dark만, 합성 CSS 문자열을 `parseCssRules`로 변환)
   - 기본 BASE 합성: style `:root{--card:#fff;--accent:var(--brand);--pad:16px} .project-card{background:var(--card);padding:var(--pad)} @media (max-width: 768px){.nav-link{color:var(--accent)}} .strength-card::before{background:var(--accent)}`, themes `:root{--brand:#3355ff}`
   - `colorTokenSet`: `--card`, `--accent`, `--brand` 포함, `--pad` 제외(별칭 사슬 양방향)
   - 허용 → `[]`: 변경 없음; `.project-card, .featured-card` 확장; `.strength-card::before` 삭제; 비색 선언 추가(gap·font-size); 새 `--section-pad: 96px`; `:focus-visible{outline:2px solid var(--accent)}`
   - 거부(정확한 문자열): 선택자 교체 `.card{background:var(--card)}` → `color-rule-missing:|.project-card`; 확장 `.project-card, .hero-name` → `selector-extended:.project-card, .hero-name`; 미디어 조건 변경 `(max-width: 900px)` → `color-rule-missing:@media (max-width: 768px)|.nav-link`; 값 변경 `background:var(--pad)` → `color-decl-changed:.project-card`; 새 규칙 `.x{color:var(--card)}` → `color-decl-new:.x`; named color `.x{border-left:2px solid navy}` → `color-decl-new:.x`; `currentColor` 대체 `.project-card{background:currentColor}` → `color-decl-changed:.project-card`; 비색 선언에 `currentColor` 새로 등장 `.y{--ring:currentColor}` → `color-token-added:--ring`; token 값 변경 `--card:#fafafa` → `color-token-changed:--card`; token 삭제 → `color-token-removed:--card`; 별칭 재정의 `--accent:var(--card)` → `color-token-changed:--accent`; 다른 위치 재정의 `.btn{--accent:#000}` → `color-token-redefined:--accent`; 새 별칭 `--btn-bg: var(--brand)` → `color-token-added:--btn-bg`; 비색 token을 색으로 `--pad: red` → `color-token-added:--pad`; `:focus-visible` outline에 `#000`·`currentColor` → `color-decl-new:…:focus-visible`
   - 입력 불변

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- design-guard-color.spec.js css-parse.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step14.json --allow tests/helpers/design-guard-color.js,tests/specs/design-guard-color.spec.js --require-absent tests/helpers/design-guard-color.js,tests/specs/design-guard-color.spec.js` → exit 0
