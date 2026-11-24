# Step 35 — axe-remediation-plan-schema

- 목적: §6.2 step 35, §6.5 `validateRemediationPlan`.
- 19분 / 선행 0~34 / 공통 §9 / gate GATE
- 허용(exact): `tests/helpers/axe.js`, `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 디렉터리)
- 추가 금지: 이전 helper 동작, 실제 fixtures

## 작업
1. `SNAP 35`
2. CLI `--check-plan [--coverage] [--require-empty] [--plan] [--baseline]`.
3. spec: FIXTURE_OK·FIXTURE_THEMES 상수(§6.5) 둘 다 `validateBaseline` → `[]`. FIXTURE_OK: 정상 예 + coverage → `[]`; 오류 예 2종 정확; id 통과 `color-token-1`·`a`·`x2`, 거부 `Group-1`·`a--b`·`-a`·`a-`·`a_b`·빈(`bad-id`); `plan: duplicate-id {id}`; `plan: groups unsorted`; PlanTarget 여분 → `fields missing=[] extra=[x]`; `unknown-target`; `targets duplicate`; `targets unsorted`; `plan: target-in-multiple-groups {key}|{target}`; fixFiles `["css/style.css"]` → `fixFiles-mismatch`; `bad-difficulty`; `bad-estMinutes`(0·21·1.5); `bad-blocked`; `reason-must-be-empty`; `{ groups: [] }`+coverage → `plan: uncovered page:desktop-dark:aria-allowed-attr|aria-allowed-attr::#heroFeatured::대표 프로젝트`; requireEmpty 빈 통과·1개 `groups: expected empty, got 1`. FIXTURE_THEMES: themes 예 → `["groups[0]: blocked-required"]`, blocked true+reason → `[]`. CLI: 정상 0, 오류 1, themes blocked false 1, `--require-empty` 0/1, plan 없음·JSON 오류 1.

## AC
- `T axe-helper.spec.js && FULL && VS && GATE 35 tests/helpers/axe.js,tests/specs/axe-helper.spec.js`
