# Step 21 — tests-browser-smoke

- 목적: 브라우저 설치, 테마 fixture·콘솔 수집 helper, 6 project smoke(§12 제거 파일은 새로 작성).
- 15분 / 선행 0~20 / 공통 §9 / gate GATE
- 허용(exact): `tests/helpers/theme.js`, `tests/specs/smoke.spec.js`
- runtime: R0 + `tests/.pw-browsers/**`
- 추가 금지: §12 backup 참조·복원

## 작업
1. `SNAP 21` → `W npm --prefix tests run browsers:install`.
2. `theme.js`: `THEME_KEY` null일 때만 주입, §8.3 `collectConsoleErrors`. spec(6 project): goto, heroName·테마, finish 두 배열 `[]`, 비동기 throw 시 pageErrors 1건.

## AC
- `T smoke.spec.js && FULL && GATE 21 tests/helpers/theme.js,tests/specs/smoke.spec.js tests/helpers/theme.js,tests/specs/smoke.spec.js`
