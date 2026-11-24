# Step 41 — focus-trap-modal

- 목적: `trapFocus` 구현과 모달 연결.
- 예상 17분 / 선행 0~40 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §8.2(step 41)
- tracked 허용(exact): `js/main.js`(`trapFocus`와 모달 trap 연결만), `tests/specs/focus-modal.spec.js`(신규)
- runtime: R0
- 금지: §15.7, `index.html`, `js/data.js`, `css/*`, lightbox 코드

## 작업 (TDD)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step41`
2. spec(desktop-dark/light, mobile-dark) 먼저 실패 확인: 경계 순환, 이탈 없음, 세 닫기 경로 복귀, 두 트리거 영역, 반복 후 Tab 한 칸.
3. main.js.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- focus-modal.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step41.json --allow js/main.js,tests/specs/focus-modal.spec.js` → exit 0
