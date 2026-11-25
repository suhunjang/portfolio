# Compact Step 10 — visual-final-contract (r34)

- 목적: screenshot spec(§C7)을 작성하고, final-contract를 bytes·콘텐츠·menu·modal 기준으로 보강한다.
- 예상 20분, hard timeout 30분. 선행: step 9. 공통 선행조건 §C0.
- 허용 파일(exact):
  - `tests/specs/screenshots.spec.js`: 신규
  - `tests/specs/final-contract.spec.js`: 보강
- runtime: §C4
- 금지: product 파일, 그 밖의 spec

## 작업
1. `screenshots.spec.js`를 작성한다(§C7).
   - `test.describe.serial` 안에서 다음 순서로 진행한다:
     1. run 디렉터리가 이미 있으면 실패한다.
     2. 15장을 촬영한다. 각 장은 `prepareForAxe`를 거친 뒤 찍는다.
     3. 목록과 SHA를 검증하고 manifest를 기록한다.
   - 모달 SVG text의 font-family가 Space Grotesk인지 확인한다.
2. `final-contract.spec.js`를 보강한다. screenshot 산출물에는 의존하지 않는다.
   - `js/data.js`:
     - `tests/.tmp/compact/evidence-step0.json`의 `baselineHead`로 `git show`한 bytes와 현재 bytes를 비교한다.
     - 허용되는 차이는 PROJECTS index 1·5·7의 title 다음에 `featured: true,`가 정확히 3줄 추가된 것뿐이다. 그 밖의 bytes는 같아야 한다.
     - `featured: false`나 다른 field·format 변경은 거부한다.
   - `css/themes.css`의 bytes가 BASE `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`와 같다.
   - PROJECTS 13개의 순서와 title이 그대로다.
   - mobile-dark에서 menu를 열고 닫을 수 있다.
   - project 0·1·2·5·7·12의 modal이 열리고 닫힌다.

## AC
- `OWN_SPEC tests/specs/screenshots.spec.js`
- `OWN_SPEC tests/specs/final-contract.spec.js`
- `T specs/final-contract.spec.js`
- `SHOT step10`
