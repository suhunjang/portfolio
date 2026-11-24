# Step 25 — axe-collect-tooling

- 목적: entry key와 수집 파일 관리(reset/write/merge).
- 예상 19분 / 선행 0~24 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §8.3(entry key, step 25, COLLECT_CHAIN)
- tracked 허용(exact): `tests/helpers/axe.js`(추가만), `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(`tests/.tmp/axe-helper-test-*/` 독립 디렉터리만)
- 금지: §15.7, step 21 동작

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step25`
2. 설계 §8.3 step 25 계약 구현.
3. spec(desktop-dark): makeEntryKey 형식·throw; entry 병합·정렬; scenario/project별 entry 분리; resolveCollectDir 우선순위·거부; reset; write 10개·잘못된 scenario throw; merge 성공·missing·extra; CLI reset 0, merge 0, 9개 1, `--dir tests/fixtures` 1; 실제 COLLECT_DIR과 `tests/fixtures/axe-collected.json` 불변.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step25.json --allow tests/helpers/axe.js,tests/specs/axe-helper.spec.js` → exit 0
