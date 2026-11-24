# Step 23 — axe-prepare-modal

- 목적: 콘텐츠 로딩 검사(textLocator 계약)와 modal 준비.
- 예상 18분 / 선행 0~22 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §3(모달), §5, §7.4, §8.4(step 23, 합성 fixture)
- tracked 허용(exact): `tests/helpers/axe-prepare.js`(추가만: `MODAL_ROOT`, `MODAL_BODY_TEXT`, `assertContentLoaded`, `prepareModal`), `tests/specs/axe-prepare-modal.spec.js`(신규)
- runtime: R0
- 금지: §15.7, modal.js·axe.js(import만), step 24 범위

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step23`
2. 설계 §8.4 step 23 계약 구현.
3. spec(desktop-dark/light): 실제 사이트 `prepareModal(page)` → include·`modal-open`·제목 = `PROJECTS[0].title`·본문 있음; 동작 fixture에서 대표 버튼과 grid 카드 `data-project="1"` 공존 → grid click 1·대표 0·`__opens === 1`; grid 밖 버튼만 → `project-card-not-found:3`; handler 없음 + 500ms → `modal-not-open`; 본문 빈 모달 → `content-not-loaded:text`; `assertContentLoaded` textLocator null/지정 단위.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-prepare-modal.spec.js axe-prepare-page.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step23.json --allow tests/helpers/axe-prepare.js,tests/specs/axe-prepare-modal.spec.js` → exit 0
