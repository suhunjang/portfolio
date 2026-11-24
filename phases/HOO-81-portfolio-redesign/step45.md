# Step 45 — component-hover-active

- 목적: desktop dark/light hover·active 비색 상태(transform·opacity만)와 상태별 BASE 색 보존 검증. generator와 spec이 공용 `measureStateSequence`로 대상마다 새 page에서 측정해 대상 간 상태를 격리한다.
- 예상 20분 / 선행 0~44 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §3(`THEME_KEY`, 모달·`modal-open`), §16.2(측정 helper, step 45 상태 순서 측정 helper·hover·active·BASE 상태 색 fixture·격리 회귀), §16.4(DESIGN_HASH_CHECK 후 `Components.dc.html` 읽기 전용); `tests/helpers/component-state.js`(import만)
- tracked 허용(exact): `css/style.css`(`.hero-cta .btn`·`.featured-card`·`#projectGrid .project-card`의 `:hover`·`:active` 규칙에서 transform·opacity·transition만), `tests/helpers/state-sequence.js`(신규), `tests/scripts/make-state-colors.mjs`(신규), `tests/fixtures/component-state-colors.json`(신규), `tests/specs/component-hover.spec.js`(신규)
- runtime: R0 + Playwright 브라우저 실행
- 금지: §15.7, `index.html`, `js/*`, 색 선언(기존 규칙에 추가 포함), hit target·clamp 규칙, focus-visible, `component-state.js`·기존 spec 수정, fixture 손편집, generator·spec에서 `measureStateSequence` 밖의 상태 측정, 여러 대상에 한 page 재사용

## 작업 (TDD)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step45` → `python3 -I tests/scripts/design-intake-check.py`
2. `state-sequence.js`: 설계 §16.2 `measureStateSequence(context, { url, selector, nth = 0, beforeMeasure = null }) → { default, hover, active }` 고정 절차 그대로 — 대상마다 `context.newPage()` → `goto(url)` → `document.fonts.ready` → `beforeMeasure(page)` → `scrollIntoViewIfNeeded()` → `waitForFiniteAnimations` → `mouse.move(0, 0)` 후 default → `locator.hover()` 후 hover → `mouse.down()` 직후 active → finally에서 down이 실행됐으면 `mouse.up()`, 그다음 항상 `page.close()`. 상태 값 `{ color, backgroundColor, borderColor, outlineColor, transform, opacity }`(`measureState` 사용).
3. `make-state-colors.mjs`(래퍼로 실행, Git은 `git show <BASE>:<path>` 읽기만):
   - `@playwright/test`의 `chromium`을 띄우고 테마(`dark`, `light`)마다 context 하나(viewport 1280×800)를 만든다. context `route('http://base.invalid/**')`에서 경로별 `git show <BASE>:<path>` 내용을 제공(BASE에 없는 경로 404, Google Fonts 요청은 통과), BASE `js/main.js`에서 `THEME_KEY` 값을 정규식으로 추출해 context `addInitScript`로 테마 설정
   - 그 context에서 키마다 `measureStateSequence(context, { url: 'http://base.invalid/index.html', selector, nth })`를 호출: `hero-cta-btn-{i}`(`.hero-cta .btn`, nth i), `grid-card-0`, `grid-card-1`(`#projectGrid .project-card[data-project="0"|"1"]`). 결과 중 color·backgroundColor·borderColor만 기록
   - 출력 `{ "schemaVersion": 1, "base": "<BASE>", "themes": { "dark": { "<key>": { "default": { "color", "backgroundColor", "borderColor" }, "hover": {…}, "active": {…} } }, "light": {…} } }`, 키 정렬·2칸 들여쓰기·끝 개행 1개
   - 인자 없음 → `tests/fixtures/component-state-colors.json` 쓰기; `--check` → 메모리에서 다시 만들어 파일 bytes와 비교, 다르면 stderr `state-colors: mismatch` exit 1, 같으면 stdout `state-colors: OK`
4. fixture 생성: `sh tests/scripts/with-env.sh node tests/scripts/make-state-colors.mjs`
5. `component-hover.spec.js`(`desktop-dark`·`desktop-light`만, 나머지 `test.skip`) 먼저 실패 확인. 테스트 `context`(project 테마 fixture 적용)와 url `/`로 `measureStateSequence`만 호출:
   - fixture 구조·`base` 값·두 테마·키 집합(`hero-cta-btn-*` 개수 = 현재 `.hero-cta .btn` 개수, `grid-card-0`, `grid-card-1`)
   - `.hero-cta .btn` 각각과 `grid-card-0`·`grid-card-1`: default·hover·active 각 상태의 현재 색 3속성 = fixture[테마][키][같은 상태]
   - 첫 `.featured-card`(data-project 1): 각 상태 색 3속성 = fixture[테마][`grid-card-1`][같은 상태]
   - hover와 active 각각에서 transform 또는 opacity가 그 요소의 default와 다름; outline-color는 그 요소 default와 같음
   - 격리 회귀: (a) `grid-card-0` 순서 측정 직후 `grid-card-1` 순서 측정이 완료되고, 그 호출의 `beforeMeasure`에서 `#projectModal`이 hidden·body에 `modal-open` 없음; (b) `hero-cta-btn-0` 순서 측정 직후 다음 대상 호출의 `beforeMeasure`에서 `location.hash === ''`·`scrollY === 0`; (c) 각 호출 전후 `context.pages().length` 동일; (d) 존재하지 않는 selector로 호출하면 reject되고 `context.pages().length`가 호출 전과 같음(finally로 page 종료)
6. style.css(guard 통과).

## AC

- `python3 -I tests/scripts/design-intake-check.py && sh tests/scripts/with-env.sh node tests/scripts/make-state-colors.mjs --check && sh tests/scripts/with-env.sh npm --prefix tests test -- component-hover.spec.js component-hit.spec.js css-parse.spec.js color-vocab.spec.js design-guard-color-rules.spec.js design-guard-color.spec.js design-guard-css.spec.js design-guard.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step45.json --allow css/style.css,tests/helpers/state-sequence.js,tests/scripts/make-state-colors.mjs,tests/fixtures/component-state-colors.json,tests/specs/component-hover.spec.js --require-absent tests/helpers/state-sequence.js,tests/scripts/make-state-colors.mjs,tests/fixtures/component-state-colors.json,tests/specs/component-hover.spec.js` → exit 0 (두 번째 명령 stdout `state-colors: OK`)
