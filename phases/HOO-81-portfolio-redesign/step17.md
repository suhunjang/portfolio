# Step 17 — design-guard-color-tokens

- 목적: 설계 §11.4 step 17 — 같은 위치 키 중복 정의 거부(먼저), 정확히 하나일 때만 보존 검사, `checkColors`.
- 19분(작성 11, 단독 1, 누적 color 2, FULL 4, gate 1) / 선행 0~16 / 공통 §9 / gate GATE
- 허용(exact): `tests/helpers/design-guard-color.js`, `tests/specs/design-guard-color.spec.js`(신규)
- runtime: R0
- 추가 금지: 사이트 파일, step 13~16 수정, 중복 키 값·위치 비교, 결과 정렬, 오류 문자열 형식 변경

## 작업
1. `SNAP 17` → RED → 구현 → GREEN.
2. style `parseCssRules(t, 'css/style.css')` + themes `parseCssRules(t, 'css/themes.css')`. BASE style `:root{--card:#fff;--accent:var(--brand);--pad:16px} .project-card{background:var(--card);padding:var(--pad)} @media (max-width: 768px){.nav-link{color:var(--accent)}} .strength-card::before{background:var(--accent)}`, themes `:root{--brand:#3355ff}`.
   - 보존: 변경 없음 `[]`; `--card:#fafafa` → `color-token-changed:--card`; 삭제 → `color-token-removed:--card`; `--accent:var(--card)` → `color-token-changed:--accent`; `.btn{--accent:#000}` → `color-token-redefined:--accent`; `--btn-bg: var(--brand)` → `color-token-added:--btn-bg`; `--ring: currentColor` → `color-token-added:--ring`; `--card2:#000` → `color-token-added:--card2`; `--pad: red` → `color-token-added:--pad`; `--section-pad: 96px` 허용
   - 중복(정확히): (a) `:root{--card:#fff;--card:#fff;--accent:var(--brand);--pad:16px}` → `["색 토큰 중복 정의: --card @ css/style.css - :root (count=2)"]`; (b) 같은 Rule `--card:#fff;--card:#fafafa` → 같은 배열(changed 없음); (c) 기존 뒤 `:root{--card:#fff}` → 같은 배열; (d) 기존 뒤 `:root{--card:#fafafa}` → 같은 배열; (e) 같은 Rule 2회 + 별도 1회 → `["색 토큰 중복 정의: --card @ css/style.css - :root (count=3)"]`; (f) `@media (min-width: 1024px){:root{--card:#fff;--card:#fff}}` 추가 → `["색 토큰 중복 정의: --card @ css/style.css @media (min-width: 1024px) :root (count=2)"]`(redefined 없음); (g) themes `:root{--brand:#3355ff;--brand:#3355ff}` → `["색 토큰 중복 정의: --brand @ css/themes.css - :root (count=2)"]`; (h) `--pad:16px;--pad:16px` → `[]`; (i) (a)에서 `--pad:red` → `["색 토큰 중복 정의: --card @ css/style.css - :root (count=2)", "color-token-added:--pad"]`
   - `checkColors` `[]`: 변경 없음, featured 대응, stripe 삭제, 비색·`--section-pad`, `:focus-visible` outline(BASE token). 거부: `selector-extended` + `--card:#fafafa` 동시 → 둘 다 포함(규칙 위반 먼저); `.x{color:var(--card)}` → `color-decl-new:.x`만; `border-top-color:var(--accent)` 추가 → `["color-decl-new:.project-card"]`; `background:var(--accent)` 후행 → `["color-decl-new:.project-card"]`; `.project-card`·`.nav-link` 미디어 규칙 뒤바꿈 → `["color-rule-reordered:.project-card|.nav-link"]`; 중복 (c) → `["색 토큰 중복 정의: --card @ css/style.css - :root (count=2)"]`
   - 입력 불변

## AC
- `T design-guard-color.spec.js design-guard-color-rules.spec.js design-guard-color-pairs.spec.js color-vocab.spec.js css-parse.spec.js && FULL && GATE 17 tests/helpers/design-guard-color.js,tests/specs/design-guard-color.spec.js tests/helpers/design-guard-color.js,tests/specs/design-guard-color.spec.js`
