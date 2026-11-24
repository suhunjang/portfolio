# Step 15 — color-rule-pairs

- 목적: 설계 §11.4 step 15 규칙 1~3(대응·featured/stripe 예외·`color-rule-reordered`).
- 18분 / 선행 0~14 / 공통 §9 / gate GATE
- 허용(exact): `tests/helpers/design-guard-color-pairs.js`, `tests/specs/design-guard-color-pairs.spec.js`(신규)
- runtime: R0
- 추가 금지: 사이트 파일, step 13·14 수정, 선언 판정(step 16)·token 판정(step 17), 결과 정렬

## 작업
1. `SNAP 15` → RED → 구현 → GREEN.
2. BASE `.a{color:red} .b{color:blue} .project-card{background:var(--card);padding:16px} @media (max-width: 768px){.nav-link{color:var(--accent)}} .strength-card::before{background:var(--accent)} .dup{color:var(--card)} .dup{color:var(--accent)} :root{--card:#fff}`(사례는 해당 부분만 변경):
   - `featuredCounterpart('#projectGrid .project-card:hover')` → `#projectGrid .featured-card:hover`, `.nav-link` → null; `.dup` 두 규칙 등장 순 짝, 하나 없으면 두 번째 null; `:root`는 색 Rule 아님
   - `[]`: 변경 없음; `.project-card, .featured-card`; stripe 삭제; `.a`·`.b` 사이 `.z{gap:1px}` 삽입; `.a{color:green}`; 비색 선언 추가·이동
   - 정확히: `.b`·`.a` 뒤바꿈 → `["color-rule-reordered:.a|.b"]`; `.project-card`를 `.a` 앞으로 → `["color-rule-reordered:.b|.project-card"]`; `.card{background:var(--card);padding:16px}` 교체 → `["color-rule-missing:|.project-card"]`; `.project-card, .hero-name` → `["selector-extended:.project-card, .hero-name"]`; `.nav-link`를 `@media (max-width: 900px)`로 → `["color-rule-missing:@media (max-width: 768px)|.nav-link"]`; 두 번째 `.dup` 삭제 → `["color-rule-missing:|.dup"]`; 뒤바꿈+`.card` 교체 → `["color-rule-missing:|.project-card", "color-rule-reordered:.a|.b"]`
   - 입력 불변

## AC
- `T design-guard-color-pairs.spec.js color-vocab.spec.js css-parse.spec.js && FULL && GATE 15 tests/helpers/design-guard-color-pairs.js,tests/specs/design-guard-color-pairs.spec.js tests/helpers/design-guard-color-pairs.js,tests/specs/design-guard-color-pairs.spec.js`
