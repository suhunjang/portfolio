# Compact Step 5 — final-verification

- 목적: 시각 증거와 최종 계약 spec을 만들고, 전체 검증을 1회 수행한다.
- 예상 20분, hard timeout 30분. 선행: step 4.
- 허용 파일(exact): `tests/specs/screenshots.spec.js`(신규), `tests/specs/final-contract.spec.js`(신규)
- runtime: `tests/screenshots/**`, `tests/.tmp/**`
- 금지: product 파일과 다른 spec 수정. 실패하면 원인 step을 보고하고 중단한다.

## 작업
1. `tests/specs/screenshots.spec.js`를 작성한다.
   - 6 project page 화면
   - desktop-dark/light 대표 모달(project 1·5·7)
   - lightbox
   - print
   - 각 화면은 `prepareForAxe`를 거친 뒤 `tests/screenshots/`에 촬영한다.
   - 모달 SVG text의 font-family가 Space Grotesk인지 확인한다.
2. `tests/specs/final-contract.spec.js`를 작성한다. 이 파일이 아래 assertion을 소유한다.
   - `js/data.js`의 featured가 정확히 1·5·7이다. PROJECTS 13개의 순서·title이 BASE `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`와 같다(git show로 읽기만).
   - `css/themes.css`의 bytes가 BASE와 같다.
   - FINAL IA 섹션 6개의 순서가 맞다.
   - 375·768·1280에서 가로 스크롤이 없다.
   - mobile-dark에서 menu를 열고 닫을 수 있다.
   - 6 project 각각에서 modal이 열린다(project 0·1·2·5·7·12).
   - print 시 본문과 featured가 보이고, interaction과 modal은 숨겨진다.
3. `SPEC_GATE`를 통과시킨다.
4. 아래 AC를 실행하고, 실패 0인지와 `tests/screenshots/**` 산출물 SHA-256 목록을 evidence에 기록한다.

## AC
- `SPEC_GATE`
- `FULL`
- `AXE0`
- `VS`
- `T specs/screenshots.spec.js specs/final-contract.spec.js specs/featured.spec.js specs/focus-modal.spec.js specs/design-intake.spec.js`
