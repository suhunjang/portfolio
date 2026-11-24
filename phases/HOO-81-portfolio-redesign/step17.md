# Step 17 — design-guard-color-tokens

- 목적: color token 정의 보존·허용 예외(custom property 정의 검사 전담)와 `checkColors` 통합(설계 §16.4 step 17), 합성 통합 테스트.
- 예상 17분 / 선행 0~16 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §16.3, §16.4(step 13~17); `tests/helpers/css-parse.js`, `tests/helpers/color-vocab.js`, `tests/helpers/design-guard-color-pairs.js`, `tests/helpers/design-guard-color-rules.js`(import만)
- tracked 허용(exact): `tests/helpers/design-guard-color.js`(신규), `tests/specs/design-guard-color.spec.js`(신규)
- runtime: R0
- 금지: §15.7, 사이트 파일, step 13~16 helper·spec 수정, Git·파일 시스템 접근

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step17`
2. `design-guard-color.js` 추가 API: `checkColorTokens({ baseRules, currentRules, colorTokens })`, `checkColors({ baseRules, currentRules })` — 설계 §16.4 step 17 그대로.
3. `design-guard-color.spec.js`(node 전용, desktop-dark만; 합성 BASE style `:root{--card:#fff;--accent:var(--brand);--pad:16px} .project-card{background:var(--card);padding:var(--pad)} @media (max-width: 768px){.nav-link{color:var(--accent)}} .strength-card::before{background:var(--accent)}`, themes `:root{--brand:#3355ff}`)
   - `checkColorTokens` 단위: 변경 없음 `[]`; token 값 변경 `--card:#fafafa` → `color-token-changed:--card`; 삭제 → `color-token-removed:--card`; 별칭 재정의 `--accent:var(--card)` → `color-token-changed:--accent`; 다른 위치 재정의 `.btn{--accent:#000}` → `color-token-redefined:--accent`; 새 별칭 `--btn-bg: var(--brand)` → `color-token-added:--btn-bg`; 새 `--ring: currentColor` → `color-token-added:--ring`; 새 `--card2:#000` → `color-token-added:--card2`; 비색 token을 색으로 `--pad: red` → `color-token-added:--pad`; 새 비색 `--section-pad: 96px` 허용
   - `checkColors` 통합 허용 → `[]`: 변경 없음; featured 대응 추가; stripe 삭제; 비색 선언·`--section-pad`; `:focus-visible` outline(BASE token)
   - `checkColors` 통합 거부: step 15 위반 1건(`.project-card, .hero-name` → `selector-extended:…`)과 token 위반 1건(`--card:#fafafa`)을 동시에 넣으면 두 문자열이 모두 결과에 있음(규칙 위반이 먼저); `.x{color:var(--card)}` 신규 → 결과에 `color-decl-new:.x`만(token 위반 없음); 기존 `.project-card`에 `border-top-color:var(--accent)` 추가 → 결과 정확히 `["color-decl-new:.project-card"]`; `.project-card`에 `background:var(--accent)` 후행 추가 → 결과 정확히 `["color-decl-new:.project-card"]`; `.project-card`와 `.nav-link` 미디어 규칙 순서 뒤바꿈 → 결과 정확히 `["color-rule-reordered:.project-card|.nav-link"]`
   - 입력 불변

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- design-guard-color.spec.js design-guard-color-rules.spec.js design-guard-color-pairs.spec.js color-vocab.spec.js css-parse.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step17.json --allow tests/helpers/design-guard-color.js,tests/specs/design-guard-color.spec.js --require-absent tests/helpers/design-guard-color.js,tests/specs/design-guard-color.spec.js` → exit 0
