# Step 33 — axe-remediation-plan-schema

- 목적: §8.6 plan schema 검증(`validateRemediationPlan`, PlanTarget `{key, target}`).
- 예상 19분 / 선행 0~32 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §8.3(step 33), §8.5, §8.6(전체, 특히 테스트 fixture FIXTURE_OK·FIXTURE_THEMES)
- tracked 허용(exact): `tests/helpers/axe.js`(추가만), `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 디렉터리)
- 금지: §15.7, 이전 helper 동작, 실제 fixtures

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step33`
2. `GROUP_ID_RE`, `loadPlan`, `validateRemediationPlan`(§8.6 규칙·오류 형식 그대로), CLI `--check-plan [--coverage] [--require-empty] [--plan] [--baseline]`.
3. spec(desktop-dark). spec 안 상수로 §8.6의 FIXTURE_OK와 FIXTURE_THEMES를 정확히 정의하고, 먼저 두 상수 모두 `validateBaseline` → `[]`임을 확인한다.
   - FIXTURE_OK 기준(정상 plan 검증 전용): §8.6 정상 예 → `validateRemediationPlan(plan, FIXTURE_OK, { coverage: true })` 정확히 `[]`(unknown-target 없음); 오류 예 2종 정확한 메시지(`groups[0].targets[0]: not-object`, `groups[0]: reason-required`); id 통과 `color-token-1`·`a`·`x2`, 거부 `Group-1`·`a--b`·`-a`·`a-`·`a_b`·빈 문자열(`bad-id`); 같은 id 두 그룹 → `plan: duplicate-id {id}`; id 역순 → `plan: groups unsorted`; PlanTarget 여분 필드 → `fields missing=[] extra=[x]`; baseline에 없는 target → `unknown-target`; 같은 PlanTarget 두 번 → `targets duplicate`; 역순 → `targets unsorted`; 두 그룹에 같은 PlanTarget → `plan: target-in-multiple-groups {key}|{target}`; fixFiles `["css/style.css"]` → `fixFiles-mismatch`; `bad-difficulty`; `bad-estMinutes`(0·21·1.5); `bad-blocked`; `blocked: false`·`reason: "x"` → `reason-must-be-empty`; `{ groups: [] }` + coverage → `plan: uncovered page:desktop-dark:aria-allowed-attr|aria-allowed-attr::#heroFeatured::대표 프로젝트`; requireEmpty 빈 통과·그룹 1개 `groups: expected empty, got 1`
   - FIXTURE_THEMES 기준(`css/themes.css` blocked 검증 전용): §8.6 themes 예(blocked false) → 정확히 `["groups[0]: blocked-required"]`; 같은 plan에 `blocked: true`, `reason: "color change excluded (HOO-81 §16.3)"` → `[]`
   - CLI: FIXTURE_OK·정상 plan 파일 → 0; 오류 plan → 1; FIXTURE_THEMES·blocked false plan → 1; `--require-empty` 빈 0·그룹 1개 1; plan 없음·JSON 오류 1

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step33.json --allow tests/helpers/axe.js,tests/specs/axe-helper.spec.js` → exit 0
