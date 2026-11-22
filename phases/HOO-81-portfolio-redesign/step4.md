# Step 4 — final-verification

설계: 전체

## 목표

전체 회귀 검증과 범위 준수를 확인하고, 시각 증거를 남긴다.

## 변경 허용 파일

`tests/**` (검증 보조 코드만). 사이트 파일은 실패를 고칠 때만 최소한으로 수정한다.

## 작업

1. `tests/specs/screenshots.spec.js`를 작성한다.
   - 3개 viewport × dark/light, 총 6장의 전체 페이지 스크린샷을 `tests/screenshots/`에 저장한다.
   - 모달이 열린 상태 1장, 인쇄 미디어 1장도 저장한다.
   - 이 파일들은 커밋하지 않는다. `tests/.gitignore`에 추가한다.
2. 범위 점검을 한다. 결과는 실행 로그로 남긴다.
   - `git diff --name-only main...HEAD`가 허용 경로(`index.html`, `css/`, `js/`, `tests/`) 안에만 있다.
   - `git diff main...HEAD -- js/data.js`가 `featured: true` 3줄 추가뿐이다.
   - 루트에 package.json이 없다.
   - `index.html` Google Fonts 링크에 Space Grotesk가 남아 있다.
3. `npm --prefix tests test`를 전체 실행해 모두 통과하는지 확인한다.
4. 각 viewport와 테마에서 대표 카드 3개를 각각 열어, 모달 SVG 일러스트 서체와 썸네일 색이 깨지지 않는지 스크린샷으로 확인한다.

## 완료 기준

- 전체 테스트가 통과한다(콘솔 에러 0건, axe 위반 0건, 기능 회귀 0건).
- 범위 점검 항목이 모두 충족된다.
- merge, deploy, main 직접 변경을 하지 않는다. PR 준비 단계까지만 진행한다.
