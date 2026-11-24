# Step 19 — design-guard-css

- 목적: 설계 §11.4 step 19 — import·font-face·URL·content·weight·unknown-token, `checkTypeAndAssets`(서체 결과 선행), `checkCss`.
- 18분(작성 10, 단독 1, 누적 GUARD 2, FULL 4, gate 1) / 선행 0~18 / 공통 §9 / gate GATE
- 허용(exact): `tests/helpers/design-guard-css.js`, `tests/specs/design-guard-css.spec.js`(신규)
- runtime: R0
- 추가 금지: 사이트 파일, step 13~18 수정(정규화·서체 판정 재구현 금지)

## 작업
1. `SNAP 19` → RED → 구현 → GREEN.
2. BASE style `@import url("a.css") screen and (min-width: 10px); body{font-family:"Pretendard",sans-serif;font-weight:400} h2{font-weight:700} .project-card{font:500 1rem/1.5 "Pretendard",sans-serif} :root{--pad:16px}`, themes `:root{--brand:#3355ff}`:
   - `[]`: 변경 없음; `@import url("a.css")   screen and (min-width:   10px);`; `@import` 삭제; `.x{font-weight:700;font-size:1.25rem;letter-spacing:.01em}`; `.y{content:none}`; `.z{padding:var(--pad)}`; `--gap:24px`+`var(--gap)`; featured 확장 font
   - 정확히: `@import url("b.css") screen and (min-width: 10px);` → `["asset:@import"]`; `@import url("a.css") screen and (min-width: 20px);` → `["asset:@import"]`; `@import url(f.css);` 추가 → `["asset:@import"]`; `@font-face{font-family:X;src:url(x.woff2)}` → `["font-asset:@font-face", "asset:@font-face"]`; `.x{font-weight:800}` → `["font-weight:800"]`; `.x{background-image:url(a.png)}` → `["asset:.x"]`; `.x::after{content:'★'}` → `["content:.x::after"]`; `.x{margin:var(--nope)}` → `["unknown-token:--nope"]`; body font-family 삭제 + `.x{font-weight:800}` → `["font-decl-missing:|body|font-family", "font-weight:800"]`; `.x{font-weight:800;font-family:Inter}` → `["font-asset:.x", "font-weight:800"]`
   - `checkCss` 포함: `.x{background-image:url(a.png)}` → `asset:.x`·`color-decl-new:.x`; themes 변경 → `themes-changed`; body font-family 삭제 → `font-decl-missing:|body|font-family`; import URL 변경 → `asset:@import`; themes `--brand` 중복 → `색 토큰 중복 정의: --brand @ css/themes.css - :root (count=2)`·`themes-changed`; 변경 없음 `[]`
   - 입력 불변

## AC
- `T design-guard-css.spec.js design-guard-font.spec.js design-guard-color.spec.js design-guard-color-rules.spec.js design-guard-color-pairs.spec.js color-vocab.spec.js css-parse.spec.js && FULL && GATE 19 tests/helpers/design-guard-css.js,tests/specs/design-guard-css.spec.js tests/helpers/design-guard-css.js,tests/specs/design-guard-css.spec.js`
