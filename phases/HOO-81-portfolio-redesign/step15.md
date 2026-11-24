# Step 15 — design-guard-color-rules

- 목적: 중복 규칙 대응, 선택자 확장 예외(featured 대응), 색 선언 보존(설계 §16.4 step 15)과 단위 테스트.
- 예상 17분 / 선행 0~14 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §5(featured 색), §16.4(step 13~15); `tests/helpers/css-parse.js`, `tests/helpers/color-vocab.js`(import만)
- tracked 허용(exact): `tests/helpers/design-guard-color-rules.js`(신규), `tests/specs/design-guard-color-rules.spec.js`(신규)
- runtime: R0
- 금지: §15.7, 사이트 파일, step 13·14 helper·spec 수정, Git·파일 시스템 접근

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step15`
2. `design-guard-color-rules.js` 추가 API: `featuredCounterpart(selector)`, `pairColorRules(baseRules, currentRules)`, `checkColorRules({ baseRules, currentRules, colorTokens })` — 설계 §16.4 step 15 규칙 1~5와 위반 문자열 그대로.
3. `design-guard-color-rules.spec.js`(node 전용, desktop-dark만; 합성 BASE `.project-card{background:var(--card);padding:16px} @media (max-width: 768px){.nav-link{color:var(--accent)}} .strength-card::before{background:var(--accent)} .dup{color:var(--card)} .dup{color:var(--accent)}`, colorTokens `--card`, `--accent`)
   - `featuredCounterpart('#projectGrid .project-card:hover')` → `#projectGrid .featured-card:hover`, `.nav-link` → null
   - `pairColorRules`: 중복 `.dup` 두 규칙이 현재의 두 `.dup`와 등장 순서대로 짝지어짐; 현재에서 하나가 없으면 두 번째가 null
   - 허용 → `[]`: 변경 없음; `.project-card, .featured-card`; `.strength-card::before` 삭제; 비색 선언 추가; `:focus-visible{outline:2px solid var(--accent)}`
   - 거부(정확한 문자열): `.card{background:var(--card)}`로 교체 → `color-rule-missing:|.project-card`; `.project-card, .hero-name` → `selector-extended:.project-card, .hero-name`; 미디어 `(max-width: 900px)`로 이동 → `color-rule-missing:@media (max-width: 768px)|.nav-link`; `background:var(--accent)`로 값 변경 → `color-decl-changed:.project-card`; `background:currentColor` → `color-decl-changed:.project-card`; 두 번째 `.dup` 삭제 → `color-rule-missing:|.dup`; 새 `.x{color:var(--card)}` → `color-decl-new:.x`; 새 `.x{border-left:2px solid navy}` → `color-decl-new:.x`; 새 비색 선언 `.y{margin:currentColor}`(BASE에 없음) → `color-decl-new:.y`; `:focus-visible{outline:2px solid #000}` → `color-decl-new:…:focus-visible`
   - 입력 불변

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- design-guard-color-rules.spec.js color-vocab.spec.js css-parse.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step15.json --allow tests/helpers/design-guard-color-rules.js,tests/specs/design-guard-color-rules.spec.js --require-absent tests/helpers/design-guard-color-rules.js,tests/specs/design-guard-color-rules.spec.js` → exit 0
