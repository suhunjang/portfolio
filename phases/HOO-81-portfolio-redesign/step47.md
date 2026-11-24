# Step 47 — state-sequence

- 목적: §11.2 `measureStateSequence`와 격리·실패 경로(사이트 불변).
- 18분 / 선행 0~46 / 공통 §9 / gate GATE
- 허용(exact): `tests/helpers/state-sequence.js`, `tests/specs/state-sequence.spec.js`(신규)
- runtime: R0
- 추가 금지: 사이트 파일, `component-state.js`·기존 spec, page 재사용, fixture·generator(48)

## 작업
1. `SNAP 47`
2. RED spec(`desktop-dark`·`desktop-light`, 나머지 skip; 테스트 `context`, url `/`; 각 test 정확히 `test.setTimeout(60000)`): 반환 6필드×3상태; 호출마다 `context.on('page')` 1회·pages 수 동일; 격리 (a) grid 0 → 1, 두 번째 `beforeMeasure`에서 `#projectModal` hidden·`modal-open` 없음; (b) `.hero-cta .btn` 0 뒤 `location.hash === ''`·`scrollY === 0`; (c) `beforeMeasure`에서 `page.setDefaultTimeout(500)` + 없는 selector → reject·pages 원복·이어 `.hero-cta .btn` 0 성공; (d) `beforeMeasure` throw → 같은 오류·pages 동일; (e) `page.setDefaultTimeout(500)` 후 pointerdown 제거 listener → reject·pages 원복(finally up·close)·이어 정상 측정 성공.
3. 구현 = §11.2 고정 절차.

## AC
- `T state-sequence.spec.js component-hit.spec.js && FULL && VS && GATE 47 tests/helpers/state-sequence.js,tests/specs/state-sequence.spec.js tests/helpers/state-sequence.js,tests/specs/state-sequence.spec.js`
