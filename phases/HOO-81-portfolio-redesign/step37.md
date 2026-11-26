# Step 37 — axe-current-checks

- 목적: §6.2 step 37.
- 17분 / 선행 0~36 / 공통 §9 / gate GATE
- 허용(exact): `tests/helpers/axe.js`, `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 디렉터리)
- 추가 금지: 이전 helper 동작, 실제 fixtures

## 작업
1. `SNAP 37`
2. remaining·uncovered 정렬 `{key, target}`, 비배열 collected `Error('invalid collected')`, 없는 id `Error('unknown group id: {id}')`.
3. spec: group done·`lightbox:desktop-dark:*`에만 남음 remaining 1·다른 그룹 무영향·unknown·형식 오류 id·`{}` throw; coverage ok·plan 밖 1 uncovered·빈 groups+잔여·입력 불변; countCollectedTargets `[]` 0·2+1 → 3·같은 target 두 entry → 2; CLI 각 0/1/없음 1; checkRegression `[]`이어도 잔여 있으면 `--assert-no-violations` 1.

## AC
- `T axe-helper.spec.js && FULL && VS && GATE 37 tests/helpers/axe.js,tests/specs/axe-helper.spec.js`
