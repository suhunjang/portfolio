# Step 13 — css-parser

- 목적: design guard용 CSS parser(설계 §16.4 step 13, Rule `prelude` 포함)와 parser 단위 테스트.
- 예상 18분 / 선행 0~12 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §16.4(step 13)
- tracked 허용(exact): `tests/helpers/css-parse.js`(신규), `tests/specs/css-parse.spec.js`(신규)
- runtime: R0
- 금지: §15.7, 사이트 파일, Git·파일 시스템 접근(순수 함수만), 외부 CSS 파서 의존성

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step13`
2. `css-parse.js`: `parseCssRules(text, file)`, `splitSelectors(text)`, `normalizeValue(value)` — 설계 §16.4 step 13 계약(Rule 필드 `file, chain, selectors, decls, atRule, prelude, index`).
3. `css-parse.spec.js`(node 전용, desktop-dark만): 단일 규칙 Rule 형태(file·chain `[]`·selectors·decls·atRule null·prelude null·index); 주석 안 `{ }`·`;` 무시; `content: "a{b};c"`·`content: '}'` 문자열 보존; `url("a;b.png")` 보존; 중첩 `@media (max-width: 768px) { @supports (display: grid) { .a { gap: 24px } } }` → chain 두 단계(공백 정규화), 내부 Rule prelude null; `@import url(x.css);` → atRule `@import`·prelude `url(x.css)`; `@import url("a.css")  screen and (min-width:   10px);` → atRule `@import`·prelude 정확히 `url("a.css") screen and (min-width: 10px)`(URL·조건 보존, 공백 정규화); 같은 import에서 URL만 `b.css`로 바꾼 것과 조건만 `(min-width: 20px)`로 바꾼 것의 prelude가 원본·서로와 모두 다름; `@charset "utf-8";` → atRule `@charset`·prelude `"utf-8"`; `@font-face { font-family: X }` → atRule `@font-face`·prelude null·decls 1개; 선택자 `.a, .b` 분리, `:is(.a, .b) .c` 한 개, `[data-x="a,b"]` 한 개; 공백·줄바꿈 정규화; custom property 이름 원문 유지·값 trim; `!important` 유지; 같은 선택자 두 번은 index로 구분; 같은 Rule 안 같은 prop 두 번(`.a{color:red;color:blue}`)은 decls에 두 항목을 등장 순서로 유지; 빈 입력 `[]`; 입력 불변.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- css-parse.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step13.json --allow tests/helpers/css-parse.js,tests/specs/css-parse.spec.js --require-absent tests/helpers/css-parse.js,tests/specs/css-parse.spec.js` → exit 0
