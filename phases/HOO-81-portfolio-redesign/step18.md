# Step 18 — font-preservation

- 목적: 설계 §11.4 step 18 `matchesBaseRule`·`checkFontDecls`(at-rule은 step 19).
- 18분(작성 10, 단독 1, 누적 GUARD 2, FULL 4, gate 1) / 선행 0~17 / 공통 §9 / gate GATE
- 허용(exact): `tests/helpers/design-guard-font.js`, `tests/specs/design-guard-font.spec.js`(신규)
- runtime: R0
- 추가 금지: 사이트 파일, step 13~17 수정, 보존·신규 판정에 다른 대응 조건, at-rule 판정, 결과 정렬

## 작업
1. `SNAP 18` → RED → 구현 → GREEN.
2. BASE `body{font-family:"Pretendard",sans-serif;font-weight:400} h2{font-weight:700} .project-card{font:500 1rem/1.5 "Pretendard",sans-serif}`(`css/style.css`):
   - `matchesBaseRule`: 같은 Rule true; `.project-card` → `.project-card, .featured-card` true; → `.project-card, .hero-name` false; → `.card` false; chain만 다름(`@media (min-width: 1024px)`) false; file만 다름 false
   - `[]`: 변경 없음; `.project-card, .featured-card{font:500 1rem/1.5 "Pretendard",sans-serif}`; `.x{font-weight:700;font-size:1.25rem;letter-spacing:.01em}`; `@font-face{font-family:X}` 추가
   - 정확히: `body{font-weight:400}`만 → `["font-decl-missing:|body|font-family"]`; + `html{font-family:"Pretendard",sans-serif}` → `["font-decl-missing:|body|font-family", "font-asset:html"]`; `@media (min-width: 1024px){body{font-family:"Pretendard",sans-serif}}`로 이동 → `["font-decl-missing:|body|font-family", "font-asset:body"]`; `body{font-family:"Inter",sans-serif;font-weight:400}` → 같음; `.project-card{}` → `["font-decl-missing:|.project-card|font"]`; `.project-card, .hero-name{…}` → `["font-decl-missing:|.project-card|font", "font-asset:.project-card, .hero-name"]`; `.card{…}` → `["font-decl-missing:|.project-card|font", "font-asset:.card"]`; `.x{font-family:Inter}` → `["font-asset:.x"]`; body font-family 삭제 + 끝 `.x{font-family:Inter}` → `["font-decl-missing:|body|font-family", "font-asset:.x"]`
   - 입력 불변

## AC
- `T design-guard-font.spec.js design-guard-color.spec.js design-guard-color-rules.spec.js design-guard-color-pairs.spec.js color-vocab.spec.js css-parse.spec.js && FULL && GATE 18 tests/helpers/design-guard-font.js,tests/specs/design-guard-font.spec.js tests/helpers/design-guard-font.js,tests/specs/design-guard-font.spec.js`
