# Step 14 — color-vocab-graph

- 목적: 색 값 어휘(리터럴·named color·`currentColor`)와 custom property 양방향 의존 그래프(설계 §16.4 step 14)와 단위 테스트.
- 예상 16분 / 선행 0~13 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §16.4(step 13·14); `tests/helpers/css-parse.js`(import만)
- tracked 허용(exact): `tests/helpers/color-vocab.js`(신규), `tests/specs/color-vocab.spec.js`(신규)
- runtime: R0
- 금지: §15.7, 사이트 파일, step 13 helper·spec 수정, Git·파일 시스템 접근

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step14`
2. `color-vocab.js` 추가 API: `NAMED_COLORS`, `COLOR_PROPS`, `COLOR_LITERAL_RE`, `valueIdentifiers(value)`, `varRefs(value)`, `isColorLiteralValue(value)`, `isColorDecl([prop, value])`, `customPropertyDefs(rules)`, `colorTokenSet(rules)`, `isColorValue(value, colorTokens)` — 설계 §16.4 step 14 그대로.
3. `color-vocab.spec.js`(node 전용, desktop-dark만, 합성 CSS를 `parseCssRules`로 변환)
   - 어휘: `NAMED_COLORS` 크기 149, `navy`·`RebeccaPurple`·`transparent` 포함; `isColorLiteralValue` true — `#fff`, `#0d0f12`, `rgb(0 0 0)`, `hsla(0,0%,0%,.5)`, `color-mix(in srgb, red, blue)`, `navy`, `NAVY`, `currentColor`, `1px solid red`; false — `16px`, `var(--navy)`, `url(navy.png)`, `"navy"`, `none`
   - `varRefs`: `var(--a)` → `['--a']`, `var(--a, var(--b))` → `['--a','--b']`
   - `isColorDecl`: `color`·`fill` true, `border: 0`·`border: none` false, `border: 1px solid var(--x)` true, `padding` false, `['--card', '#fff']` false
   - 그래프(합성 style `:root{--card:#fff;--accent:var(--brand);--pad:16px;--alias:var(--accent);--ring:var(--pad)} .a{background:var(--card)} .b{color:var(--alias)}`, themes `:root{--brand:#3355ff}`): `colorTokenSet` = `--card`, `--accent`, `--brand`, `--alias`(양방향 별칭 사슬), `--pad`·`--ring` 제외; 색 선언이 직접 참조하지 않아도 리터럴 정의(`--brand`)는 포함
   - `isColorValue('var(--alias)', set)` true, `isColorValue('var(--pad)', set)` false
   - 입력 불변

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- color-vocab.spec.js css-parse.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step14.json --allow tests/helpers/color-vocab.js,tests/specs/color-vocab.spec.js --require-absent tests/helpers/color-vocab.js,tests/specs/color-vocab.spec.js` → exit 0
