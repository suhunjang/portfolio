# Step 13 — css-parser

- 목적: design guard용 CSS parser(설계 §16.4 step 13)와 parser 단위 테스트.
- 예상 17분 / 선행 0~12 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §16.4(step 13)
- tracked 허용(exact): `tests/helpers/css-parse.js`(신규), `tests/specs/css-parse.spec.js`(신규)
- runtime: R0
- 금지: §15.7, 사이트 파일, Git·파일 시스템 접근(순수 함수만), 외부 CSS 파서 의존성

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step13`
2. `css-parse.js`: `parseCssRules(text, file)`, `splitSelectors(text)`, `normalizeValue(value)` — 설계 §16.4 step 13 계약.
3. `css-parse.spec.js`(node 전용, desktop-dark만): 단일 규칙 Rule 형태(file·chain `[]`·selectors·decls·atRule null·index); 주석 안 `{ }`·`;` 무시; `content: "a{b};c"`·`content: '}'` 문자열 보존; `url("a;b.png")` 보존; 중첩 `@media (max-width: 768px) { @supports (display: grid) { .a { gap: 24px } } }` → chain 두 단계(공백 정규화); `@import url(x.css);` → atRule `@import` Rule; `@font-face { font-family: X }` → atRule `@font-face` Rule; 선택자 `.a, .b` 분리, `:is(.a, .b) .c` 한 개, `[data-x="a,b"]` 한 개; 공백·줄바꿈 정규화; custom property 이름 원문 유지·값 trim; `!important` 유지; 같은 선택자 두 번은 index로 구분; 빈 입력 `[]`; 입력 불변.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- css-parse.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step13.json --allow tests/helpers/css-parse.js,tests/specs/css-parse.spec.js --require-absent tests/helpers/css-parse.js,tests/specs/css-parse.spec.js` → exit 0
