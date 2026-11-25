# Compact Step 3 — contrast-nested

- 목적: 현재 DOM에서 확인된 color-contrast와 nested-interactive 결함을 기존 token과 기존 DOM 경로로 직접 수정한다. `css/themes.css`는 읽기 전용이다.
- 예상 15분, hard timeout 30분. 선행: step 2.
- 허용 파일(exact): `css/style.css`, `js/main.js`, `tests/helpers/design-guard-color-rules.js`, `tests/specs/design-guard-color-rules.spec.js`
- 금지:
  - 새 token, 리터럴 색, palette 변경
  - `css/themes.css` 수정
  - 범용 mapper·framework
  - 승인된 기존 spec을 수정해야만 해결되는 변경

## 작업
1. `AXE0`의 1~4단계를 실행해 `tests/.tmp/axe-current.json`을 얻는다.
   - ruleId가 color-contrast나 nested-interactive가 아니면 그 rule만 blocker로 보고하고 중단한다.
2. color-contrast:
   - 해당 target에 적용된 `css/style.css` 기존 선언만, 기존 color token `var(--x)`로 바꾼다.
   - token 선택 규칙: 영향을 받는 모든 theme·state에서 대비 4.5 이상을 만족하는 기존 token 가운데, 원래 계산색과의 sRGB 거리 합이 가장 작은 것을 고른다. 거리가 같으면 token 이름의 코드 단위 순서로 정한다.
   - 조건을 만족하는 token이 없으면 `color-scope-themes-required`로 중단한다.
3. nested-interactive:
   - `js/main.js`의 project-card 렌더 부분에서 card와 `button.project-more`가 중첩된 구조만 고친다.
   - card click 위임으로 모달이 열리는 동작, 키보드 진입, trigger로의 focus 복귀는 그대로 유지한다.
4. design guard 예외:
   - `tests/helpers/design-guard-color-rules.js`에 export 상수 `HOO81_COLOR_V52_ALLOW` 1개를 둔다. 항목은 2단계에서 바꾼 선언의 `{file, selectors, prop, base, to}`이고 정렬해 둔다.
   - guard는 그 정확한 위치에서 값이 `base`이거나 정확히 `to`일 때만 색 규칙에서 제외한다.
   - `tests/specs/design-guard-color-rules.spec.js`에 회귀 테스트 1개를 둔다. 목록 밖 위치와, 목록 위치의 다른 값은 여전히 위반이어야 한다. `to`는 통과해야 한다. 상수가 `[]`이면 기존 동작과 같아야 한다.

## AC
- `T <GS>`
- `DI`
- `AXE0`
