# Step 15 — axe-baseline-regression

- 목적: baseline 스키마·회귀 판정·분류 대기 baseline 계약.
- 예상 19분 / 선행 0~14 / 공통 절차 설계 §15
- read-first: 설계 §8.3(entry key, step 15, 실행 모드)
- tracked 허용(exact): `tests/helpers/axe.js`(추가만), `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 디렉터리)
- 금지: §15.7, step 10·14 동작, 실제 fixtures

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step15`
2. 설계 §8.3 step 15 계약 구현(`resolveBaselineMode`는 환경변수를 읽지 않는다).
3. spec(desktop-dark, 경로는 모두 독립 디렉터리): validateBaseline 통과(혼합 color-contrast, js-render, static-markup, text-change `[]`); 거부 — key 불일치·중복·targets 중복·미정렬, kind별 파일 오대응 5종, 비-text-change 빈 배열, js-render 여분 파일, 합집합 불일치, fix 누락, targets 밖 target, 알 수 없는 kind; checkRegression 새 key/target 오류·사라짐 허용·`page:desktop-dark`에만 있는 target이 `page:desktop-light`에 나오면 new-key/new-target·입력 불변; resolveBaselineMode — baseline 있음 → `check`, baseline 없음+collected 있음+plan 없음 → `pending`, baseline 없음+collected 없음 → throw, baseline 없음+collected 있음+plan 있음 → throw, `process.env.AXE_ALLOW_MISSING_BASELINE='1'`을 설정해도 collected 없으면 throw; loadBaseline 없음·잘못된 JSON·`{}` throw; CLI `--assert-empty` `[]` 0, `[{}]`·`{}`·잘못된 JSON·없음 1.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step15.json --allow tests/helpers/axe.js,tests/specs/axe-helper.spec.js` → exit 0
