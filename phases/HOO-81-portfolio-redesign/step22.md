# Step 22 — axe-current-checks

- 목적: 현재 수집 결과 판정(group done, coverage, 위반 0).
- 예상 17분 / 선행 0~21 / 공통 절차 설계 §15
- read-first: 설계 §8.3(entry key, step 22, gate·recheck·finalize·재계획 계약)
- tracked 허용(exact): `tests/helpers/axe.js`(추가만), `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 디렉터리)
- 금지: §15.7, step 13·17~21 동작, 실제 fixtures

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step22`
2. 설계 §8.3 step 22 계약 구현.
3. spec(desktop-dark): checkGroupDone 사라짐 done, lightbox에만 남음 remaining 1(`lightbox:desktop-*:*`), 다른 그룹 잔여 무영향, unknown·형식 오류 id throw, collected `{}` throw; checkCollectedCoverage 전부 포함 ok, plan 밖 1개 uncovered, 빈 groups + 잔여 uncovered, 입력 불변; countCollectedTargets `[]` 0, 2+1 → 3, 같은 target 두 entry → 2; CLI group-done done 0·remaining 1·unknown 1·없음 1, coverage 포함 0·잔여 1·없음 1, assert-no-violations `[]` 0·1개 1·없음 1; baseline과 수집에 같은 target이 남으면 checkRegression `[]`이어도 `--assert-no-violations` 1.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step22.json --allow tests/helpers/axe.js,tests/specs/axe-helper.spec.js` → exit 0
