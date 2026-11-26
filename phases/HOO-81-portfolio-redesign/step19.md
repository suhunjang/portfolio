# Step 19 — design-guard-css

- 목적: 설계 §11.4 step 19 — import·font-face·URL·content·weight·`unknown-token`(KNOWN = BASE·현재 네 Rule 집합의 모든 custom property 이름 합집합), `checkTypeAndAssets`(서체 결과 선행), `checkCss`.
- 19분(작성 11, 단독 1, 누적 GUARD 2, FULL 4, gate 1) / 선행 0~18 / 공통 §9 / gate GATE
- 허용(exact): `tests/helpers/design-guard-css.js`, `tests/specs/design-guard-css.spec.js`(신규)
- runtime: R0
- 추가 금지: 사이트 파일, step 13~18 수정(정규화·서체 판정·`varRefs` 재구현 금지), `unknown-token`에서 colorTokens 사용·custom property 추가·삭제·값 적법성 판정(step 14~17 몫)

## 작업
1. `SNAP 19` → RED → 구현 → GREEN.
2. 입력: baseRules·currentRules는 각각 `parseCssRules(style, 'css/style.css')`와 `parseCssRules(themes, 'css/themes.css')`를 이어 붙인 배열. BASE style `@import url("a.css") screen and (min-width: 10px); body{font-family:"Pretendard",sans-serif;font-weight:400} h2{font-weight:700} .project-card{font:500 1rem/1.5 "Pretendard",sans-serif} :root{--pad:16px} .brand{color:var(--brand)}`, BASE themes `:root{--brand:#3355ff}`(현재 themes 동일).
3. `checkTypeAndAssets` spec:
   - `[]`: 변경 없음(`.brand`의 themes `--brand` 참조 포함); `.y{border-color:var(--brand)}` 추가(unknown-token 없음, 색 적법성은 다른 guard 몫); `@import url("a.css")   screen and (min-width:   10px);`; `@import` 삭제; `.x{font-weight:700;font-size:1.25rem;letter-spacing:.01em}`; `.y{content:none}`; `.z{padding:var(--pad)}`; 현재에 `:root{--gap:24px}` + `.g{gap:var(--gap)}`(현재에만 정의된 이름도 KNOWN); 현재에서 `:root{--pad:16px}` 삭제 + `.z{padding:var(--pad)}`(BASE에만 정의된 이름도 KNOWN, 삭제 적법성은 다른 guard 결과로만 판정); featured 확장 font
   - 정확히: `@import url("b.css") screen and (min-width: 10px);` → `["asset:@import"]`; `@import url("a.css") screen and (min-width: 20px);` → `["asset:@import"]`; `@import url(f.css);` 추가 → `["asset:@import"]`; `@font-face{font-family:X;src:url(x.woff2)}` → `["font-asset:@font-face", "asset:@font-face"]`; `.x{font-weight:800}` → `["font-weight:800"]`; `.x{background-image:url(a.png)}` → `["asset:.x"]`; `.x::after{content:'★'}` → `["content:.x::after"]`; `.x{margin:var(--nope)}` → `["unknown-token:--nope"]`; `.x{color:var(--brand);margin:var(--nope)}` → `["unknown-token:--nope"]`; 현재에 `:root{--a:1px}` + `.x{margin:var(--a, var(--nope))}` → `["unknown-token:--nope"]`; `.x{margin:var(--nope)} .w{padding:var(--nope)}` → `["unknown-token:--nope"]`(1회); body font-family 삭제 + `.x{font-weight:800}` → `["font-decl-missing:|body|font-family", "font-weight:800"]`; `.x{font-weight:800;font-family:Inter}` → `["font-asset:.x", "font-weight:800"]`
4. `checkCss` 포함: `.x{background-image:url(a.png)}` → `asset:.x`·`color-decl-new:.x`; themes 변경 → `themes-changed`; body font-family 삭제 → `font-decl-missing:|body|font-family`; import URL 변경 → `asset:@import`; themes `--brand` 중복 → `색 토큰 중복 정의: --brand @ css/themes.css - :root (count=2)`·`themes-changed`; 변경 없음 `[]`.
5. 입력 불변.

## AC
- `T design-guard-css.spec.js design-guard-font.spec.js design-guard-color.spec.js design-guard-color-rules.spec.js design-guard-color-pairs.spec.js color-vocab.spec.js css-parse.spec.js && FULL && GATE 19 tests/helpers/design-guard-css.js,tests/specs/design-guard-css.spec.js tests/helpers/design-guard-css.js,tests/specs/design-guard-css.spec.js`
