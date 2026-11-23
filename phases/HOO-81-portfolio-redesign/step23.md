# Step 23 — axe-collect

- 목적: axe.spec.js 10개 시나리오와 최초 수집. 종료 시 분류 대기(`pending`) 상태로 기본 testCommand가 통과한다.
- 예상 17분 / 선행 0~22 / 공통 절차 설계 §15
- read-first: 설계 §8.1, §8.3(분류 대기 baseline 계약, 실행 모드, COLLECT_CHAIN, step 23), §8.4
- tracked 허용(exact): `tests/specs/axe.spec.js`(신규), `tests/fixtures/axe-collected.json`
- runtime: R0(실제 COLLECT_DIR 포함)
- 금지: §15.7, helper, `axe-baseline.json`·plan 생성(step 24)

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step23`
2. `axe.spec.js`: 10개 시나리오, collector 고정 순서, `prepareForAxe` → `runAxe({ include: prep.include })`. 수집 모드 `writeCollected(scenario, testInfo.project.name, violations)`만. 일반 모드 `resolveBaselineMode()`; `check`면 checkRegression, validateBaseline(desktop-dark 1회), plan 있으면 validateRemediationPlan(coverage false); `pending`이면 준비 절차까지만 실행하고 `test.skip(true, 'axe classification pending (step 24)')`; throw면 실패.
3. COLLECT_CHAIN(기본 out `tests/fixtures/axe-collected.json`) 실행 후 entry 수·(key, target) 수·ruleId 분포를 로그로 남기고 모든 key = makeEntryKey 확인.
4. 기본 testCommand(환경변수 없음)를 실행해 axe.spec.js가 `pending` 경로로 준비 통과·판정 skip되는지 확인.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset && AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step23.json --allow tests/specs/axe.spec.js,tests/fixtures/axe-collected.json` → exit 0 (기본 testCommand가 환경변수 없이 통과)
