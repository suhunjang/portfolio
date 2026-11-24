# Step 15 — design-guard-color-rules

- 목적: 중복 규칙 대응, 선택자 확장 예외(featured 대응), 기존 색 선언 보존, 짝지어진 규칙에 새로 나타난 모든 색 선언 쌍 거부(같은 prop의 다른 값 포함), 고정 진단 순서(설계 §16.4 step 15 규칙 1~6)와 단위 테스트. custom property(`--x`) 정의는 이 step에서 검사하지 않는다(step 16 전담).
- 예상 19분 / 선행 0~14 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §5(featured 색), §16.3, §16.4(step 13~16, 특히 step 15 진단 순서·규칙 3·4·중복 제거); `tests/helpers/css-parse.js`, `tests/helpers/color-vocab.js`(import만)
- tracked 허용(exact): `tests/helpers/design-guard-color-rules.js`(신규), `tests/specs/design-guard-color-rules.spec.js`(신규)
- runtime: R0
- 금지: §15.7, 사이트 파일, step 13·14 helper·spec 수정, Git·파일 시스템 접근, custom property 정의 판정(step 16 몫), 결과 배열 정렬

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step15`
2. `design-guard-color-rules.js` 추가 API: `featuredCounterpart(selector)`, `pairColorRules(baseRules, currentRules)`, `checkColorRules({ baseRules, currentRules, colorTokens })` — 설계 §16.4 step 15 규칙 1~6, 위반 문자열, 진단 순서(BASE 색 Rule을 BASE 순서로 규칙 1→2→3→4, 그다음 짝 없는 현재 Rule을 현재 순서로 규칙 5→6, Rule 안 선언 순, 같은 문자열은 처음 것만) 그대로. 규칙 4는 prop 제한 없이 BASE Rule에 없는 모든 비-custom property (prop, 정규화 value) 쌍을 검사한다.
3. `design-guard-color-rules.spec.js`(node 전용, desktop-dark만; 합성 BASE `:root{--card:#fff;--accent:#3355ff} .project-card{background:var(--card);padding:16px} @media (max-width: 768px){.nav-link{color:var(--accent)}} .strength-card::before{background:var(--accent)} .dup{color:var(--card)} .dup{color:var(--accent)} .btn{border-color:var(--accent)}`, colorTokens `--card`, `--accent`; 각 거부 사례는 BASE 텍스트에서 해당 부분만 바꾼 현재 텍스트)
   - `featuredCounterpart('#projectGrid .project-card:hover')` → `#projectGrid .featured-card:hover`, `.nav-link` → null
   - `pairColorRules`: 중복 `.dup` 두 규칙이 현재의 두 `.dup`와 등장 순서대로 짝지어짐; 현재에서 하나가 없으면 두 번째가 null; `:root` 규칙은 색 Rule로 취급하지 않음(custom property만 있음)
   - 허용 → `[]`: 변경 없음; 변경 없는 `:root{--card:#fff;--accent:#3355ff}`(색 custom property 정의는 오류 없음); `:root`에 새 `--card2:#000` 추가(이 step은 정의를 보지 않으므로 `[]`, 판정은 step 16); `.project-card, .featured-card`; `.strength-card::before` 삭제; 짝지어진 `.project-card`에 비색 선언 `margin:4px`·`transition:transform .2s` 추가; 새 비색 규칙 `.z{gap:24px}`; `:focus-visible{outline:2px solid var(--accent)}`
   - 거부(정확한 결과 배열, 순서 포함):
     - `.project-card` 규칙을 `.card{background:var(--card);padding:16px}`로 교체 → `["color-rule-missing:|.project-card", "color-decl-new:.card"]`
     - `.project-card, .hero-name` → `["selector-extended:.project-card, .hero-name"]`
     - `.nav-link` 규칙을 `@media (max-width: 900px)`로 이동 → `["color-rule-missing:@media (max-width: 768px)|.nav-link", "color-decl-new:.nav-link"]`
     - `background:var(--accent)`로 값 교체 → `["color-decl-changed:.project-card", "color-decl-new:.project-card"]`
     - `background:currentColor`로 값 교체 → `["color-decl-changed:.project-card", "color-decl-new:.project-card"]`
     - 같은 prop 다른 값 후행 추가 `background`: `.project-card{background:var(--card);padding:16px;background:var(--accent)}` → 정확히 `["color-decl-new:.project-card"]`
     - 같은 prop 다른 값 후행 추가 `color`: `.nav-link{color:var(--accent);color:var(--card)}`(같은 미디어 안) → 정확히 `["color-decl-new:.nav-link"]`
     - 같은 prop 다른 값 후행 추가 `border-color`: `.btn{border-color:var(--accent);border-color:var(--card)}` → 정확히 `["color-decl-new:.btn"]`
     - 기존 `.project-card`에 `border-top-color:var(--accent)` 추가 → 정확히 `["color-decl-new:.project-card"]`
     - 기존 `.project-card`에 `outline-color:navy` 추가 → `["color-decl-new:.project-card"]`
     - 기존 `.project-card`에 `margin:currentColor` 추가 → `["color-decl-new:.project-card"]`
     - 두 번째 `.dup` 삭제 → `["color-rule-missing:|.dup"]`
     - 일반 신규 색 선언 `.x{color:var(--card)}` → `["color-decl-new:.x"]`
     - 새 `.x{border-left:2px solid navy}` → `["color-decl-new:.x"]`
     - 새 `.x{border-bottom-color:var(--card)}` → `["color-decl-new:.x"]`
     - 새 비색 선언 `.y{margin:currentColor}`(규칙 5·6 같은 문자열, 중복 제거) → `["color-decl-new:.y"]`
     - `:focus-visible{outline:2px solid #000}` → `["color-decl-new:…:focus-visible"]`(현재 selectors 그대로)
     - 순서 결합: `.project-card` 규칙을 `.card{background:var(--card);padding:16px}`로 교체하고 첫 번째 `.dup` 값을 `color:var(--accent)`로 바꾸며 끝에 `.x{color:var(--card)}` 추가 → `["color-rule-missing:|.project-card", "color-decl-changed:.dup", "color-decl-new:.dup", "color-decl-new:.card", "color-decl-new:.x"]`
   - 입력 불변

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- design-guard-color-rules.spec.js color-vocab.spec.js css-parse.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step15.json --allow tests/helpers/design-guard-color-rules.js,tests/specs/design-guard-color-rules.spec.js --require-absent tests/helpers/design-guard-color-rules.js,tests/specs/design-guard-color-rules.spec.js` → exit 0
