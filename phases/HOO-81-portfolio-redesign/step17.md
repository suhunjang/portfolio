# Step 17 — axe-collect-tooling

- 목적: entry key와 수집 파일 관리(reset/write/merge).
- 예상 19분 / 선행 0~16 / 공통 절차 설계 §15
- read-first: 설계 §8.3(entry key, step 17, COLLECT_CHAIN)
- tracked 허용(exact): `tests/helpers/axe.js`(추가만), `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(테스트는 `tests/.tmp/axe-helper-test-*/` 독립 디렉터리만, 실제 COLLECT_DIR에 쓰지 않음)
- 금지: §15.7, step 13 동작

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step17`
2. 설계 §8.3 step 17 계약 구현.
3. spec(desktop-dark): makeEntryKey 형식·빈 ruleId·`:` 포함 throw; 같은 ruleId 2개·중복 target → entry 1개 정렬; 같은 target이 page-desktop-dark/light → entry 2개, page/modal → 2개; 모든 key = makeEntryKey; resolveCollectDir 우선순위·`tests/.tmp` 밖 거부; reset 후 비어 있음; write 10개·잘못된 scenario throw; merge 10개 성공·9개 missing·여분 extra; CLI(`--dir`/`--out` 지정) reset 0, merge 0, 9개 1, `--dir tests/fixtures` 1; 실행 전후 실제 COLLECT_DIR(존재·목록·크기·mtime)과 `tests/fixtures/axe-collected.json` 불변.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step17.json --allow tests/helpers/axe.js,tests/specs/axe-helper.spec.js` → exit 0
