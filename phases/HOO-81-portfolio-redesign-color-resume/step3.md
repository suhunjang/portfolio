# Color-resume Step 3 — a11y-collect-classify

- 존재 이유: wave 1 통합 뒤 최종 페이지를 기준으로 axe를 다시 수집해 정본을 만든다. 그 결과로 검증된 wave 2 manifest를 만들고, 대표 v52 색 결정을 guard 예외 상수 1개로 반영한다.
- 시간: agent 예상 ≤20분, Harness hard timeout 30분. 선행 0~2. 공통 규칙: 원 §9 + §C1·§C7. gate: `XGATE 3`.
- 허용(exact):
  - `tests/helpers/design-guard-color-rules.js`: export 상수 `HOO81_COLOR_V52_ALLOW`와 그 적용 분기만
  - `tests/specs/design-guard-color-rules.spec.js`: 회귀 테스트 1개 추가만
  - `tests/specs/component-hover.spec.js`: 상수 import와 해당 항목의 BASE 비교 제외만
- runtime: R0 + `tests/.tmp/axe-final/**`, `tests/.tmp/a11y-wave/components.json`
- 추가 금지: 사이트 파일 수정, `css/themes.css`, 새 token·리터럴 색, 새 policy 모듈·fixture, baseline·plan 작성, 이력 pairs·collected 수정, contrast·nested 밖 rule 수정

## 작업
1. `XSNAP 3` → `COLLECT_CHAIN --out tests/.tmp/axe-final/collected.json`
2. rule 집합이 {color-contrast, nested-interactive} 안인지 확인한다. 밖이면 `a11y: out-of-scope-rule:{ruleId}`로 중단한다.
3. 기존 helper(`canonicalFromDescriptor`, resume §R5.1 실행 골격)로 다음을 만든다.
   - target별 edit anchor
   - color `to`(§C7 후보 규칙). 해결할 수 없으면 `color-scope-themes-required:{target}`로 중단한다.
   - nested 구조·interaction 계약
   - shard
   - `components.json`(§C7)
4. `HOO81_COLOR_V52_ALLOW`에 color-declaration만 투영한다. 이어서 guard 적용 분기, 회귀 테스트(목록 밖 위치나 목록 위치의 다른 값은 위반, `to`는 통과, 상수가 `[]`이면 기존 동작 그대로), hover spec 제외 처리를 넣는다.
5. `PW validate-manifest`를 실행한다. coordinator가 wave 2 `prepare`를 시작하려면 이 검증을 통과해야 한다.

## AC
- `PW validate-manifest --collected tests/.tmp/axe-final/collected.json --manifest tests/.tmp/a11y-wave/components.json && T design-guard-color-rules.spec.js component-hover.spec.js GS && FULL && VS && XGATE 3 tests/helpers/design-guard-color-rules.js,tests/specs/design-guard-color-rules.spec.js,tests/specs/component-hover.spec.js`
- 이 시점 사이트 색은 BASE 그대로이므로 GS는 통과해야 한다.
