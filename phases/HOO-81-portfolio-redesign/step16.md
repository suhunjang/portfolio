# Step 16 — color-decl-rules

- 목적: 짝지어진 색 Rule의 선언 보존(changed), 색 선언 순서 보존(`color-decl-reordered`), 새로 나타난 색 선언 거부(new), 짝 없는 현재 Rule 판정과 `checkColorRules`의 전체 진단 순서·중복 제거(설계 §16.4 step 16 규칙 4~8). custom property 정의는 검사하지 않는다(step 17 전담).
- 예상 18분 / 선행 0~15 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §16.3, §16.4(step 15, step 16 "BASE 색 선언 배열"·진단 순서·규칙 4~8·중복 제거); `tests/helpers/css-parse.js`, `tests/helpers/color-vocab.js`, `tests/helpers/design-guard-color-pairs.js`(import만)
- tracked 허용(exact): `tests/helpers/design-guard-color-rules.js`(신규), `tests/specs/design-guard-color-rules.spec.js`(신규)
- runtime: R0
- 금지: §15.7, 사이트 파일, step 13~15 helper·spec 수정(pair 판정 재구현 금지, import만), Git·파일 시스템 접근, custom property 정의 판정(step 17 몫), 결과 배열 정렬

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step16`
2. `design-guard-color-rules.js` API: `checkColorRules({ baseRules, currentRules, colorTokens })` — `checkColorRulePairs` 결과 뒤에 설계 §16.4 step 16 규칙 4~8의 선언 진단을 고정 순서(짝 있는 BASE 색 Rule을 BASE 순서로 4→5→6, 그다음 짝 없는 현재 Rule을 현재 순서로 7→8, Rule 안 선언 순)로 이어 붙이고 전체에서 같은 문자열은 처음 것만 남긴다. 규칙 5는 규칙 4가 성립하지 않은 짝에서만 판정한다. 규칙 6은 prop 제한 없이 BASE Rule에 없는 모든 비-custom property (prop, 정규화 value) 쌍을 검사한다.
3. `design-guard-color-rules.spec.js`(node 전용, desktop-dark만; 합성 BASE `:root{--card:#fff;--accent:#3355ff} .project-card{background:var(--card);padding:16px} @media (max-width: 768px){.nav-link{color:var(--accent)}} .strength-card::before{background:var(--accent)} .dup{color:var(--card)} .dup{color:var(--accent)} .btn{border-color:var(--accent)} .pair{color:var(--card);color:var(--accent)}`, colorTokens `--card`, `--accent`; 각 거부 사례는 BASE 텍스트에서 해당 부분만 바꾼 현재 텍스트)
   - 허용 → `[]`: 변경 없음; 변경 없는 `:root{--card:#fff;--accent:#3355ff}`; `:root`에 새 `--card2:#000` 추가(정의 판정은 step 17); `.project-card, .featured-card`; `.strength-card::before` 삭제; 짝지어진 `.project-card`에 비색 선언 `margin:4px`·`transition:transform .2s` 추가; 비색 선언 이동 `.project-card{padding:16px;background:var(--card)}`; `.pair{margin:0;color:var(--card);gap:4px;color:var(--accent)}`(비색 선언 삽입, 색 순서 유지); 새 비색 규칙 `.z{gap:24px}`; `:focus-visible{outline:2px solid var(--accent)}`
   - 거부(정확한 결과 배열, 순서 포함):
     - 같은 prop 두 색 선언 순서 뒤바꿈 `.pair{color:var(--accent);color:var(--card)}` → 정확히 `["color-decl-reordered:.pair"]`
     - `background:var(--accent)`로 값 교체 → `["color-decl-changed:.project-card", "color-decl-new:.project-card"]`(reordered 없음)
     - `background:currentColor`로 값 교체 → `["color-decl-changed:.project-card", "color-decl-new:.project-card"]`
     - 같은 prop 다른 값 후행 추가 `background`: `.project-card{background:var(--card);padding:16px;background:var(--accent)}` → 정확히 `["color-decl-new:.project-card"]`
     - 같은 prop 다른 값 후행 추가 `color`: `.nav-link{color:var(--accent);color:var(--card)}`(같은 미디어 안) → 정확히 `["color-decl-new:.nav-link"]`
     - 같은 prop 다른 값 후행 추가 `border-color`: `.btn{border-color:var(--accent);border-color:var(--card)}` → 정확히 `["color-decl-new:.btn"]`
     - 기존 `.project-card`에 `border-top-color:var(--accent)` 추가 → 정확히 `["color-decl-new:.project-card"]`
     - 기존 `.project-card`에 `outline-color:navy` 추가 → `["color-decl-new:.project-card"]`
     - 기존 `.project-card`에 `margin:currentColor` 추가 → `["color-decl-new:.project-card"]`
     - `.project-card` 규칙을 `.card{background:var(--card);padding:16px}`로 교체 → `["color-rule-missing:|.project-card", "color-decl-new:.card"]`(pair 진단 뒤에 선언 진단)
     - `.nav-link` 규칙을 `@media (max-width: 900px)`로 이동 → `["color-rule-missing:@media (max-width: 768px)|.nav-link", "color-decl-new:.nav-link"]`
     - `.btn`과 `.pair` 규칙 순서 뒤바꿈 → 정확히 `["color-rule-reordered:.btn|.pair"]`(pair 진단 포함 확인)
     - 일반 신규 색 선언 `.x{color:var(--card)}` → `["color-decl-new:.x"]`
     - 새 `.x{border-left:2px solid navy}` → `["color-decl-new:.x"]`
     - 새 `.x{border-bottom-color:var(--card)}` → `["color-decl-new:.x"]`
     - 새 비색 선언 `.y{margin:currentColor}`(규칙 7·8 같은 문자열, 중복 제거) → `["color-decl-new:.y"]`
     - `:focus-visible{outline:2px solid #000}` → `["color-decl-new:…:focus-visible"]`(현재 selectors 그대로)
     - 순서 결합: `.project-card` 규칙을 `.card{background:var(--card);padding:16px}`로 교체, 첫 번째 `.dup` 값을 `color:var(--accent)`로, `.pair` 두 색 선언 순서를 뒤바꾸고 끝에 `.x{color:var(--card)}` 추가 → `["color-rule-missing:|.project-card", "color-decl-changed:.dup", "color-decl-new:.dup", "color-decl-reordered:.pair", "color-decl-new:.card", "color-decl-new:.x"]`
   - 입력 불변

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- design-guard-color-rules.spec.js design-guard-color-pairs.spec.js color-vocab.spec.js css-parse.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step16.json --allow tests/helpers/design-guard-color-rules.js,tests/specs/design-guard-color-rules.spec.js --require-absent tests/helpers/design-guard-color-rules.js,tests/specs/design-guard-color-rules.spec.js` → exit 0
