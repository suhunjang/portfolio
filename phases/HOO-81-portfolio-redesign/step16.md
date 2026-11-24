# Step 16 — color-decl-rules

- 목적: 설계 §11.4 step 16 규칙 4~8과 `checkColorRules` 진단 순서·중복 제거.
- 18분 / 선행 0~15 / 공통 §9 / gate GATE
- 허용(exact): `tests/helpers/design-guard-color-rules.js`, `tests/specs/design-guard-color-rules.spec.js`(신규)
- runtime: R0
- 추가 금지: 사이트 파일, step 13~15 수정(pairs는 import만), token 판정, 결과 정렬

## 작업
1. `SNAP 16` → RED → 구현 → GREEN.
2. BASE `:root{--card:#fff;--accent:#3355ff} .project-card{background:var(--card);padding:16px} @media (max-width: 768px){.nav-link{color:var(--accent)}} .strength-card::before{background:var(--accent)} .dup{color:var(--card)} .dup{color:var(--accent)} .btn{border-color:var(--accent)} .pair{color:var(--card);color:var(--accent)}`, colorTokens `--card`·`--accent`:
   - `[]`: 변경 없음; 같은 `:root`; `:root`에 `--card2:#000`; `.project-card, .featured-card`; stripe 삭제; `.project-card`에 `margin:4px`·`transition:transform .2s`; `.project-card{padding:16px;background:var(--card)}`; `.pair{margin:0;color:var(--card);gap:4px;color:var(--accent)}`; `.z{gap:24px}`; `:focus-visible{outline:2px solid var(--accent)}`
   - 정확히: `.pair{color:var(--accent);color:var(--card)}` → `["color-decl-reordered:.pair"]`; `background:var(--accent)` 교체 → `["color-decl-changed:.project-card", "color-decl-new:.project-card"]`; `background:currentColor` 교체 → 같음; `.project-card{background:var(--card);padding:16px;background:var(--accent)}` → `["color-decl-new:.project-card"]`; `.nav-link{color:var(--accent);color:var(--card)}` → `["color-decl-new:.nav-link"]`; `.btn{border-color:var(--accent);border-color:var(--card)}` → `["color-decl-new:.btn"]`; `.project-card`에 `border-top-color:var(--accent)` → `["color-decl-new:.project-card"]`; `outline-color:navy` → 같음; `margin:currentColor` → 같음; `.card{background:var(--card);padding:16px}` 교체 → `["color-rule-missing:|.project-card", "color-decl-new:.card"]`; `.nav-link` 900px 이동 → `["color-rule-missing:@media (max-width: 768px)|.nav-link", "color-decl-new:.nav-link"]`; `.btn`·`.pair` 뒤바꿈 → `["color-rule-reordered:.btn|.pair"]`; `.x{color:var(--card)}` → `["color-decl-new:.x"]`; `.x{border-left:2px solid navy}` → `["color-decl-new:.x"]`; `.x{border-bottom-color:var(--card)}` → `["color-decl-new:.x"]`; `.y{margin:currentColor}` → `["color-decl-new:.y"]`; `:focus-visible{outline:2px solid #000}` → `["color-decl-new:…:focus-visible"]`(현재 selectors); 결합(`.card` 교체 + 첫 `.dup`을 `color:var(--accent)` + `.pair` 뒤바꿈 + 끝 `.x{color:var(--card)}`) → `["color-rule-missing:|.project-card", "color-decl-changed:.dup", "color-decl-new:.dup", "color-decl-reordered:.pair", "color-decl-new:.card", "color-decl-new:.x"]`
   - 입력 불변

## AC
- `T design-guard-color-rules.spec.js design-guard-color-pairs.spec.js color-vocab.spec.js css-parse.spec.js && FULL && GATE 16 tests/helpers/design-guard-color-rules.js,tests/specs/design-guard-color-rules.spec.js tests/helpers/design-guard-color-rules.js,tests/specs/design-guard-color-rules.spec.js`
