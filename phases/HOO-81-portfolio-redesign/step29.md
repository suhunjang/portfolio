# Step 29 — axe-remediation-plan-schema

- 목적: §8.6 plan schema 검증(`validateRemediationPlan`, PlanTarget `{key, target}`).
- 예상 19분 / 선행 0~28 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §8.3(step 29), §8.5, §8.6(전체)
- tracked 허용(exact): `tests/helpers/axe.js`(추가만), `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 디렉터리)
- 금지: §15.7, 이전 helper 동작, 실제 fixtures

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step29`
2. `GROUP_ID_RE`, `loadPlan`, `validateRemediationPlan`(§8.6 규칙·오류 형식 그대로), CLI `--check-plan [--coverage] [--require-empty] [--plan] [--baseline]`.
3. spec(desktop-dark, §8.5 정상 baseline 기반): §8.6 정상 예 통과; 오류 예 2종 정확한 메시지; id 통과·거부 목록, duplicate-id, groups unsorted; targets 문자열·여분 필드·unknown-target·duplicate·unsorted·두 그룹 중복; fixFiles-mismatch; difficulty·estMinutes(0·21·1.5); blocked 비boolean; reason-required·reason-must-be-empty; text-change 또는 themes fixFiles인데 비blocked → blocked-required; coverage 누락 `plan: uncovered`; requireEmpty; CLI 정상 0·오류 1·`--require-empty` 0/1.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step29.json --allow tests/helpers/axe.js,tests/specs/axe-helper.spec.js` → exit 0
