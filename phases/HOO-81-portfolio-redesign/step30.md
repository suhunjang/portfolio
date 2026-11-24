# Step 30 — axe-current-checks

- 목적: 현재 수집 결과 판정(group done, coverage, 위반 0).
- 예상 17분 / 선행 0~29 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §8.3(step 30)
- tracked 허용(exact): `tests/helpers/axe.js`(추가만), `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 디렉터리)
- 금지: §15.7, 이전 helper 동작, 실제 fixtures

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step30`
2. 설계 §8.3 step 30 계약 구현.
3. spec(desktop-dark): checkGroupDone done·remaining·무영향·unknown·형식 오류; checkCollectedCoverage ok·uncovered·입력 불변; countCollectedTargets; CLI group-done·coverage·assert-no-violations 각 0/1; baseline 잔존 target이 있으면 `--assert-no-violations` 1.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step30.json --allow tests/helpers/axe.js,tests/specs/axe-helper.spec.js` → exit 0
