# Step 39 — axe-collect

- 목적: axe.spec.js 10개 시나리오·최초 수집, 종료 시 `pending`(§6.2 실행 모드).
- 17분 / 선행 0~38 / 공통 §9 / gate GATE
- 허용(exact): `tests/specs/axe.spec.js`(신규), `tests/fixtures/axe-collected.json`
- runtime: R0(실제 COLLECT_DIR)
- 추가 금지: helper, baseline·plan 생성

## 작업
1. `SNAP 39`
2. spec: `prepareForAxe` → `runAxe({ include })`; 수집 모드 `writeCollected(scenario, testInfo.project.name, violations)`만; 일반 모드 §6.2(pending이면 준비까지 후 `test.skip(true, 'axe classification pending (step 40)')`).
3. COLLECT_CHAIN 후 entry·target 수·ruleId 분포 로그, key = makeEntryKey 확인. `FULL` pending 경로 확인.

## AC
- `COLLECT_CHAIN && FULL && VS && GATE 39 tests/specs/axe.spec.js,tests/fixtures/axe-collected.json`
