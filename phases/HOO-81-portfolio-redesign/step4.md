# Step 4 — axe-baseline

- 예상 시간: 12분
- 실행 횟수: 테스트 1회(웹서버 1회), verify-scope 1회
- 선행 step: 0~3 completed

## 공통: 시작 전 필수 확인 (read-first)

1. `README.md`를 읽는다. `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서 두 개를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` — §8
3. index.json에서 step 0~3이 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드를 확인한다.
   - 모달 DOM `#projectModal .modal-dialog[role=dialog]`
   - `ensureLightbox`
   - `tests/helpers/modal.js`의 API
5. `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`는 읽기 전용이다. 문서 변경은 하네스만 한다.
6. main 직접 변경, merge, deploy는 금지다.

## 허용 파일 (exact)

- `tests/specs/axe.spec.js`
- `tests/fixtures/axe-known.json`

## 수정 금지

- `tests/` 밖의 모든 파일
- 기존 tests 파일

## 작업

1. `tests/specs/axe.spec.js`를 작성한다. `@axe-core/playwright` AxeBuilder를 쓰고, tags는 wcag2a와 wcag2aa다.
   - page: 6개 project 전부. reducedMotion reduce context로 전체 페이지를 검사한다.
   - modal: desktop-dark와 desktop-light에서 Motion-O 모달을 열고 `#projectModal`을 include해 검사한다.
   - lightbox: desktop-dark와 desktop-light에서 lightbox를 열고 `.lightbox`를 include해 검사한다.
   - impact가 serious나 critical인 위반만 대상으로 한다.
   - 각 위반의 키는 `{scenario}:{project}:{ruleId}`다. 이 키가 `tests/fixtures/axe-known.json` 배열에 없으면 실패한다.
2. 첫 실행 결과로 `axe-known.json`을 채운다.
   - BASE에 이미 있는 위반만 기록한다. 빈 배열이어도 된다.
   - 이 목록은 step 7에서 `[]`로 비운다.

## 완료 기준 (AC)

`npm --prefix tests test && npm --prefix tests run verify-scope` → 통과
