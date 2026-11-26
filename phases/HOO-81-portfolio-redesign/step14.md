# Step 14 — color-vocab-graph

- 목적: 설계 §11.4 step 14 색 어휘(`color()` 포함, 대소문자 무시·identifier 경계)·`COLOR_PROPS`·양방향 token 그래프.
- 18분 / 선행 0~13 / 공통 §9 / gate GATE
- 허용(exact): `tests/helpers/color-vocab.js`, `tests/specs/color-vocab.spec.js`(신규)
- runtime: R0
- 추가 금지: 사이트 파일, step 13 수정, Git·fs, 문자열·`url()` 제외 스캔 생략

## 작업
1. `SNAP 14` → RED → 구현 → GREEN.
2. `COLOR_LITERAL_RE` = 설계 §11.4 step 14 그대로(hex 또는 `(?<![A-Za-z0-9_-])(?:rgb|rgba|hsl|hsla|hwb|lab|lch|oklab|oklch|color|color-mix)\s*\(`, 플래그 `i`). `isColorLiteralValue`는 따옴표 문자열·`url(…)` 내용을 먼저 제거한 뒤 판정.
3. spec:
   - `NAMED_COLORS` 149·`navy`·`RebeccaPurple`·`transparent`
   - `isColorLiteralValue` true: `#fff`, `#0d0f12`, `rgb(0 0 0)`, `hsla(0,0%,0%,.5)`, `color-mix(in srgb, red, blue)`, `navy`, `NAVY`, `currentColor`, `1px solid red`, `color(display-p3 1 0 0)`, `CoLoR(display-p3 1 0 0)`, `color(from rgb(255 0 0) srgb r g b)`, `color(from color(display-p3 1 0 0) srgb r g b / .5)`, `RGB (0 0 0)`(함수명 뒤 공백)
   - `isColorLiteralValue` false: `16px`, `var(--navy)`, `url(navy.png)`, `"navy"`, `none`, `mycolor(display-p3 1 0 0)`, `"color(display-p3 1 0 0)"`, `url(color(display-p3 1 0 0).png)`, `x-rgb(1 2 3)`
   - `COLOR_PROPS` = 설계 집합, `border-top-color`·`border-right-color`·`border-bottom-color`·`border-left-color`·`border-block-start-color`·`border-inline-end-color`·`-webkit-text-fill-color`·`text-emphasis-color`·`scrollbar-color`·`stop-color` 포함, `padding`·`font-size`·`transform` 불포함
   - `varRefs` `var(--a)` → `['--a']`, `var(--a, var(--b))` → `['--a','--b']`
   - `isColorDecl` true `['color', x]`, `['fill', x]`, `['border', '1px solid var(--x)']`, `['border-top-color', 'var(--x)']`, `['border-left-color', 'transparent']`, `['border-inline-start-color', 'var(--x)']`, `['-webkit-text-fill-color', 'var(--x)']`, `['scrollbar-color', 'auto']`, `['text-decoration', 'underline var(--x)']` / false `['border', '0']`, `['border', 'none']`, `['border-top', 'none']`, `['outline', 'none']`, `['text-decoration', 'none']`, `['padding', '16px']`, `['--card', '#fff']`
   - 그래프 style `:root{--card:#fff;--accent:var(--brand);--pad:16px;--alias:var(--accent);--ring:var(--pad);--p3:color(display-p3 1 0 0)} .a{background:var(--card)} .b{color:var(--alias)}` + themes `:root{--brand:#3355ff}` → 정확히 `--card`, `--accent`, `--brand`, `--alias`, `--p3`(`--pad`·`--ring` 제외); `.c{border-top-color:var(--ring2)}`+`:root{--ring2:var(--pad)}` 추가 시 `--ring2`·`--pad`·`--ring` 포함; `isColorValue('var(--alias)', set)` true, `isColorValue('var(--p3)', set)` true, `('var(--pad)', 기본 set)` false
   - 입력 불변

## AC
- `T color-vocab.spec.js css-parse.spec.js && FULL && GATE 14 tests/helpers/color-vocab.js,tests/specs/color-vocab.spec.js tests/helpers/color-vocab.js,tests/specs/color-vocab.spec.js`
