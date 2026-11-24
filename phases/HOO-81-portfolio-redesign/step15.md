# Step 15 — design-guard-color-rules

- 목적: 중복 규칙 대응, 선택자 확장 예외(featured 대응), 기존 색 선언 보존과 짝지어진 규칙의 새 색 선언 거부(설계 §16.4 step 15 규칙 1~6)와 단위 테스트. custom property(`--x`) 정의는 이 step에서 검사하지 않는다(step 16 전담).
- 예상 18분 / 선행 0~14 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §5(featured 색), §16.3, §16.4(step 13~16, 특히 step 15 머리말의 custom property 제외와 규칙 3·4 구분); `tests/helpers/css-parse.js`, `tests/helpers/color-vocab.js`(import만)
- tracked 허용(exact): `tests/helpers/design-guard-color-rules.js`(신규), `tests/specs/design-guard-color-rules.spec.js`(신규)
- runtime: R0
- 금지: §15.7, 사이트 파일, step 13·14 helper·spec 수정, Git·파일 시스템 접근, custom property 정의 판정(step 16 몫)

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step15`
2. `design-guard-color-rules.js` 추가 API: `featuredCounterpart(selector)`, `pairColorRules(baseRules, currentRules)`, `checkColorRules({ baseRules, currentRules, colorTokens })` — 설계 §16.4 step 15 규칙 1~6과 위반 문자열 그대로(모든 규칙에서 `--x` 선언 제외, 결과는 발견 순서·같은 문자열 한 번).
3. `design-guard-color-rules.spec.js`(node 전용, desktop-dark만; 합성 BASE `:root{--card:#fff;--accent:#3355ff} .project-card{background:var(--card);padding:16px} @media (max-width: 768px){.nav-link{color:var(--accent)}} .strength-card::before{background:var(--accent)} .dup{color:var(--card)} .dup{color:var(--accent)}`, colorTokens `--card`, `--accent`)
   - `featuredCounterpart('#projectGrid .project-card:hover')` → `#projectGrid .featured-card:hover`, `.nav-link` → null
   - `pairColorRules`: 중복 `.dup` 두 규칙이 현재의 두 `.dup`와 등장 순서대로 짝지어짐; 현재에서 하나가 없으면 두 번째가 null; `:root` 규칙은 색 Rule로 취급하지 않음(custom property만 있음)
   - 허용 → `[]`: 변경 없음; 변경 없는 `:root{--card:#fff;--accent:#3355ff}`(색 custom property 정의는 오류 없음); `:root`에 새 `--card2:#000` 추가(이 step은 정의를 보지 않으므로 `[]`, 판정은 step 16); `.project-card, .featured-card`; `.strength-card::before` 삭제; 짝지어진 `.project-card`에 비색 선언 `margin:4px`·`transition:transform .2s` 추가; 새 비색 규칙 `.z{gap:24px}`; `:focus-visible{outline:2px solid var(--accent)}`
   - 거부(정확한 결과 배열):
     - `.card{background:var(--card)}`로 교체 → `["color-rule-missing:|.project-card"]`
     - `.project-card, .hero-name` → `["selector-extended:.project-card, .hero-name"]`
     - 미디어 `(max-width: 900px)`로 이동 → `["color-rule-missing:@media (max-width: 768px)|.nav-link"]`
     - `background:var(--accent)`로 값 변경 → `["color-decl-changed:.project-card"]`
     - `background:currentColor` → `["color-decl-changed:.project-card"]`
     - 기존 `.project-card`에 `border-top-color:var(--accent)` 추가(나머지 그대로) → 정확히 `["color-decl-new:.project-card"]`
     - 기존 `.project-card`에 `outline-color:navy` 추가 → `["color-decl-new:.project-card"]`
     - 기존 `.project-card`에 `padding:16px;margin:currentColor` → `["color-decl-new:.project-card"]`
     - 두 번째 `.dup` 삭제 → `["color-rule-missing:|.dup"]`
     - 일반 신규 색 선언 `.x{color:var(--card)}` → 정확히 `["color-decl-new:.x"]`
     - 새 `.x{border-left:2px solid navy}` → `["color-decl-new:.x"]`
     - 새 `.x{border-bottom-color:var(--card)}` → `["color-decl-new:.x"]`
     - 새 비색 선언 `.y{margin:currentColor}`(BASE에 없음) → `["color-decl-new:.y"]`
     - `:focus-visible{outline:2px solid #000}` → `["color-decl-new:…:focus-visible"]`(현재 selectors 그대로)
   - 입력 불변

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- design-guard-color-rules.spec.js color-vocab.spec.js css-parse.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step15.json --allow tests/helpers/design-guard-color-rules.js,tests/specs/design-guard-color-rules.spec.js --require-absent tests/helpers/design-guard-color-rules.js,tests/specs/design-guard-color-rules.spec.js` → exit 0
