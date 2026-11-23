# Step 21 — axe-plan-executable

- 목적: blocked·text-change·빈 fixFiles 그룹에서 중단하는 실행 가능성 검사.
- 예상 15분 / 선행 0~20 / 공통 절차 설계 §15
- read-first: 설계 §7.2, §8.3(step 21, gate, 재계획 생성 조건)
- tracked 허용(exact): `tests/helpers/axe.js`(추가만), `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 디렉터리)
- 금지: §15.7, step 13·17~20 동작, 실제 fixtures

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step21`
2. 설계 §8.3 step 21 계약 구현.
3. spec(desktop-dark): `{ groups: [] }` → `[]`; css-token 실행 가능 → `[]`; blocked css-rule → `blocked-group`; text-change 그룹(blocked, `[]`) → blocked-group·text-change·empty-fixfiles 모두; 정상+blocked 혼합 → blocked 오류만·길이 ≥ 1; 입력 불변; CLI 빈 0, 실행 가능만 0, blocked 1(첫 줄 `Harness 재계획 필요: 실행 불가 remediation 그룹`), fixFiles `[]` 1, plan 없음·baseline JSON 오류 1.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step21.json --allow tests/helpers/axe.js,tests/specs/axe-helper.spec.js` → exit 0
