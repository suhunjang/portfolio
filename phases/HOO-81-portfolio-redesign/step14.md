# Step 14 — color-vocab-graph

- 목적: 색 값 어휘(리터럴·named color·`currentColor`), 색 적용 속성 분류(`COLOR_PROPS`, 방향·논리 border 색 longhand 포함), custom property 양방향 의존 그래프(설계 §16.4 step 14)와 단위 테스트.
- 예상 17분 / 선행 0~13 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §16.4(step 13·14); `tests/helpers/css-parse.js`(import만)
- tracked 허용(exact): `tests/helpers/color-vocab.js`(신규), `tests/specs/color-vocab.spec.js`(신규)
- runtime: R0
- 금지: §15.7, 사이트 파일, step 13 helper·spec 수정, Git·파일 시스템 접근

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step14`
2. `color-vocab.js` 추가 API: `NAMED_COLORS`, `COLOR_PROPS`, `COLOR_LITERAL_RE`, `valueIdentifiers(value)`, `varRefs(value)`, `isColorLiteralValue(value)`, `isColorDecl([prop, value])`, `customPropertyDefs(rules)`, `colorTokenSet(rules)`, `isColorValue(value, colorTokens)` — 설계 §16.4 step 14 그대로(`COLOR_PROPS`는 설계 목록과 정확히 같은 집합).
3. `color-vocab.spec.js`(node 전용, desktop-dark만, 합성 CSS를 `parseCssRules`로 변환)
   - 어휘: `NAMED_COLORS` 크기 149, `navy`·`RebeccaPurple`·`transparent` 포함; `isColorLiteralValue` true — `#fff`, `#0d0f12`, `rgb(0 0 0)`, `hsla(0,0%,0%,.5)`, `color-mix(in srgb, red, blue)`, `navy`, `NAVY`, `currentColor`, `1px solid red`; false — `16px`, `var(--navy)`, `url(navy.png)`, `"navy"`, `none`
   - `COLOR_PROPS`: 설계 목록과 집합 동일; `border-top-color`, `border-right-color`, `border-bottom-color`, `border-left-color`, `border-block-start-color`, `border-inline-end-color`, `-webkit-text-fill-color`, `text-emphasis-color`, `scrollbar-color`, `stop-color` 포함; `padding`·`font-size`·`transform` 불포함
   - `varRefs`: `var(--a)` → `['--a']`, `var(--a, var(--b))` → `['--a','--b']`
   - `isColorDecl` true: `['color', x]`, `['fill', x]`, `['border', '1px solid var(--x)']`, `['border-top-color', 'var(--x)']`, `['border-left-color', 'transparent']`, `['border-inline-start-color', 'var(--x)']`, `['-webkit-text-fill-color', 'var(--x)']`, `['scrollbar-color', 'auto']`, `['text-decoration', 'underline var(--x)']`
   - `isColorDecl` false: `['border', '0']`, `['border', 'none']`, `['border-top', 'none']`, `['outline', 'none']`, `['text-decoration', 'none']`, `['padding', '16px']`, `['--card', '#fff']`
   - 그래프(합성 style `:root{--card:#fff;--accent:var(--brand);--pad:16px;--alias:var(--accent);--ring:var(--pad)} .a{background:var(--card)} .b{color:var(--alias)}`, themes `:root{--brand:#3355ff}`): `colorTokenSet` = `--card`, `--accent`, `--brand`, `--alias`(양방향 별칭 사슬), `--pad`·`--ring` 제외; 색 선언이 직접 참조하지 않아도 리터럴 정의(`--brand`)는 포함; `.c{border-top-color:var(--ring2)}`와 `:root{--ring2:var(--pad)}`를 추가하면 `--ring2`와 별칭 사슬로 `--pad`·`--ring`도 포함(색 longhand 참조가 시작 집합에 들어감)
   - `isColorValue('var(--alias)', set)` true, `isColorValue('var(--pad)', 기본 set)` false
   - 입력 불변

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- color-vocab.spec.js css-parse.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step14.json --allow tests/helpers/color-vocab.js,tests/specs/color-vocab.spec.js --require-absent tests/helpers/color-vocab.js,tests/specs/color-vocab.spec.js` → exit 0
