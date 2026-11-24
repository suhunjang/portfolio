# Step 15 — color-rule-pairs

- 목적: BASE 색 Rule 대응(`pairColorRules`), featured 대응·stripe 예외, BASE 색 Rule 상대 순서 보존(`color-rule-reordered`)을 전담하는 helper와 단위 테스트(설계 §16.4 step 15 규칙 1~3). 선언 내용 비교와 custom property 정의는 다루지 않는다(step 16·17 몫).
- 예상 18분 / 선행 0~14 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §5(featured 색), §16.3, §16.4(step 13 `index`, step 14, step 15); `tests/helpers/css-parse.js`, `tests/helpers/color-vocab.js`(import만)
- tracked 허용(exact): `tests/helpers/design-guard-color-pairs.js`(신규), `tests/specs/design-guard-color-pairs.spec.js`(신규)
- runtime: R0
- 금지: §15.7, 사이트 파일, step 13·14 helper·spec 수정, Git·파일 시스템 접근, 선언 changed·reordered·new 판정(step 16 몫), custom property 정의 판정(step 17 몫), 결과 배열 정렬

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step15`
2. `design-guard-color-pairs.js` API: `featuredCounterpart(selector)`, `pairColorRules(baseRules, currentRules)`, `checkColorRulePairs({ baseRules, currentRules })` — 설계 §16.4 step 15 규칙 1~3, 위반 문자열, 진단 순서(BASE 색 Rule을 BASE 순서로 규칙 1→2, 그다음 file별 규칙 3, 같은 문자열은 처음 것만) 그대로.
3. `design-guard-color-pairs.spec.js`(node 전용, desktop-dark만; 합성 BASE `.a{color:red} .b{color:blue} .project-card{background:var(--card);padding:16px} @media (max-width: 768px){.nav-link{color:var(--accent)}} .strength-card::before{background:var(--accent)} .dup{color:var(--card)} .dup{color:var(--accent)} :root{--card:#fff}`; 각 사례는 BASE 텍스트에서 해당 부분만 바꾼 현재 텍스트)
   - `featuredCounterpart('#projectGrid .project-card:hover')` → `#projectGrid .featured-card:hover`, `.nav-link` → null
   - `pairColorRules`: 중복 `.dup` 두 규칙이 현재의 두 `.dup`와 등장 순서대로 짝지어짐; 현재에서 하나가 없으면 두 번째가 null; `:root` 규칙은 색 Rule로 취급하지 않음(custom property만 있음)
   - 허용 → `[]`: 변경 없음; `.project-card, .featured-card`(featured 확장); `.strength-card::before` 삭제; `.a`와 `.b` 사이에 새 규칙 `.z{gap:1px}` 삽입; 색 선언 값만 바꾼 `.a{color:green}`(선언 판정은 step 16이므로 이 함수는 `[]`); 비색 선언 추가·이동
   - 거부(정확한 결과 배열, 순서 포함):
     - 같은 specificity 두 규칙 순서 뒤바꿈 `.b{color:blue} .a{color:red} …` → 정확히 `["color-rule-reordered:.a|.b"]`
     - `.project-card` 규칙을 `.a` 앞으로 이동 → 정확히 `["color-rule-reordered:.b|.project-card"]`
     - `.project-card` 규칙을 `.card{background:var(--card);padding:16px}`로 교체 → `["color-rule-missing:|.project-card"]`
     - `.project-card, .hero-name` → `["selector-extended:.project-card, .hero-name"]`
     - `.nav-link` 규칙을 `@media (max-width: 900px)`로 이동 → `["color-rule-missing:@media (max-width: 768px)|.nav-link"]`
     - 두 번째 `.dup` 삭제 → `["color-rule-missing:|.dup"]`
     - 순서 결합: `.a`·`.b` 뒤바꿈과 `.project-card` → `.card` 교체를 함께 → `["color-rule-missing:|.project-card", "color-rule-reordered:.a|.b"]`
   - 입력 불변

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- design-guard-color-pairs.spec.js color-vocab.spec.js css-parse.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step15.json --allow tests/helpers/design-guard-color-pairs.js,tests/specs/design-guard-color-pairs.spec.js --require-absent tests/helpers/design-guard-color-pairs.js,tests/specs/design-guard-color-pairs.spec.js` → exit 0
