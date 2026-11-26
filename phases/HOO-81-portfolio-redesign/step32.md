# Step 32 — axe-collect-tooling

- 목적: §6.2 step 32.
- 19분 / 선행 0~31 / 공통 §9 / gate GATE
- 허용(exact): `tests/helpers/axe.js`, `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(`tests/.tmp/axe-helper-test-*/`)
- 추가 금지: step 28 동작

## 작업
1. `SNAP 32`
2. spec(desktop-dark): makeEntryKey 형식·빈·`:` throw; 같은 ruleId 2·중복 target → entry 1 정렬; page desktop-dark/light → 2, page/modal → 2; resolveCollectDir 우선순위·`tests/.tmp` 밖 거부; reset; write 10·잘못된 scenario throw; merge 성공·9개 missing·여분 extra; CLI(`--dir`/`--out`) reset 0·merge 0·9개 1·`--dir tests/fixtures` 1; 실제 COLLECT_DIR·`tests/fixtures/axe-collected.json` 불변.

## AC
- `T axe-helper.spec.js && FULL && VS && GATE 32 tests/helpers/axe.js,tests/specs/axe-helper.spec.js`
