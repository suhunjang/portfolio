# Step 48 — component-hover-active

- 목적: desktop dark/light hover·active 비색 상태(transform·opacity만)와 상태별 BASE 색 보존 검증.
- 예상 16분 / 선행 0~47 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §16.2(step 46 helper, step 47 fixture, step 48 hover·active), §16.4(DESIGN_HASH_CHECK 후 `Components.dc.html` 읽기 전용); `tests/helpers/state-sequence.js`(import만), `tests/fixtures/component-state-colors.json`(읽기만)
- tracked 허용(exact): `css/style.css`(`.hero-cta .btn`·`.featured-card`·`#projectGrid .project-card`의 `:hover`·`:active` 규칙에서 transform·opacity·transition만), `tests/specs/component-hover.spec.js`(신규)
- runtime: R0
- 금지: §15.7, `index.html`, `js/*`, 색 선언(기존 규칙에 추가·순서 변경 포함), 기존 색 규칙 순서 변경, hit target·clamp 규칙, focus-visible, helper·generator·fixture·기존 spec 수정, `measureStateSequence` 밖의 상태 측정

## 작업 (TDD)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step48` → `python3 -I tests/scripts/design-intake-check.py`
2. `component-hover.spec.js`(`desktop-dark`·`desktop-light`만, 나머지 `test.skip`) 먼저 실패 확인. 테스트 `context`(project 테마 fixture 적용)와 url `/`로 `measureStateSequence`만 호출:
   - `.hero-cta .btn` 각각(`hero-cta-btn-{i}`)과 `grid-card-0`·`grid-card-1`: default·hover·active 각 상태의 현재 색 3속성 = fixture[테마][키][같은 상태]
   - 첫 `.featured-card`(data-project 1): 각 상태 색 3속성 = fixture[테마][`grid-card-1`][같은 상태]
   - hover와 active 각각에서 transform 또는 opacity가 그 요소의 default와 다름; outline-color는 그 요소 default와 같음
3. style.css(guard 통과).

## AC

- `python3 -I tests/scripts/design-intake-check.py && sh tests/scripts/with-env.sh node tests/scripts/make-state-colors.mjs --check && sh tests/scripts/with-env.sh npm --prefix tests test -- component-hover.spec.js state-sequence.spec.js state-colors.spec.js component-hit.spec.js css-parse.spec.js color-vocab.spec.js design-guard-color-pairs.spec.js design-guard-color-rules.spec.js design-guard-color.spec.js design-guard-css.spec.js design-guard.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step48.json --allow css/style.css,tests/specs/component-hover.spec.js --require-absent tests/specs/component-hover.spec.js` → exit 0 (두 번째 명령 stdout `state-colors: OK`)
