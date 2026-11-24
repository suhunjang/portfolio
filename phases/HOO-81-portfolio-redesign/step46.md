# Step 46 — component-clamp-stripe

- 목적: blurb line clamp 3, 본문 보존, 선택적 strength 장식 stripe 제거.
- 예상 15분 / 선행 0~45 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §3, §16.2(측정 helper, step 46), §16.4(strength stripe 예외, DESIGN_HASH_CHECK 후 `DesktopExplore.dc.html`·`Components.dc.html` 읽기 전용); main.js 카드 blurb 렌더 요소(spec 상수 `CARD_BLURB`로 확정); `tests/helpers/component-state.js`(import만)
- tracked 허용(exact): `css/style.css`(`.featured-blurb`·`CARD_BLURB` 대상의 line clamp 비색 규칙과 BASE `.strength-card::before` 규칙 삭제만), `tests/specs/component-clamp.spec.js`(신규)
- runtime: R0
- 금지: §15.7, `index.html`, `js/*`, 색 선언, 그 밖 strength 규칙 변경, print 규칙(step 49), helper·기존 spec 수정

## 작업 (TDD)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step46` → `python3 -I tests/scripts/design-intake-check.py`
2. `component-clamp.spec.js`(6 project) 먼저 실패 확인(computed 값 읽기 전 대상에 `waitForFiniteAnimations`): `.featured-blurb` 3개와 `#projectGrid` 13개 카드의 `CARD_BLURB` computed `-webkit-line-clamp`가 `3`(tokens.blurbLineClamp); 각 textContent(norm) = 해당 `PROJECTS[i].blurb`(norm); 카드 0을 열었을 때 `.modal-blurb`의 `-webkit-line-clamp`가 `none`이고 텍스트 전문; `.strength-card` 6개 텍스트가 `STRENGTHS` 순서·내용과 같음(stripe 유무 무관).
3. style.css(guard 통과, stripe 삭제는 선택).

## AC

- `python3 -I tests/scripts/design-intake-check.py && sh tests/scripts/with-env.sh npm --prefix tests test -- component-clamp.spec.js component-hover.spec.js component-hit.spec.js css-parse.spec.js color-vocab.spec.js design-guard-color-rules.spec.js design-guard-color.spec.js design-guard-css.spec.js design-guard.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step46.json --allow css/style.css,tests/specs/component-clamp.spec.js --require-absent tests/specs/component-clamp.spec.js` → exit 0
