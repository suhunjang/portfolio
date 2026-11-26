# Compact Step 10 — visual-final-contract (r34)

- 목적:
  - screenshot spec을 만든다(§C7: 단일 실행 주체, `COMPACT_RUN_ID`가 있을 때만 실행).
  - final-contract에 bytes·콘텐츠·menu·modal 검증을 더한다.
- 예상 20분, hard timeout 30분. 선행: step 9. 공통 선행조건: §C0.
- 허용 파일(exact):
  - `tests/specs/screenshots.spec.js`(신규)
  - `tests/specs/final-contract.spec.js`(보강)
- runtime: §C4
- 금지: product 수정, 다른 spec 수정, 새 공통 helper·coordinator

## 작업
1. `screenshots.spec.js`를 작성한다(§C7).
   - `COMPACT_RUN_ID`가 없으면 skip한다.
   - desktop-dark가 아닌 project에서는 skip한다.
   - 한 `test.describe.serial` 안에서 아래 순서로 진행한다.
     1. ID를 검사한다.
     2. 출력 디렉터리가 없는지 확인한 뒤 만든다.
     3. config에서 6개 project를 읽는다.
     4. project마다 context를 차례로 만들고 테마를 적용해 15장을 찍는다.
     5. 결과 목록을 1회 검사한다.
     6. manifest를 1회 기록한다.
   - 모달 SVG text가 Space Grotesk인지 확인한다.
2. `final-contract.spec.js`를 보강한다. screenshot 결과에는 의존하지 않는다.
   - `js/data.js`
     - `evidence-step0.json`의 `baselineHead` bytes와 비교한다.
     - index 1·5·7의 title 다음 줄에 `featured: true,`가 정확히 3줄만 추가됐고, 나머지 bytes는 같아야 한다.
     - `featured: false`나 다른 field·형식 변경은 거부한다.
   - `css/themes.css` bytes가 BASE `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`와 같다.
   - 13개 순서와 title이 그대로다.
   - mobile-dark에서 menu를 열고 닫을 수 있다.
   - project 0·1·2·5·7·12의 modal을 열고 닫을 수 있다.

## AC
- `OWN_SPEC tests/specs/screenshots.spec.js`
- `OWN_SPEC tests/specs/final-contract.spec.js`
- `T specs/final-contract.spec.js specs/screenshots.spec.js`(`COMPACT_RUN_ID`가 없으므로 screenshots는 skip되는지 확인한다)
- `SHOT s10 s10`(새 ID `s10-<UTC>`, desktop-dark 하나로 실행). 그 ID의 manifest에 path 15개와 각 sha256이 있어야 한다.
