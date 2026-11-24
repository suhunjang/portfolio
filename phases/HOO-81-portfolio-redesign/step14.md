# Step 14 — tests-browser-smoke

- 목적: 브라우저 설치, 테마 fixture와 콘솔 오류 수집 helper, 6 project smoke. §17 preflight에서 제거한 이전 untracked 파일은 참고하지 않고 새로 작성한다.
- 예상 15분 / 선행 0~13 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §3(테마), §11.4, §11.6, §17
- tracked 허용(exact): `tests/helpers/theme.js`, `tests/specs/smoke.spec.js`
- runtime: R0 + `tests/.pw-browsers/**`
- 금지: §15.7, §17 backup 파일 참조·복원

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step14` (시작 시 두 경로가 없어야 하며 require-absent로 검증)
2. `sh tests/scripts/with-env.sh npm --prefix tests run browsers:install`
3. `theme.js`: `THEME_KEY` null일 때만 주입하는 fixture, §11.4 `collectConsoleErrors`.
4. `smoke.spec.js`(6 project): collect → goto, heroName·테마 확인, finish 두 배열 `[]`, 비동기 throw 시 pageErrors 1건.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- smoke.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step14.json --allow tests/helpers/theme.js,tests/specs/smoke.spec.js --require-absent tests/helpers/theme.js,tests/specs/smoke.spec.js` → exit 0
