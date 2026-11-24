# Step 35 — axe-remediation-plan-schema

- 목적: §6.2 step 35, §6.5 `validateRemediationPlan(plan, baseline, { coverage = false, requireEmpty = false }) → string[]`(blocked·reason은 대응 fix의 text-change·`requiresColorChange`에서 도출).
- 20분(작성 12, 단독 2, FULL 4, VS·gate 2) / 선행 0~34 / 공통 §9 / gate GATE
- 허용(exact): `tests/helpers/axe.js`, `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 디렉터리)
- 추가 금지: 이전 helper 동작(`validateBaseline` 포함), 실제 fixtures

## 작업
1. `SNAP 35`
2. `GROUP_ID_RE`, `loadPlan`, `validateRemediationPlan`(§6.5 규칙·오류, `reason-mismatch` 포함), CLI `--check-plan [--coverage] [--require-empty] [--plan] [--baseline]`.
3. spec(step 33의 FIXTURE_OK·FIXTURE_THEMES·FIXTURE_RULE_PLAIN·FIXTURE_RULE_COLOR 상수, 먼저 모두 `validateBaseline` → `[]`):
   - FIXTURE_OK: §6.5 정상 예 + coverage → `[]`; 오류 예 2종 정확; id 통과 `color-token-1`·`a`·`x2`, 거부 `Group-1`·`a--b`·`-a`·`a-`·`a_b`·빈(`bad-id`); `plan: duplicate-id {id}`; `plan: groups unsorted`; PlanTarget 여분 → `fields missing=[] extra=[x]`; `unknown-target`; `targets duplicate`; `targets unsorted`; `plan: target-in-multiple-groups {key}|{target}`; fixFiles `["css/style.css"]` → `fixFiles-mismatch`; `bad-difficulty`; `bad-estMinutes`(0·21·1.5); `bad-blocked`; `blocked: false`·`reason: "x"` → `reason-must-be-empty`; `{ groups: [] }`+coverage → `plan: uncovered page:desktop-dark:aria-allowed-attr|aria-allowed-attr::#heroFeatured::대표 프로젝트`; requireEmpty 빈 통과·1개 `groups: expected empty, got 1`
   - FIXTURE_THEMES: themes 예(blocked false) → `["groups[0]: blocked-required"]`; blocked true·`color change excluded (HOO-81 §16.3)` → `[]`; blocked true·`reason: "x"` → `["groups[0]: reason-mismatch"]`
   - FIXTURE_RULE_PLAIN: `theme-toggle-size` 그룹 blocked false·`""` → `[]`
   - FIXTURE_RULE_COLOR: `career-kicker-rule` 그룹 blocked false·`""` → 정확히 `["groups[0]: blocked-required"]`; blocked true·`color change excluded (HOO-81 §16.3)` → `[]`
   - FIXTURE_MIXED(§6.5): reason `text change excluded; color change excluded (HOO-81 §16.3)`·blocked true → `[]`; reason `color change excluded (HOO-81 §16.3)` → `["groups[0]: reason-mismatch"]`; blocked false → `["groups[0]: blocked-required"]`
   - CLI: FIXTURE_OK·정상 0; 오류 1; THEMES blocked false 1; RULE_COLOR blocked false 1; RULE_PLAIN 0; `--require-empty` 0/1; plan 없음·JSON 오류 1

## AC
- `T axe-helper.spec.js && FULL && VS && GATE 35 tests/helpers/axe.js,tests/specs/axe-helper.spec.js`
