# Step 18 — design-guard-type-asset

- 목적: 공용 대응 helper `matchesBaseRule`로 BASE `font-family`·`font` 선언을 양방향(보존·신규) 판정하고, `@import`를 file·chain·atRule·prelude로 대응하며, 서체·asset·content·unknown-token 검사와 `checkCss`를 결합한다(설계 §16.4 step 18).
- 예상 19분 / 선행 0~17 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §16.2(font-weight·font-family 보존), §16.3, §16.4(step 13 `prelude` 정규화 계약, step 15 `featuredCounterpart`, step 18); step 13~17 helper(import만)
- tracked 허용(exact): `tests/helpers/design-guard-css.js`(신규), `tests/specs/design-guard-css.spec.js`(신규)
- runtime: R0
- 금지: §15.7, 사이트 파일, step 13~17 helper·spec 수정(step 13 정규화 계약 포함), Git·파일 시스템 접근, 보존·신규 판정에 서로 다른 대응 조건 사용

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step18`
2. `design-guard-css.js` 추가 API: `matchesBaseRule(baseRule, currentRule)`, `checkTypeAndAssets({ baseRules, currentRules })`(보존 → 신규 순서, 서체 두 방향 모두 `matchesBaseRule`만 사용, `@import`는 file·chain·atRule·prelude 대응), `checkCss({ baseCss, currentCss, baseThemes, currentThemes })` — 설계 §16.4 step 18 그대로.
3. `design-guard-css.spec.js`(node 전용, desktop-dark만, 합성 BASE style `@import url("a.css") screen and (min-width: 10px); body{font-family:"Pretendard",sans-serif;font-weight:400} h2{font-weight:700} .project-card{font:500 1rem/1.5 "Pretendard",sans-serif} :root{--pad:16px}`, themes `:root{--brand:#3355ff}`):
   - `matchesBaseRule` 단위: 같은 Rule → true; `.project-card` → `.project-card, .featured-card` → true; `.project-card` → `.project-card, .hero-name` → false; `.project-card` → `.card` → false; chain만 다름(`@media (min-width: 1024px)`) → false; file만 다름 → false
   - `checkTypeAndAssets` 허용 → `[]`: 변경 없음(기존 `@import` 그대로); 공백만 다른 `@import url("a.css")   screen and (min-width:   10px);`(step 13 trim·연속 공백 1칸 정규화 후 BASE와 같은 prelude `url("a.css") screen and (min-width: 10px)`); `@import` 삭제; `.x{font-weight:700;font-size:1.25rem;letter-spacing:.01em}`; `.y{content:none}`; `.z{padding:var(--pad)}`; 새 `--gap:24px`와 `var(--gap)`; `.project-card, .featured-card{font:500 1rem/1.5 "Pretendard",sans-serif}`(featured 대응 확장은 보존 충족·신규 아님)
   - `@import` 거부(정확한 결과 배열): URL만 변경 `@import url("b.css") screen and (min-width: 10px);` → `["asset:@import"]`; 조건만 변경 `@import url("a.css") screen and (min-width: 20px);` → `["asset:@import"]`; 새 import 추가 `@import url(f.css);` → `["asset:@import"]`
   - 보존·신규 서체 거부(정확한 결과 배열):
     - 삭제: `body{font-weight:400}`만 남김 → `["font-decl-missing:|body|font-family"]`
     - 선택자 이동: `body{font-weight:400} html{font-family:"Pretendard",sans-serif}` → `["font-decl-missing:|body|font-family", "font-asset:html"]`
     - 미디어 조건 이동: `body{font-weight:400} @media (min-width: 1024px){body{font-family:"Pretendard",sans-serif}}` → `["font-decl-missing:|body|font-family", "font-asset:body"]`
     - 값 변경: `body{font-family:"Inter",sans-serif;font-weight:400}` → `["font-decl-missing:|body|font-family", "font-asset:body"]`
     - `font` shorthand 삭제: `.project-card{}` → `["font-decl-missing:|.project-card|font"]`
     - 임의 선택자 확장: `.project-card, .hero-name{font:500 1rem/1.5 "Pretendard",sans-serif}` → `["font-decl-missing:|.project-card|font", "font-asset:.project-card, .hero-name"]`
     - 선택자 교체: `.card{font:500 1rem/1.5 "Pretendard",sans-serif}` → `["font-decl-missing:|.project-card|font", "font-asset:.card"]`
   - 신규 거부(유지): `.x{font-family:Inter}` → `font-asset:.x`; `@font-face{font-family:X;src:url(x.woff2)}` → `["font-asset:@font-face", "asset:@font-face"]`; `.x{font-weight:800}` → `font-weight:800`; `.x{background-image:url(a.png)}` → `asset:.x`; `.x::after{content:'★'}` → `content:.x::after`; `.x{margin:var(--nope)}` → `unknown-token:--nope`
   - `checkCss` 결합: `.x{background-image:url(a.png)}` → `asset:.x`와 `color-decl-new:.x` 모두 포함; themes 텍스트 변경 → `themes-changed` 포함; `body` font-family 삭제 → `font-decl-missing:|body|font-family` 포함; import URL 변경 → `asset:@import` 포함; 변경 없음 `[]`
   - 입력 불변

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- design-guard-css.spec.js design-guard-color.spec.js design-guard-color-rules.spec.js design-guard-color-pairs.spec.js color-vocab.spec.js css-parse.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step18.json --allow tests/helpers/design-guard-css.js,tests/specs/design-guard-css.spec.js --require-absent tests/helpers/design-guard-css.js,tests/specs/design-guard-css.spec.js` → exit 0
