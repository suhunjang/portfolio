# Compact Step 4 — section-structure (r21, FINAL 변환)

- 목적: §C1의 FINAL 구조(원 §4)를 구현한다. 허용되는 변경은 원 §5 예외 (2)~(5)뿐이다.
- 예상 18분, hard timeout 30분. 선행 step 3. 공통 선행조건 §C0.
- 허용 파일(exact):
  - `index.html`: hero 밖 섹션 subtree 이동, kicker·heading, Stack &amp; Contact 분리, nav 순서, scroll-hint만
  - `js/main.js`: 스크롤스파이 배열, skill-group h4만
  - `tests/specs/final-contract.spec.js`(신규)
- runtime: §C4
- 금지:
  - `css/*`, `js/data.js`, hero 내부 변경
  - 원 §5 예외 밖의 문구·수치 변경
  - 새 섹션·이미지·아이콘 추가

## 작업
1. `final-contract.spec.js`를 작성하고 `OWN_SPEC`이 통과하는지 본 뒤, RED를 확인한다. 이 spec이 소유하는 assertion:
   - 섹션 id·class·kicker·h2 텍스트가 §C1 표와 정확히 같다.
   - about 안에 `h3.subsection-title` "기술 스택"이 정확히 1개 있고, 그 뒤에 `#skillsGrid`가 오며, skill-group 제목은 h4다.
   - contact 섹션에 `.contact-card`와 h3 "함께 만들어요"가 있다.
   - nav 순서가 §C1과 같다.
   - 스크롤스파이가 원 §4의 문법(projects·about)대로 동작한다.
   - `.scroll-hint`가 `#career`를 가리킨다.
   - heading 계층이 올바르다.
   - `#heroFeatured`가 유지된다.
   - `#projectGrid`에 13개 카드가 data.js 순서대로 있다.
2. subtree를 통째로 이동한다. 텍스트는 바꾸지 않는다.

## AC
- `OWN_SPEC tests/specs/final-contract.spec.js`
- `T specs/final-contract.spec.js specs/content-static.spec.js specs/content-data.spec.js specs/ui-regression.spec.js`
- `DI`
- `T <GS>`
