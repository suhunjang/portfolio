# Step 27 — axe-baseline-projection

- 목적: collected↔baseline 투영과 양방향 일치 검사.
- 예상 17분 / 선행 0~26 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §8.3(step 27)
- tracked 허용(exact): `tests/helpers/axe.js`(추가만), `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 디렉터리)
- 금지: §15.7, 이전 helper 동작, 실제 fixtures

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step27`
2. 설계 §8.3 step 27 계약 구현.
3. spec(desktop-dark): projectEntry 7필드·정렬·throw; compareCollectedBaseline ok·missing/extra entries·targets·fieldMismatches·중복 key throw·입력 불변; CLI 일치 0, 불일치 5종 1, 파일 오류 1.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step27.json --allow tests/helpers/axe.js,tests/specs/axe-helper.spec.js` → exit 0
