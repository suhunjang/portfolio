# Step 34 — axe-plan-executable

- 목적: blocked·text-change·빈 fixFiles 그룹에서 중단하는 실행 가능성 검사.
- 예상 15분 / 선행 0~33 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §7.2, §8.3(step 34, 재계획 조건), §8.6(FIXTURE_OK·FIXTURE_THEMES), §16.3
- tracked 허용(exact): `tests/helpers/axe.js`(추가만), `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 디렉터리)
- 금지: §15.7, 이전 helper 동작, 실제 fixtures

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step34`
2. `validateRemediationExecutable(plan, baseline)`, CLI `--check-executable`.
3. spec(desktop-dark, step 33의 FIXTURE_OK·FIXTURE_THEMES 상수 재사용): `{ groups: [] }` → `[]`; FIXTURE_OK + §8.6 정상 예 → `[]`; FIXTURE_THEMES + blocked true themes 그룹 → 정확히 `["blocked-group:career-kicker-contrast"]`; text-change fix 하나뿐인 합성 baseline + 그 그룹(blocked, fixFiles `[]`) → `blocked-group:{id}`·`text-change:{id}:{key}:{target}`·`empty-fixfiles:{id}`; 정상+blocked 혼합 → blocked 관련만; 입력 불변; CLI 빈 0·가능만 0·blocked 1(첫 줄 `Harness 재계획 필요: 실행 불가 remediation 그룹`)·plan 없음·baseline JSON 오류 1.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step34.json --allow tests/helpers/axe.js,tests/specs/axe-helper.spec.js` → exit 0
