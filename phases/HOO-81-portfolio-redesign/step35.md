# Step 35 — axe-current-checks

- 목적: 현재 수집 결과 판정(PlanTarget 단위 group done·coverage, 위반 0).
- 예상 17분 / 선행 0~34 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §8.3(step 35), §8.6
- tracked 허용(exact): `tests/helpers/axe.js`(추가만), `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 디렉터리)
- 금지: §15.7, 이전 helper 동작, 실제 fixtures

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step35`
2. 설계 §8.3 step 35 계약(remaining·uncovered는 정렬된 `{key, target}` 배열, 비배열 collected `Error('invalid collected')`, 없는 id `Error('unknown group id: {id}')`).
3. spec(desktop-dark): checkGroupDone 사라짐 done·`lightbox:desktop-dark:*`에만 남음 remaining 1(정확한 PlanTarget)·다른 그룹 잔여 무영향·unknown·형식 오류 id·`{}` collected throw; coverage 전부 포함 ok·plan 밖 1개 uncovered·빈 groups+잔여·입력 불변; countCollectedTargets `[]` 0·2+1 → 3·같은 target 두 entry → 2; CLI group-done·coverage·assert-no-violations 각 0/1/없음 1; baseline과 수집에 같은 target이 남으면 checkRegression `[]`이어도 `--assert-no-violations` 1.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step35.json --allow tests/helpers/axe.js,tests/specs/axe-helper.spec.js` → exit 0
