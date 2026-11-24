# Step 26 — axe-collect-tooling

- 목적: entry key와 수집 파일 관리.
- 예상 19분 / 선행 0~25 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §8.3(step 26), §8.5(MergedEntry 7필드)
- tracked 허용(exact): `tests/helpers/axe.js`(추가만), `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(`tests/.tmp/axe-helper-test-*/`)
- 금지: §15.7, step 22 동작

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step26`
2. 설계 §8.3 step 26 계약.
3. spec(desktop-dark): makeEntryKey; entry 병합·정렬; scenario/project 분리; resolveCollectDir; reset; write; merge 성공·missing·extra; CLI 4사례; 실제 COLLECT_DIR·`axe-collected.json` 불변.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step26.json --allow tests/helpers/axe.js,tests/specs/axe-helper.spec.js` → exit 0
