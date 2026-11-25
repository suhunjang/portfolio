# Compact Step 2 — section-layout

- 목적: 현재 HEAD에 남은 실제 diff만 구현한다. 색은 바꾸지 않는다.
  - FINAL 섹션 구조, nav 순서, scrollspy(원 §4)
  - 섹션 padding·grid·Career 반응형(원 §7)
  - hit target, hover·active의 transform·opacity
  - `@media print`(clamp 해제 포함)
- 예상 18분, hard timeout 30분. 선행: step 1. 공통 선행조건: §C0.
- 허용 파일(exact): `index.html`, `js/main.js`(scrollspy 배열·skill-group heading만), `css/style.css`
- 금지:
  - 색 선언 변경
  - 문구·수치·이미지 변경
  - 새 섹션 추가
  - `js/data.js` 수정
  - focus trap 구현(step 3 몫)

## 작업
1. 섹션 subtree를 통째로 옮겨 FINAL IA 순서를 맞추고, nav 순서·scrollspy를 맞춘다.
2. `css/style.css`에 비색 규칙만 추가한다: 레이아웃, hit target, hover/active, print.

## AC
- `T specs/content-static.spec.js specs/ui-regression.spec.js specs/first-visit.spec.js specs/smoke.spec.js specs/featured.spec.js`
- `DI`
- `T <GS>`
