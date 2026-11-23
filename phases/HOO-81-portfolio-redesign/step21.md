# Step 21 — axe-collect

- 목적: axe.spec.js 10개 시나리오와 최초 수집.
- 예상 17분 / 선행 0~20 / 공통 절차 설계 §15
- read-first: 설계 §8.1, §8.3(실행 모드, COLLECT_CHAIN, step 21), §8.4
- tracked 허용(exact): `tests/specs/axe.spec.js`(신규), `tests/fixtures/axe-collected.json`
- runtime: R0(실제 COLLECT_DIR 포함)
- 금지: §15.7, helper, baseline·plan

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step21`
2. `axe.spec.js`: 10개 시나리오, collector 고정 순서, `prepareForAxe` → `runAxe({ include: prep.include })`. 수집 모드 `writeCollected(scenario, testInfo.project.name, violations)`만. 일반 모드 `resolveBaselineMode()`; check면 checkRegression, validateBaseline(desktop-dark 1회), plan 있으면 validateRemediationPlan(coverage false); skip이면 준비까지만 하고 axe 판정 `test.skip`.
3. COLLECT_CHAIN(기본 out) 실행 후 entry 수·(key, target) 수·ruleId 분포를 로그로 남기고 모든 key = makeEntryKey 확인.
4. 최초 일반 실행은 `AXE_ALLOW_MISSING_BASELINE=1`로만(옵션 없는 실행의 실패는 의도됨).

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset && AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge && AXE_ALLOW_MISSING_BASELINE=1 sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step21.json --allow tests/specs/axe.spec.js,tests/fixtures/axe-collected.json` → exit 0
