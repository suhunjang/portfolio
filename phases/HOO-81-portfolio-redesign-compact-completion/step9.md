# Compact Step 9 — contrast-nested

- 목적: 현재 DOM에서 확인된 color-contrast와 nested-interactive를 기존 token과 기존 DOM 경로로 직접 고친다. 색 예외는 선언 단위로만 둔다.
- 예상 16분, hard timeout 30분. 선행: step 8. 공통 선행조건 §C0.
- 허용 파일(exact): `css/style.css`, `js/main.js`, `tests/helpers/design-guard-color-rules.js`, `tests/specs/design-guard-color-rules.spec.js`
- runtime: §C4
- 금지: 새 token, 리터럴 색, palette 변경, `css/themes.css`, 범용 mapper, 승인된 spec 수정

## 작업
1. `AXE0` 1~4단계를 실행한다. color-contrast와 nested-interactive가 아닌 rule이 나오면 그 rule을 blocker로 보고하고 중단한다.
2. color-contrast를 고친다.
   - target의 `css/style.css` 기존 선언만 기존 token `var(--x)`로 바꾼다.
   - token 선택 기준:
     - 영향받는 모든 theme와 state에서 대비가 4.5 이상인 후보만 본다.
     - 그중 sRGB 제곱거리 합이 가장 작은 것을 고른다.
     - 같으면 token 이름의 code-unit 순서로 정한다.
   - 후보가 없으면 `color-scope-themes-required`로 중단한다.
3. nested-interactive를 고친다.
   - `js/main.js` project-card 렌더의 중첩 구조만 바꾼다.
   - card click 위임, 키보드 진입, trigger 복귀는 유지한다.
4. `HOO81_COLOR_V52_ALLOW`를 작성한다(§C6).
   - 바꾼 선언마다 항목 하나를 정렬해서 넣는다.
   - guard에는 선언 단위 예외 분기만 추가한다.
5. `design-guard-color-rules.spec.js`에 회귀를 추가한다.
   - 통과해야 하는 경우: 지정 선언의 `to`, 상수가 `[]`이면 기존 동작.
   - 계속 실패해야 하는 경우:
     - chain이 다른 같은 selector
     - 같은 chain·selector의 다른 occurrence
     - 같은 rule의 다른 선언 변경
     - 지정 선언이 `to`가 아닌 값

## AC
- `T <GS>`
- `DI`
- `T specs/featured.spec.js specs/focus-modal.spec.js specs/modal-regression.spec.js`
- `AXE0`
