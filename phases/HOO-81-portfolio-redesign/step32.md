# Step 32 — axe-collect

- 목적: axe.spec.js 10개 시나리오와 최초 수집. 종료 시 `pending` 상태로 기본 testCommand 통과.
- 예상 17분 / 선행 0~31 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §8.1, §8.3(실행 모드, COLLECT_CHAIN, step 32), §8.4
- tracked 허용(exact): `tests/specs/axe.spec.js`(신규), `tests/fixtures/axe-collected.json`
- runtime: R0(실제 COLLECT_DIR)
- 금지: §15.7, helper, baseline·plan 생성

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step32`
2. `axe.spec.js`: 10개 시나리오, `prepareForAxe` → `runAxe`. 수집 모드 `writeCollected`만. 일반 모드 `resolveBaselineMode()`; `pending`이면 `test.skip(true, 'axe classification pending (step 33)')`.
3. COLLECT_CHAIN(기본 out) 후 entry 수·target 수·ruleId 분포 로그, 모든 key = makeEntryKey.
4. 기본 testCommand에서 `pending` 경로 확인.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset && AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step32.json --allow tests/specs/axe.spec.js,tests/fixtures/axe-collected.json` → exit 0
