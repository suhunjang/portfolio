# Compact Step 5 — section-layout (r22)

- 목적: 원 §7의 섹션 레이아웃을 구현한다(padding, gap, Career 반응형, grid, 비색 타이포 위계).
- 예상 16분, hard timeout 30분. 선행: step 4. 공통 선행조건: §C0.
- 허용 파일(exact):
  - `css/style.css`: 섹션 padding, Career, grid, 제목 타이포 중 색이 아닌 속성만
  - `tests/specs/final-contract.spec.js`: 보강
- runtime: §C4
- 금지: `index.html`, `js/*`, 색

## 작업
1. `final-contract.spec.js`에 아래 assertion을 보강하고 RED를 확인한다. 대상은 6개 project 전부다.
   - 가로 스크롤이 0이다.
   - 섹션 padding이 tokens.`sectionPaddingPx[viewport]`와 같다.
   - 세 grid의 gap이 24px이다.
   - projectGrid와 strengthsGrid의 열 수가 1/2/3이다.
   - Career는 375에서 세로, 768·1280에서 가로로 배치된다(top 차이 < 24).
   - 375에서 highlights가 보인다.
   - `.subsection-title`이 h2보다 위계가 낮다(weight는 h2 이하, size는 h2 미만).
2. 구현한다.

## AC
- `OWN_SPEC tests/specs/final-contract.spec.js`
- `T specs/final-contract.spec.js specs/ui-regression.spec.js`
- `DI`
- `T <GS>`
