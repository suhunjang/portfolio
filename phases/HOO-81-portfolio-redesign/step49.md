# Step 49 — focus-trap-modal

- 목적: `trapFocus` 구현과 모달 연결.
- 예상 17분 / 선행 0~48 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §8.2(step 49); `openProjectModal`, `closeProjectModal`, `lastFocused`, lightbox 코드 위치(수정 금지)
- tracked 허용(exact): `js/main.js`(`trapFocus`와 모달 trap 연결만), `tests/specs/focus-modal.spec.js`(신규)
- runtime: R0
- 금지: §15.7, `index.html`, `js/data.js`, `css/*`, lightbox 코드

## 작업 (TDD)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step49`
2. spec(desktop-dark/light, mobile-dark) 먼저 실패 확인: 마지막→Tab→첫, 첫→Shift+Tab→마지막, 모달 밖으로 나가지 않음; button·backdrop·esc 닫기 후 트리거 복귀; `#heroFeatured`·`#projectGrid` 트리거 양쪽; 연속 2회 열고 닫아도 Tab 한 칸만 이동.
3. main.js(§8.2 계약).

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- focus-modal.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step49.json --allow js/main.js,tests/specs/focus-modal.spec.js` → exit 0
