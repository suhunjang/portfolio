# Step 48 — state-colors-fixture

- 목적: §11.2 BASE 상태 색 fixture generator·fixture·`--check`(정상·변형 별도 test, 각 75초).
- 19분(작성 9, 생성 1, 단독 3, FULL 5, gate 1) / 선행 0~47 / 공통 §9 / gate GATE
- 허용(exact): `tests/scripts/make-state-colors.mjs`, `tests/fixtures/component-state-colors.json`, `tests/specs/state-colors.spec.js`(신규)
- runtime: R0 + 브라우저(`tests/.tmp/state-colors-<pid>/`)
- 추가 금지: 사이트 파일, helper·기존 spec, fixture 손편집, `measureStateSequence` 밖 측정, Git 쓰기, 정상·변형 한 test 묶기, 실행별 다른 timeout

## 작업
1. `SNAP 48`
2. generator(`W`, Git은 `git show <BASE>:<path>`만): `chromium`, 테마(dark, light)마다 context 1개(1280×800), `route('http://base.invalid/**')`로 BASE 파일 제공(없음 404, Google Fonts 통과), BASE `js/main.js`에서 `THEME_KEY` 정규식 추출 → `addInitScript`; 키마다 `measureStateSequence(context, { url: 'http://base.invalid/index.html', selector, nth })`(`hero-cta-btn-{i}` = `.hero-cta .btn` nth i(BASE 개수), `grid-card-0`·`grid-card-1`), color·backgroundColor·borderColor만. 출력 `{ "schemaVersion": 1, "base": "<BASE>", "themes": { "dark": { "<key>": { "default": {…}, "hover": {…}, "active": {…} } }, "light": {…} } }` 키 정렬·2칸·끝 개행 1. 인자 없음 → fixture 쓰기; `--check [--fixture <path>]` → 다르면 stderr `state-colors: mismatch` exit 1, 같으면 stdout `state-colors: OK` 0; 그 밖 2.
3. 생성 `W node tests/scripts/make-state-colors.mjs`.
4. spec(node, desktop-dark; 독립 test 4개): `schema`(키 `schemaVersion, base, themes`·1·BASE·`dark, light`·키 = `hero-cta-btn-0..n-1`(n ≥ 1 = `tests/fixtures/baseline-index.html`의 `.hero-cta .btn` 수) ∪ `grid-card-0`·`grid-card-1`·상태 3·필드 3 비어 있지 않은 문자열); `serialization`(bytes = 키 정렬 `JSON.stringify(…, null, 2) + '\n'`); `check-ok`(첫 줄 정확히 `test.setTimeout(75000)`, `--check` subprocess timeout 60000ms → 0·`state-colors: OK`, 원본 불변); `check-mismatch`(첫 줄 정확히 `test.setTimeout(75000)`, `tests/.tmp/state-colors-<pid>/` 사본 값 하나 변경 → `--check --fixture <사본>` subprocess 60000ms → 1·`state-colors: mismatch`, 원본 불변, finally 사본 삭제).

## AC
- `W node tests/scripts/make-state-colors.mjs --check && T state-colors.spec.js state-sequence.spec.js && FULL && VS && GATE 48 tests/scripts/make-state-colors.mjs,tests/fixtures/component-state-colors.json,tests/specs/state-colors.spec.js tests/scripts/make-state-colors.mjs,tests/fixtures/component-state-colors.json,tests/specs/state-colors.spec.js`(첫 명령 `state-colors: OK`)
