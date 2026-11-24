# Step 15 — design-guard-type-asset

- 목적: 서체·asset·content·unknown-token 검사와 `checkCss` 결합(설계 §16.4 step 15).
- 예상 15분 / 선행 0~14 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §16.2(font-weight), §16.4; `tests/helpers/css-parse.js`, `tests/helpers/design-guard-color.js`(import만)
- tracked 허용(exact): `tests/helpers/design-guard-css.js`(신규), `tests/specs/design-guard-css.spec.js`(신규)
- runtime: R0
- 금지: §15.7, 사이트 파일, step 13·14 helper·spec 수정, Git·파일 시스템 접근

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step15`
2. `design-guard-css.js`: `checkTypeAndAssets({ baseRules, currentRules })`, `checkCss({ baseCss, currentCss, baseThemes, currentThemes })`.
3. `design-guard-css.spec.js`(node 전용, desktop-dark만, 합성 BASE style `body{font-family:"Pretendard",sans-serif;font-weight:400} h2{font-weight:700} :root{--pad:16px}`, themes `:root{--brand:#3355ff}`):
   - 허용 → `[]`: 변경 없음; `.x{font-weight:700;font-size:1.25rem;letter-spacing:.01em}`; `.y{content:none}`; `.z{padding:var(--pad)}`; 새 `--gap:24px`와 `var(--gap)` 사용
   - 거부: `.x{font-family:Inter}` → `font-asset:.x`; `@import url(f.css);` → `font-asset:@import`; `@font-face{font-family:X;src:url(x.woff2)}` → `font-asset:@font-face`(그리고 `asset:@font-face`); `.x{font-weight:800}` → `font-weight:800`; `.x{background-image:url(a.png)}` → `asset:.x`(색 검사는 step 14 몫이므로 이 spec은 `checkTypeAndAssets`만 볼 때 asset만 기대); `.x::after{content:'★'}` → `content:.x::after`; `.x{margin:var(--nope)}` → `unknown-token:--nope`
   - `checkCss` 결합: 위 `background-image` 사례는 `checkCss` 결과에 `asset:.x`와 step 14의 `color-decl-new:.x`가 모두 있음; themes 텍스트 변경 → `themes-changed` 포함; 변경 없음 `[]`
   - 입력 불변

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- design-guard-css.spec.js design-guard-color.spec.js css-parse.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step15.json --allow tests/helpers/design-guard-css.js,tests/specs/design-guard-css.spec.js --require-absent tests/helpers/design-guard-css.js,tests/specs/design-guard-css.spec.js` → exit 0
