# Step 6: state-sequence

## Always-on invariants
Do not modify historical phase records/evidence. Preserve all copy, numbers, font assets/weights, information architecture, 3 featured project identities, all 13 PROJECTS and order. No new copy, section, image, icon, project or placeholder content. css/themes.css is read-only; if it or index.html is required outside the listed lane, stop and replan. Implementation workers must not commit, push, merge, edit the canonical phase index, or write outside their exact lane files. Run only focused tests in lanes; canonical FULL/UI/a11y run at steps 12 and 14.

## Exact work order
### Bound historical contract: `phases/HOO-81-portfolio-redesign-resume/step24.md`
SHA-256 `628ce602b7be6eb93b1e1a3ada5e519839cbc7bb69974343c1254cfa9b9923d4`

# Resume Step 24 — state-sequence (원 step 47, §R10 분기)

- 목적: 원 §11.2 `measureStateSequence`와 격리·실패 경로(사이트 불변). 테마는 전달된 context의 §THEME init script 상속.
- 18분 / 선행 0~23 / 공통 원 §9 + §R1·§R10 / gate `RGATE_B 24`
- 허용(exact): `tests/helpers/state-sequence.js`, `tests/specs/state-sequence.spec.js`(신규)
- 분기 R: `tests/helpers/state-sequence.js,tests/specs/state-sequence.spec.js`
- runtime: R0
- 추가 금지: 사이트 파일, `component-state.js`·`theme.js`·기존 spec, page 재사용, helper 안 테마 주입, fixture·generator(resume 25), start snapshot 수정·재생성, existing 분기에서 R 파일 수정

## 작업
1. `RSNAP 24` → `RBRANCH 24 tests/helpers/state-sequence.js,tests/specs/state-sequence.spec.js`.
   - `existing`: 작업 2~3 생략, 쓰기 없는 AC 전체 실행 → 통과 시 `resume step24: no-op`, 실패 시 tracked 불변 중단·재계획.
   - `new`: 아래 진행. `branch-mixed`면 중단.
2. RED spec(`desktop-dark`·`desktop-light`, 나머지 skip; §THEME `test`의 `context`, url `/`; 각 test 정확히 `test.setTimeout(60000)`): 반환 6필드×3상태; 호출마다 `context.on('page')` 1회·pages 수 동일; 측정 page `html[data-theme]` = project suffix; 격리 (a) grid 0 → 1, 두 번째 `beforeMeasure`에서 `#projectModal` hidden·`modal-open` 없음; (b) `.hero-cta .btn` 0 뒤 `location.hash === ''`·`scrollY === 0`; (c) `beforeMeasure`에서 `page.setDefaultTimeout(500)` + 없는 selector → reject·pages 원복·이어 정상 측정 성공; (d) `beforeMeasure` throw → 같은 오류·pages 동일; (e) `page.setDefaultTimeout(500)` 후 pointerdown 제거 listener → reject·pages 원복·이어 정상 측정 성공.
3. 구현 = 원 §11.2 고정 절차.

## AC
- `T state-sequence.spec.js component-hit.spec.js && FULL && VS && RGATE_B 24 tests/helpers/state-sequence.js,tests/specs/state-sequence.spec.js tests/helpers/state-sequence.js,tests/specs/state-sequence.spec.js`


Create the deterministic state sequence helper/spec only after component-hit fan-in. No product source writes.

## Exact write boundary
state-sequence: tests/helpers/state-sequence.js, tests/specs/state-sequence.spec.js

## Acceptance
Run every argv in this step’s immutable `index.json.acceptanceCommands` in order. Any nonzero exit blocks the next step.
