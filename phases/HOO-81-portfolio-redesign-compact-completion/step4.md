# Compact Step 4 — section-structure (r21, FINAL 변환)

- 목적: §C1의 FINAL 구조(원 §4)와 원 §5의 허용 예외 (2)~(5)를 구현한다.
  - kicker·heading
  - `#skillsGrid`를 about으로 이동
  - `h3.subsection-title` 기술 스택 1개
  - skill-group 제목을 h4로
  - section-alt 클래스
  - nav·스크롤스파이
  - `.scroll-hint`
- 예상 18분, hard timeout 30분. 선행: step 3. 공통 선행조건: §C0.
- 허용 파일(exact):
  - `index.html`: hero 밖 섹션 subtree 이동, kicker·heading, Stack &amp; Contact 분리, nav 순서, scroll-hint만
  - `js/main.js`: 스크롤스파이 배열과 skill-group h4만
  - `tests/specs/final-contract.spec.js`(신규)
- runtime: §C4
- 금지: `css/*`, `js/data.js`, hero 내부, 원 §5 예외 밖의 문구·수치, 새 섹션·이미지·아이콘

## 작업
1. `final-contract.spec.js`를 작성한다. `OWN_SPEC`이 통과한 뒤 RED를 확인한다. 이 spec이 소유하는 assertion은 다음과 같다.
   - 섹션 id·class·kicker·h2 텍스트가 §C1 표와 정확히 같다.
   - about 안에 `h3.subsection-title` 기술 스택이 정확히 1개 있고, 그 뒤에 `#skillsGrid`가 있다. skill-group 제목은 h4다.
   - contact에 `.contact-card`와 h3 함께 만들어요가 있다.
   - nav 순서가 맞다.
   - 스크롤스파이 동작을 원 §4의 정확한 문법으로 projects와 about에서 각각 확인한다.
   - `.scroll-hint`의 href가 `#career`다.
   - heading 계층이 맞다.
   - `#heroFeatured`가 유지된다.
   - `#projectGrid`에 카드 13개가 data.js 순서대로 있다.
2. subtree를 통째로 이동한다. 텍스트는 바꾸지 않는다.

## AC
- `OWN_SPEC tests/specs/final-contract.spec.js`
- `T specs/final-contract.spec.js specs/content-static.spec.js specs/content-data.spec.js specs/ui-regression.spec.js`
- `DI`
- `T <GS>`
