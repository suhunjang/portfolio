# Step 31 — axe-current-checks

- 목적: 현재 수집 결과 판정(PlanTarget 단위 group done·coverage, 위반 0).
- 예상 17분 / 선행 0~30 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §8.3(step 31), §8.6
- tracked 허용(exact): `tests/helpers/axe.js`(추가만), `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 디렉터리)
- 금지: §15.7, 이전 helper 동작, 실제 fixtures

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step31`
2. 설계 §8.3 step 31 계약(remaining·uncovered는 `{key, target}` 정렬 배열).
3. spec(desktop-dark): checkGroupDone done·remaining 정확한 PlanTarget·무영향·unknown·invalid collected; coverage ok·uncovered·입력 불변; countCollectedTargets; CLI 각 0/1; baseline 잔존 target이 수집에 있으면 `--assert-no-violations` 1.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step31.json --allow tests/helpers/axe.js,tests/specs/axe-helper.spec.js` → exit 0
