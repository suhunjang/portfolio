# Step 30 — axe-prepare-modal

- 목적: §6.3 step 30.
- 18분 / 선행 0~29 / 공통 §9 / gate GATE
- 허용(exact): `tests/helpers/axe-prepare.js`(추가만: `MODAL_ROOT`, `MODAL_BODY_TEXT`, `assertContentLoaded`, `prepareModal`), `tests/specs/axe-prepare-modal.spec.js`(신규)
- runtime: R0
- 추가 금지: modal.js·axe.js(import만), step 29 동작

## 작업
1. `SNAP 30`
2. spec(desktop-dark/light): `prepareModal(page)` → include `#projectModal`·`modal-open`·제목 `PROJECTS[0].title`·본문; 동작 fixture에서 대표 버튼과 grid `data-project="1"` 공존 → grid click 1·대표 0·`__opens === 1`; grid 밖만(`data-project="3"`) → `project-card-not-found:3`; handler 없음 + 500ms → `modal-not-open`; `.modal-blurb` 빈·`.modal-section` 0 → `content-not-loaded:text`; 텍스트 없는 div + null 통과, textLocator 지정 시 text 실패.

## AC
- `T axe-prepare-modal.spec.js axe-prepare-page.spec.js && FULL && VS && GATE 30 tests/helpers/axe-prepare.js,tests/specs/axe-prepare-modal.spec.js`
