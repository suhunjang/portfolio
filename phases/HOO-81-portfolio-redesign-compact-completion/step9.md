# Compact Step 9 — contrast-nested

- 목적: 현재 DOM에서 확인된 color-contrast와 nested-interactive 결함을 기존 token과 기존 DOM 경로로 직접 고친다. 색 예외는 선언 단위로만 둔다.
- 예상 16분, hard timeout 30분. 선행: step 8. 공통 선행조건: §C0.
- 허용 파일(exact): `css/style.css`, `js/main.js`, `tests/helpers/design-guard-color-rules.js`, `tests/specs/design-guard-color-rules.spec.js`
- runtime: §C4
- 금지: 새 token, 리터럴 색, palette 변경, `css/themes.css`, 범용 mapper, 승인된 spec 수정

## 작업
1. `AXE0` 1~4를 실행한다. color-contrast·nested-interactive 밖의 rule이 나오면 blocker로 보고하고 중단한다.
2. color-contrast를 고친다.
   - 해당 target에 적용된 `css/style.css` 기존 선언만 `var(--x)`로 바꾼다.
   - token 선택:
     - 모든 theme·state에서 대비 4.5 이상을 만족하는 token만 후보로 둔다.
     - 그중 sRGB 제곱 거리 합이 가장 작은 것을 고른다.
     - 같으면 이름의 code-unit 순서로 정한다.
   - 후보가 없으면 `color-scope-themes-required`로 중단한다.
3. nested-interactive를 고친다.
   - `js/main.js` project-card 렌더의 중첩 구조만 바꾼다.
   - 다음 동작은 유지한다: card click 위임, 키보드 진입, trigger로의 focus 복귀.
4. `HOO81_COLOR_V52_ALLOW`를 작성한다(§C6).
   - 바꾼 선언마다 항목 하나를 넣고 정렬한다.
   - guard에는 선언 단위 분기만 추가한다.
5. 회귀 테스트를 추가한다.
   - 통과: `to` 값, 그리고 상수가 `[]`일 때의 기존 동작
   - 실패: 다른 chain, 다른 occurrence, 같은 rule의 다른 선언, `to`가 아닌 값

## AC
- `T <GS>`
- `DI`
- `T specs/featured.spec.js specs/focus-modal.spec.js specs/modal-regression.spec.js`
- `AXE0`
