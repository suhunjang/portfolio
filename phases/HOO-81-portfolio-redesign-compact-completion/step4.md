# Compact Step 4 — contrast-nested

- 목적: 현재 DOM에서 확인된 color-contrast·nested-interactive 결함을 기존 token과 기존 DOM 경로로 직접 고친다.
- 예상 15분, hard timeout 30분. 선행: step 3. 공통 선행조건: §C0.
- 허용 파일(exact): `css/style.css`, `js/main.js`, `tests/helpers/design-guard-color-rules.js`, `tests/specs/design-guard-color-rules.spec.js`
- 금지:
  - 새 token, 리터럴 색, palette 변경
  - `css/themes.css` 수정
  - 범용 mapper·framework
  - 승인된 spec 수정

## 작업
1. `AXE0` 1~4단계를 실행한다. color-contrast·nested-interactive 밖의 rule이 나오면 그 rule을 blocker로 보고하고 중단한다.
2. color-contrast를 고친다.
   - 해당 target에 적용된 `css/style.css` 기존 선언만, 기존 color token `var(--x)`로 바꾼다.
   - token 선택: 영향받는 모든 theme·state에서 대비 4.5 이상인 후보 중, 원래 계산색과의 sRGB 제곱거리 합이 가장 작은 것을 고른다. 같으면 token 이름의 code-unit 순서로 정한다.
   - 후보가 없으면 `color-scope-themes-required`로 중단한다.
3. nested-interactive를 고친다.
   - `js/main.js` project-card 렌더에서 card와 `button.project-more`가 중첩된 구조만 바꾼다.
   - 다음 동작은 유지한다: card click 위임으로 모달 열기, 키보드 진입, trigger 복귀.
4. guard 예외를 추가한다.
   - `HOO81_COLOR_V52_ALLOW`를 export한다. 2단계에서 바꾼 선언마다 `{file, selectors, prop, base, to}` 항목을 넣고 정렬한다.
   - guard는 그 정확한 위치의 값이 `base` 또는 `to`일 때만 해당 색 규칙을 제외한다.
   - 회귀 1개를 추가한다:
     - 목록 밖 위치나, 목록 위치라도 다른 값이면 위반이다.
     - `to`는 통과한다.
     - 목록이 `[]`이면 기존 동작과 같다.

## AC
- `T <GS>`
- `DI`
- `T specs/featured.spec.js specs/focus-modal.spec.js specs/modal-regression.spec.js`
- `AXE0`
