# Compact Step 10 — visual-final-contract (r34)

- 목적:
  - screenshot spec을 작성한다(§C7: 실행 주체 하나, `COMPACT_RUN_ID` 조건부).
  - final-contract에 bytes, 콘텐츠, menu, modal 검증을 보강한다.
- 예상 20분, hard timeout 30분. 선행: step 9. 공통 선행조건: §C0.
- 허용 파일(exact):
  - `tests/specs/screenshots.spec.js`(신규)
  - `tests/specs/final-contract.spec.js`(보강)
- runtime: §C4
- 금지: product 수정, 다른 spec 수정, 새 공통 helper·coordinator

## 작업
1. `screenshots.spec.js`를 작성한다(§C7).
   - `COMPACT_RUN_ID`가 없으면 suite 전체를 `test.skip`한다.
   - project가 desktop-dark가 아니면 skip한다.
   - 나머지 작업은 `test.describe.serial` 하나 안에서 순서대로 한다.
     1. ID 형식을 검사한다.
     2. 출력 디렉터리가 없는지 확인하고 생성한다.
     3. config에서 6개 project를 읽는다.
     4. project마다 context를 순차로 만들고 테마를 적용해 15장을 찍는다.
     5. 결과 목록을 1회 검사한다.
     6. manifest를 1회 기록한다.
   - 모달 SVG text의 font가 Space Grotesk인지 확인한다.
2. `final-contract.spec.js`를 보강한다. screenshot 결과에는 의존하지 않는다.
   - `js/data.js`
     - `tests/.tmp/compact/evidence-step0.json`에 기록된 `baselineHead`의 bytes와 비교한다.
     - 허용되는 차이는 index 1·5·7 title 다음 줄의 `featured: true,` 정확히 3줄뿐이다. 나머지 bytes는 같아야 한다.
     - `featured: false`나 다른 field·형식 변경은 거부한다.
   - `css/themes.css`의 bytes가 BASE `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`와 같다.
   - 13개 project의 순서와 title이 그대로다.
   - mobile-dark에서 menu가 열리고 닫힌다.
   - project 0·1·2·5·7·12의 modal이 열리고 닫힌다.

## AC
- `OWN_SPEC tests/specs/screenshots.spec.js`
- `OWN_SPEC tests/specs/final-contract.spec.js`
- `T specs/final-contract.spec.js specs/screenshots.spec.js`
  - 이 실행에는 `COMPACT_RUN_ID`가 없으므로 screenshots suite가 skip되는지 확인한다.
- `SHOT s10 s10`
  - 새 ID `s10-<UTC>`를 쓰고, desktop-dark 하나로 실행한다.
  - 그 ID의 manifest에 15개 path와 sha256이 모두 있어야 한다.
