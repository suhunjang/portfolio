# Color-resume Step 2 — a11y-collect-classify

- 존재 이유: wave 1 통합 뒤 최종 페이지 기준 axe 정본을 다시 수집·분류해 wave 2 shard 입력을 만들고, 대표 v52 색 결정을 design guard의 exact 예외 1개로 반영한다.
- ≤30분 / 선행 0~1 / 공통 원 §9 + §C1·§C7 / gate `XGATE 2`
- 허용(exact): `tests/helpers/design-guard-color-rules.js`(상수 `HOO81_COLOR_V52_ALLOW`와 그 적용 분기만), `tests/specs/design-guard-color-rules.spec.js`(회귀 1개 추가만), `tests/specs/component-hover.spec.js`(상수 import와 해당 항목 BASE 비교 제외만)
- runtime: R0 + `tests/.tmp/axe-final/**`, `tests/.tmp/a11y-wave/components.json`
- 추가 금지: 사이트 파일(`index.html`·`css/*`·`js/*`) 수정, `css/themes.css`, 새 token·리터럴 색, 새 policy 모듈·fixture, baseline·plan 작성, 이력 pairs·collected 수정, contrast·nested 밖 rule 수정

## 작업
1. `XSNAP 2` → `COLLECT_CHAIN --out tests/.tmp/axe-final/collected.json`.
2. rule 집합 ⊆ {color-contrast, nested-interactive} 확인(아니면 `a11y: out-of-scope-rule:{ruleId}` 중단·보고). 위반 0이면 manifest `shards: []` 기록 후 작업 4로.
3. 기존 helper(`canonicalFromDescriptor`, resume §R5.1 실행 골격, `PW_PORT` 기본)로 target별 edit anchor 결정, color target은 §C7 후보 규칙으로 `to` 결정(해결 불가면 `color-scope-themes-required:{target}` 중단). anchor 연결 성분 → shard(최대 5) → `tests/.tmp/a11y-wave/components.json`(§C7 스키마).
4. `HOO81_COLOR_V52_ALLOW` = manifest 모든 `changes` 정렬(없으면 `[]`), guard 적용 분기·회귀 spec·`component-hover.spec.js` 제외 처리(§C7).

## AC
- `T design-guard-color-rules.spec.js component-hover.spec.js GS && FULL && VS && XGATE 2 tests/helpers/design-guard-color-rules.js,tests/specs/design-guard-color-rules.spec.js,tests/specs/component-hover.spec.js`(GS는 현재 사이트 색이 BASE 그대로이므로 통과)
