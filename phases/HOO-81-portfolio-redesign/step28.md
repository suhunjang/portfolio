# Step 28 — axe-collect-tooling

- 목적: entry key와 수집 파일 관리.
- 예상 19분 / 선행 0~27 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §8.3(step 28), §8.5(MergedEntry 7필드)
- tracked 허용(exact): `tests/helpers/axe.js`(추가만), `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(`tests/.tmp/axe-helper-test-*/`)
- 금지: §15.7, step 24 동작

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step28`
2. 설계 §8.3 step 28 계약.
3. spec(desktop-dark): makeEntryKey 형식·빈 ruleId·`:` throw; 같은 ruleId 2개·중복 target → entry 1개 정렬; 같은 target이 page-desktop-dark/light → 2개, page/modal → 2개; resolveCollectDir 우선순위·`tests/.tmp` 밖 거부; reset; write 10개·잘못된 scenario throw; merge 성공·9개 missing·여분 extra; CLI(`--dir`/`--out`) reset 0·merge 0·9개 1·`--dir tests/fixtures` 1; 실제 COLLECT_DIR·`tests/fixtures/axe-collected.json` 불변.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step28.json --allow tests/helpers/axe.js,tests/specs/axe-helper.spec.js` → exit 0
