# Compact Step 5 — section-layout (r22)

- 목적: 원 §7의 섹션 레이아웃을 구현한다. 대상은 padding, card gap, Career 반응형, grid, 비색 타이포 위계다.
- 예상 16분, hard timeout 30분. 선행: step 4. 공통 선행조건: §C0.
- 허용 파일(exact):
  - `css/style.css`: 섹션 padding, Career, grid gap과 열, 섹션 제목과 `.subsection-title`의 비색 타이포만
  - `tests/specs/final-contract.spec.js`: 보강
- runtime: §C4
- 금지: `index.html`, `js/*` 수정, 색 변경

## 작업
1. `final-contract.spec.js`에 아래 assertion을 보강하고 RED를 확인한다(6 project 대상).
   - 가로 스크롤 0
   - `#career`부터 `#contact`까지의 padding-top·bottom이 tokens.`sectionPaddingPx[viewport]`와 같다.
   - 세 grid의 row-gap·column-gap이 24px다.
   - projectGrid와 strengthsGrid가 1/2/3열이다.
   - Career는 375에서 세로 배치, 768·1280에서 가로 배치다(top 차이 < 24).
   - 375에서 highlights가 보인다.
   - `.subsection-title`의 weight는 h2 이하이고 size는 h2보다 작다.
2. 구현한다.

## AC
- `OWN_SPEC tests/specs/final-contract.spec.js`
- `T specs/final-contract.spec.js specs/ui-regression.spec.js`
- `DI`
- `T <GS>`
