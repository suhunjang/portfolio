# Step 33 — axe-collect

- 목적: axe.spec.js 10개 시나리오와 최초 수집. 종료 시 `pending`.
- 예상 17분 / 선행 0~32 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §8.1, §8.3, §8.4
- tracked 허용(exact): `tests/specs/axe.spec.js`(신규), `tests/fixtures/axe-collected.json`
- runtime: R0(실제 COLLECT_DIR)
- 금지: §15.7, helper, baseline·plan 생성

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step33`
2. `axe.spec.js`: 10개 시나리오; 수집 모드 `writeCollected`; 일반 모드 `resolveBaselineMode()`, `pending`이면 `test.skip(true, 'axe classification pending (step 34)')`.
3. COLLECT_CHAIN(기본 out) 후 분포 로그, key 확인.
4. 기본 testCommand `pending` 경로 확인.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset && AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step33.json --allow tests/specs/axe.spec.js,tests/fixtures/axe-collected.json` → exit 0
