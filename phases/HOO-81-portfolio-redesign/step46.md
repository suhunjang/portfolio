# Step 46 — state-sequence

- 목적: 상태 순서 측정 helper `measureStateSequence`(대상마다 새 page, finally `mouse.up()`·`page.close()`)와 격리·실패 경로 테스트. 사이트 파일은 바꾸지 않는다.
- 예상 18분 / 선행 0~45 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §3(모달·`modal-open`·CTA), §16.2(step 46 상태 순서 측정 helper·격리·실패 회귀); `tests/helpers/component-state.js`(import만)
- tracked 허용(exact): `tests/helpers/state-sequence.js`(신규), `tests/specs/state-sequence.spec.js`(신규)
- runtime: R0
- 금지: §15.7, 사이트 파일, `component-state.js`·기존 spec 수정, 여러 대상에 한 page 재사용, BASE fixture·generator(step 47 몫)

## 작업 (TDD)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step46`
2. `state-sequence.spec.js`(`desktop-dark`·`desktop-light`만, 나머지 `test.skip`; 테스트 `context`와 url `/` 사용; spec 전체 각 test에 정확히 `test.setTimeout(60000)`) 먼저 실패 확인:
   - 반환 형태: `.hero-cta .btn` nth 0 → `{ default, hover, active }` 각각 정확히 `color, backgroundColor, borderColor, outlineColor, transform, opacity` 6필드
   - page 수: 호출마다 `context.on('page')` 이벤트 정확히 1회, 호출 전후 `context.pages().length` 동일
   - 격리 (a): `#projectGrid .project-card[data-project="0"]` 순서 측정 직후 `[data-project="1"]` 순서 측정이 완료되고, 두 번째 호출의 `beforeMeasure`에서 `#projectModal`이 hidden·body에 `modal-open` 없음
   - 격리 (b): `.hero-cta .btn` nth 0 순서 측정 직후 다음 대상 호출의 `beforeMeasure`에서 `location.hash === ''`·`scrollY === 0`
   - 실패 경로 (c): `beforeMeasure`에서 `page.setDefaultTimeout(500)`을 설정하고 존재하지 않는 selector로 호출 → reject; 그 뒤 `context.pages().length`가 호출 전과 같음; 이어서 같은 context로 `.hero-cta .btn` nth 0 정상 측정이 성공
   - 실패 경로 (d): `beforeMeasure`가 throw → 같은 오류로 reject, `context.pages().length` 동일
   - 실패 경로 (e): `beforeMeasure`에서 `page.setDefaultTimeout(500)`을 설정한 뒤 대상에 `pointerdown` 시 요소를 제거하는 listener를 등록 → active 측정이 실패해 reject; 그 뒤 `context.pages().length`가 호출 전과 같음(finally에서 `mouse.up()`과 `page.close()` 수행); 이어서 같은 context로 `.hero-cta .btn` nth 0 정상 측정이 성공
3. `state-sequence.js`: 설계 §16.2 고정 절차 그대로 — 대상마다 `context.newPage()` → `goto(url)` → `document.fonts.ready` → `beforeMeasure(page)` → `scrollIntoViewIfNeeded()` → `waitForFiniteAnimations` → `mouse.move(0, 0)` 후 default → `locator.hover()` 후 hover → `mouse.down()` 직후 active → finally에서 down이 실행됐으면 `mouse.up()`, 그다음 항상 `page.close()`. 상태 값은 `measureState` 결과의 6필드.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- state-sequence.spec.js component-hit.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step46.json --allow tests/helpers/state-sequence.js,tests/specs/state-sequence.spec.js --require-absent tests/helpers/state-sequence.js,tests/specs/state-sequence.spec.js` → exit 0 (첫 명령에 실패 경로 (c)·(e) 각각의 reject 뒤 page 수 원복과 다음 정상 측정 성공 포함)
