# Step 29 — focus-trap-modal

- 목적: `trapFocus` 구현과 모달 연결.
- 예상 17분 / 선행 0~28 / 공통 절차 설계 §15
- read-first: 설계 §8.2(step 29); `openProjectModal`, `closeProjectModal`, `lastFocused`, 모달 포커스 요소, lightbox 코드 위치(수정 금지)
- tracked 허용(exact): `js/main.js`(`trapFocus` 추가와 모달 열기·닫기 trap 연결만), `tests/specs/focus-modal.spec.js`(신규)
- runtime: R0
- 금지: §15.7, `index.html`, `js/data.js`, `css/*`, lightbox 관련 코드

## 작업 (TDD)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step29`
2. spec(desktop-dark/light, mobile-dark) 먼저 실패 확인: 마지막→Tab→첫, 첫→Shift+Tab→마지막, 모달 밖으로 나가지 않음; button·backdrop·esc 닫기 후 트리거 복귀; `#heroFeatured`·`#projectGrid` 트리거 양쪽; 연속 2회 열고 닫아도 Tab 한 칸만 이동.
3. main.js: §8.2 계약 그대로, 열 때 push(trigger)·닫을 때 release.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- focus-modal.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step29.json --allow js/main.js,tests/specs/focus-modal.spec.js` → exit 0
