# Step 35 — axe-finalize

- 목적: 위반 0 전제 확인 후 baseline을 `[]`로 확정.
- 예상 16분 / 선행 0~34 / 공통 절차 설계 §15
- read-first: 설계 §8.3(REGRESSION_GATE, step 35)
- tracked 허용(exact): `tests/fixtures/axe-baseline.json`(`[]`로 바꾸는 것만)
- runtime: R0
- 금지: §15.7, 사이트 파일, helper·spec·다른 fixture

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step35`
2. 전제(실패 시 baseline 불변으로 중단): `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset && AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge --out tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-regression --collected tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-plan --require-empty && sh tests/scripts/with-env.sh node tests/helpers/axe.js --assert-no-violations --collected tests/.tmp/axe-current.json`
3. baseline을 `[]`로 바꾸고 일반 axe 전체 실행. 실패하면 되돌리지 않고 보고·재계획.

## AC

- 작업 2 전제가 exit 0
- `sh tests/scripts/with-env.sh node tests/helpers/axe.js --assert-empty && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step35.json --allow tests/fixtures/axe-baseline.json` → exit 0
