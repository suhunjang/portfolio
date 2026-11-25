# Compact Step 9 — contrast-nested

- 목적: 현재 DOM에서 확인된 color-contrast와 nested-interactive를 기존 token과 기존 DOM 경로로 직접 고친다. 색 예외는 선언 하나 단위로만 둔다.
- 예상 16분, hard timeout 30분. 선행: step 8. 공통 선행조건: §C0.
- 허용 파일(exact): `css/style.css`, `js/main.js`, `tests/helpers/design-guard-color-rules.js`, `tests/specs/design-guard-color-rules.spec.js`
- runtime: §C4
- 금지: 새 token, 리터럴 색, palette 변경, `css/themes.css`, 범용 mapper, 승인된 spec 수정

## 작업
1. `AXE0` 1~4를 실행한다. color-contrast·nested-interactive가 아닌 rule이 나오면 blocker로 보고하고 중단한다.
2. color-contrast를 고친다.
   - 해당 target에 적용된 `css/style.css`의 기존 선언만 `var(--x)`로 바꾼다.
   - token 선택:
     - 영향받는 모든 theme·state에서 대비 4.5 이상인 token만 후보로 둔다.
     - 후보 중 sRGB 제곱거리 합이 가장 작은 것을 고른다.
     - 거리가 같으면 token 이름의 code-unit 순으로 고른다.
   - 후보가 하나도 없으면 `color-scope-themes-required`로 중단한다.
3. nested-interactive를 고친다.
   - `js/main.js` project-card 렌더의 중첩 구조만 바꾼다.
   - card click 위임, 키보드 진입, trigger 복귀 동작은 유지한다.
4. `HOO81_COLOR_V52_ALLOW`(§C6)를 만든다. 바꾼 선언마다 항목 하나를 정렬해 넣고, guard에는 선언 단위 분기만 추가한다.
5. `design-guard-color-rules.spec.js`에 회귀 테스트를 추가한다. 사례는 §C6 판정 기준과 1:1로 대응한다.
   - 통과 사례
     - 같은 file·chain·selector·occurrence·prop의 값이 `base`인 경우 1개
     - 같은 선언의 값이 정확히 `to`인 경우 1개
     - 허용 목록이 `[]`이면 기존 동작과 같은 경우
   - 계속 실패하는 사례
     - 같은 선언의 값이 `base`도 `to`도 아닌 경우
     - chain이 다른 같은 selector
     - 같은 chain·selector에서 occurrence가 다른 경우
     - 같은 rule 안의 다른 선언이 바뀐 경우

## AC
- `T <GS>`
- `DI`
- `T specs/featured.spec.js specs/focus-modal.spec.js specs/modal-regression.spec.js`
- `AXE0`
