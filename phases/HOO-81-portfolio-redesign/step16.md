# Step 16 — design-guard-color-tokens

- 목적: color token 정의 보존·허용 예외와 `checkColors` 통합(설계 §16.4 step 16), 합성 통합 테스트.
- 예상 17분 / 선행 0~15 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §16.3, §16.4(step 13~16); `tests/helpers/css-parse.js`, `tests/helpers/color-vocab.js`, `tests/helpers/design-guard-color-rules.js`(import만)
- tracked 허용(exact): `tests/helpers/design-guard-color.js`(신규), `tests/specs/design-guard-color.spec.js`(신규)
- runtime: R0
- 금지: §15.7, 사이트 파일, step 13~15 helper·spec 수정, Git·파일 시스템 접근

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step16`
2. `design-guard-color.js` 추가 API: `checkColorTokens({ baseRules, currentRules, colorTokens })`, `checkColors({ baseRules, currentRules })` — 설계 §16.4 step 16 그대로.
3. `design-guard-color.spec.js`(node 전용, desktop-dark만; 합성 BASE style `:root{--card:#fff;--accent:var(--brand);--pad:16px} .project-card{background:var(--card);padding:var(--pad)} @media (max-width: 768px){.nav-link{color:var(--accent)}} .strength-card::before{background:var(--accent)}`, themes `:root{--brand:#3355ff}`)
   - `checkColorTokens` 단위: token 값 변경 `--card:#fafafa` → `color-token-changed:--card`; 삭제 → `color-token-removed:--card`; 별칭 재정의 `--accent:var(--card)` → `color-token-changed:--accent`; 다른 위치 재정의 `.btn{--accent:#000}` → `color-token-redefined:--accent`; 새 별칭 `--btn-bg: var(--brand)` → `color-token-added:--btn-bg`; 새 `--ring: currentColor` → `color-token-added:--ring`; 비색 token을 색으로 `--pad: red` → `color-token-added:--pad`; 새 비색 `--section-pad: 96px` 허용
   - `checkColors` 통합 허용 → `[]`: 변경 없음; featured 대응 추가; stripe 삭제; 비색 선언·`--section-pad`; `:focus-visible` outline(BASE token)
   - `checkColors` 통합 거부: step 15 규칙 위반 1건(`.project-card, .hero-name` → `selector-extended:…`)과 token 위반 1건(`--card:#fafafa`)을 동시에 넣으면 두 문자열이 모두 결과에 있음(규칙 위반이 먼저)
   - 입력 불변

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- design-guard-color.spec.js design-guard-color-rules.spec.js color-vocab.spec.js css-parse.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step16.json --allow tests/helpers/design-guard-color.js,tests/specs/design-guard-color.spec.js --require-absent tests/helpers/design-guard-color.js,tests/specs/design-guard-color.spec.js` → exit 0
