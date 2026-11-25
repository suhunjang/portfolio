# Compact Step 10 — visual-final-contract (r34)

- 목적:
  - screenshot spec을 작성한다(§C7: 단일 실행 주체, `COMPACT_RUN_ID` 조건).
  - final-contract를 bytes·콘텐츠·menu·modal 검사로 보강한다.
- 예상 20분, hard timeout 30분. 선행: step 9. 공통 선행조건: §C0.
- 허용 파일(exact):
  - `tests/specs/screenshots.spec.js`(신규)
  - `tests/specs/final-contract.spec.js`(보강)
- runtime: §C4
- 금지: product 파일 수정, 다른 spec 수정, 새 공통 helper·coordinator 추가

## 작업
1. `screenshots.spec.js`를 작성한다. 세부 규칙은 §C7을 따른다.
   - `COMPACT_RUN_ID`가 없으면 suite 전체를 `test.skip`한다.
   - `testInfo.project.name !== 'desktop-dark'`이면 suite 전체를 skip한다.
   - desktop-dark의 `test.describe.serial` 하나 안에서 아래를 순서대로 한다.
     1. ID 형식을 검사한다.
     2. 출력 디렉터리가 없는지 검사한 뒤 1회 생성한다.
     3. `tests/playwright.config.js`의 6개 project 설정을 읽는다.
     4. project마다 `browser.newContext`와 `installProjectTheme`로 context를 순차 생성하고, 15장을 촬영한다.
     5. 15개 exact 경로를 1회 검사한다.
     6. SHA manifest를 1회 기록한다.
   - 모달 SVG text의 font-family가 Space Grotesk인지 확인한다.
2. `final-contract.spec.js`를 보강한다. screenshot 산출물에는 의존하지 않는다.
   - `js/data.js` bytes 비교
     - 기준은 `tests/.tmp/compact/evidence-step0.json`의 `baselineHead`를 `git show`한 bytes다.
     - PROJECTS index 1·5·7의 title 다음에 `featured: true,` 정확히 3줄만 추가되고, 나머지 bytes는 같아야 한다.
     - `featured: false`나 다른 필드·형식 변경은 거부한다.
   - `css/themes.css` bytes가 BASE `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`와 같다.
   - PROJECTS 13개의 순서와 title이 같다.
   - mobile-dark에서 menu가 열리고 닫힌다.
   - project 0·1·2·5·7·12의 modal이 열리고 닫힌다.

## AC
- `OWN_SPEC tests/specs/screenshots.spec.js`
- `OWN_SPEC tests/specs/final-contract.spec.js`
- `T specs/final-contract.spec.js specs/screenshots.spec.js`
  - 이 실행에는 `COMPACT_RUN_ID`가 없으므로 screenshots suite가 skip되는지 확인한다.
- `SHOT s10 s10`
  - 새 ID `s10-<UTC>`를 만들어 `shot-id-s10.txt`에 기록하고 desktop-dark 하나로 실행한다.
  - 생성된 `tests/.tmp/compact/screenshots-<그 ID>.json`에 15개 path와 sha256이 있어야 한다.
