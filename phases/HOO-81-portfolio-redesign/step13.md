# Step 13 — css-parser

- 목적: 설계 §11.4 step 13 parser.
- 18분 / 선행 0~12 / 공통 §9 / gate GATE
- 허용(exact): `tests/helpers/css-parse.js`, `tests/specs/css-parse.spec.js`(신규)
- runtime: R0
- 추가 금지: 사이트 파일, Git·fs 접근, 외부 CSS 파서

## 작업
1. `SNAP 13` → RED spec → 구현 → GREEN.
2. spec(node, desktop-dark): 단일 Rule 형태(chain `[]`, atRule·prelude null, index 0); 주석 안 `{ }`·`;` 무시; `content: "a{b};c"`·`content: '}'` 보존; `url("a;b.png")` 보존; `@media (max-width: 768px) { @supports (display: grid) { .a { gap: 24px } } }` → chain 2단계, prelude null; `.a{} @media (x){.b{}} .c{}` index 0·1·2; `@import url(x.css);` → atRule `@import`·prelude `url(x.css)`; `@import url("a.css")  screen and (min-width:   10px);` → prelude 정확히 `url("a.css") screen and (min-width: 10px)`; URL만 `b.css`·조건만 `(min-width: 20px)` 변형 prelude가 원본·서로와 다름; `@charset "utf-8";` → prelude `"utf-8"`; `@font-face { font-family: X }` → prelude null·decls 1개; `.a, .b` 분리, `:is(.a, .b) .c`·`[data-x="a,b"]` 1개; 공백·줄바꿈 정규화; custom property 이름 원문·값 trim; `!important` 유지; 같은 선택자 두 번은 index 구분; `.a{color:red;color:blue}` decls 2개 순서 유지; 빈 입력 `[]`; 입력 불변.

## AC
- `T css-parse.spec.js && FULL && GATE 13 tests/helpers/css-parse.js,tests/specs/css-parse.spec.js tests/helpers/css-parse.js,tests/specs/css-parse.spec.js`
