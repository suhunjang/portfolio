# Color-resume Step 7 — a11y-collect-classify

- 존재 이유: wave 1 통합 뒤 최종 페이지를 기준으로 axe 정본을 수집·분류해 검증된 wave 2 manifest를 만든다. 대표 v52 색 결정은 guard exact 예외 상수 1개로 반영한다.
- 시간: agent 예상 ≤20분. 근거: 수집 1회, 기존 helper로 분류, 상수 1개와 회귀 테스트 1개, hover 제외 처리. Harness hard timeout은 30분.
- 선행: 0~6
- 공통 규칙: 원 §9 + §C1·§C9
- gate: `XGATE 7`
- 허용(exact):
  - `tests/helpers/design-guard-color-rules.js`: export 상수 `HOO81_COLOR_V52_ALLOW`와 그 적용 분기만
  - `tests/specs/design-guard-color-rules.spec.js`: 회귀 테스트 1개 추가만
  - `tests/specs/component-hover.spec.js`: 상수 import와 해당 항목의 BASE 비교 제외만
- runtime: R0 + `tests/.tmp/axe-final/**`, `tests/.tmp/a11y-wave/components.json`
- 추가 금지:
  - 사이트 파일, `css/themes.css`
  - 새 token, 리터럴 색
  - 새 policy 모듈·fixture
  - baseline·plan 작성
  - 이력 pairs·collected 수정
  - contrast·nested 밖 rule 수정

## 작업
1. `XSNAP 7` → `COLLECT_CHAIN --out tests/.tmp/axe-final/collected.json`
2. rule 확인. 밖이면 `a11y: out-of-scope-rule:{ruleId}`로 중단한다.
3. 기존 helper(`canonicalFromDescriptor`, resume §R5.1 실행 골격)로 다음을 만든다.
   - target별 owner anchor
   - color `to`와 6 project proof 파일(§C9 후보 규칙). 해결이 안 되면 `color-scope-themes-required:{target}`로 중단한다.
   - nested 계약
   - shard
   - `components.json`
4. `HOO81_COLOR_V52_ALLOW`에 color-declaration 투영만 넣는다.
5. guard 적용 분기와 회귀 테스트를 넣는다. 회귀 테스트는 세 가지를 확인한다.
   - 목록 밖 위치나 목록 위치의 다른 값은 여전히 위반이다.
   - `to`는 통과한다.
   - `[]`이면 기존 동작이다.
6. hover spec 제외 처리를 넣는다.

## AC
- `PW validate-manifest --collected tests/.tmp/axe-final/collected.json --manifest tests/.tmp/a11y-wave/components.json && T design-guard-color-rules.spec.js component-hover.spec.js GS && FULL && VS && XGATE 7 tests/helpers/design-guard-color-rules.js,tests/specs/design-guard-color-rules.spec.js,tests/specs/component-hover.spec.js`
- 이 시점 사이트 색은 BASE 그대로이므로 GS는 통과해야 한다.
- `COORD_WAVE2`는 이 step이 PASS한 뒤 `validate-manifest`를 다시 통과해야 시작할 수 있다.
