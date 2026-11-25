# Compact Step 6 — visual-final-contract

- 목적: 시각 증거 spec과 최종 계약 spec을 작성한다.
- 예상 20분, hard timeout 30분. 선행: step 5. 공통 선행조건: §C0.
- 허용 파일(exact): `tests/specs/screenshots.spec.js`, `tests/specs/final-contract.spec.js`(둘 다 신규)
- runtime: `tests/screenshots/**`
- 금지: product 파일 수정, 다른 spec 수정. 실패하면 원인 step을 보고하고 중단한다.

## 작업
1. `tests/specs/screenshots.spec.js`를 작성한다.
   - 설계 §C7의 15장을 그 정확한 파일명으로 찍는다.
   - 각 장은 `prepareForAxe`를 거친 뒤 찍는다. 대상 project에 맞지 않는 장은 test.skip한다.
   - lightbox 장은 기존 helper가 찾은 첫 shots project ID를 `tests/.tmp/compact/lightbox-project.txt`에 기록한다.
   - 모달 SVG text의 font-family가 Space Grotesk인지 확인한다.
2. `tests/specs/final-contract.spec.js`를 작성한다. 이 spec이 소유하는 assertion:
   - `js/data.js`:
     - `tests/.tmp/compact/evidence-step0.json`의 `baselineHead`에서 `git show`로 bytes를 읽어 최종 bytes와 비교한다.
     - PROJECTS index 1·5·7의 title 다음에 `featured: true,` 정확히 3줄만 추가됐고, 나머지 bytes는 같아야 한다.
     - `featured: false`, 다른 field, format 변경은 거부한다.
   - `css/themes.css` bytes가 BASE `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`와 같다.
   - FINAL IA 6개 섹션 순서, PROJECTS 13개의 순서·title.
   - 375·768·1280에서 가로 스크롤 0.
   - mobile-dark에서 menu를 열고 닫을 수 있다.
   - project 0·1·2·5·7·12의 modal이 열리고 닫힌다.
   - print에서 본문·featured가 보이고, interaction·modal은 숨겨진다.
   - `tests/screenshots/`의 png 목록이 §C7 15장과 정확히 같다. screenshots spec 실행 후에 검사한다.
3. 두 spec 각각 `OWN_SPEC`을 통과한 뒤 실행한다.

## AC
- `OWN_SPEC tests/specs/screenshots.spec.js`
- `OWN_SPEC tests/specs/final-contract.spec.js`
- `T specs/screenshots.spec.js`
- `T specs/final-contract.spec.js`
