# Step 12 — tests-browser-smoke

- 목적: 브라우저 설치, 테마 fixture와 콘솔 오류 수집 helper, 6 project smoke. 이 step부터 종료 gate는 CLI다(첫 CLI 종료 gate).
- 예상 15분 / 선행 0~11 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §3(테마), §11.4, §11.6, §11.7
- tracked 허용(exact): `tests/helpers/theme.js`, `tests/specs/smoke.spec.js`
- runtime: R0 + `tests/.pw-browsers/**`
- 금지: §15.7

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step12`
2. `sh tests/scripts/with-env.sh npm --prefix tests run browsers:install`
3. `theme.js`: `THEME_KEY` null일 때만 주입하는 fixture, §11.4 `collectConsoleErrors`.
4. `smoke.spec.js`(6 project): collect → goto, heroName·테마 확인, finish 두 배열 `[]`, 비동기 throw 시 pageErrors 1건.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- smoke.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step12.json --allow tests/helpers/theme.js,tests/specs/smoke.spec.js --require-absent tests/helpers/theme.js,tests/specs/smoke.spec.js` → exit 0 (마지막 명령이 첫 CLI 종료 gate: projectRoot 유형 → 경로 유형 → schema(저장소 상대 경로 계약 포함) → 현재 identity → 상태 수집(unsafe면 after.z 미접촉 exit 1) → after.z 안전 쓰기 → 판정)
