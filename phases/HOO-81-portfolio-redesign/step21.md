# Step 21 — axe-prepare-modal

- 목적: 콘텐츠 로딩 검사(textLocator 계약)와 modal 준비.
- 예상 18분 / 선행 0~20 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §3(모달), §5, §7.4, §8.4(step 21, 오류 코드, 합성 fixture)
- tracked 허용(exact): `tests/helpers/axe-prepare.js`(추가만: `MODAL_ROOT`, `MODAL_BODY_TEXT`, `assertContentLoaded`, `prepareModal`), `tests/specs/axe-prepare-modal.spec.js`(신규)
- runtime: R0
- 금지: §15.7, modal.js·axe.js(import만), lightbox·prepareOverlay·prepareForAxe(step 22)

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step21`
2. 설계 §8.4 step 21 계약 구현.
3. spec(desktop-dark/light): 실제 사이트 `prepareModal(page)` → include·`modal-open`·제목 = `PROJECTS[0].title`·본문 텍스트 있음; 동작 fixture에서 `#heroFeatured` 대표 버튼과 grid 카드 `data-project="1"` 공존 → 성공·grid click 1·대표 0·`__opens === 1`; grid 밖 버튼만(`data-project="3"`) → `project-card-not-found:3`; handler 없는 fixture + 500ms → `modal-not-open`; 제목은 정상·`.modal-blurb` 빈 문자열·`.modal-section` 0개 → 제목 통과 후 `content-not-loaded:text`; `assertContentLoaded` 단위: 텍스트 없는 div + null 통과, 같은 div를 textLocator로 → text 실패.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-prepare-modal.spec.js axe-prepare-page.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step21.json --allow tests/helpers/axe-prepare.js,tests/specs/axe-prepare-modal.spec.js` → exit 0
