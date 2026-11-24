# Step 29 — axe-plan-executable

- 목적: blocked(색 변경 제외 포함)·text-change·빈 fixFiles 그룹에서 중단하는 실행 가능성 검사.
- 예상 15분 / 선행 0~28 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §7.2, §8.3(step 29, 색 변경 제외, 재계획 조건), §16.3
- tracked 허용(exact): `tests/helpers/axe.js`(추가만), `tests/specs/axe-helper.spec.js`(추가만)
- runtime: R0(독립 디렉터리)
- 금지: §15.7, 이전 helper 동작, 실제 fixtures

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step29`
2. 설계 §8.3 step 29 계약 구현.
3. spec(desktop-dark): `{ groups: [] }` → `[]`; 실행 가능 → `[]`; blocked css-rule → `blocked-group`; reason `color change excluded (HOO-81 §16.3)`인 blocked css-token 그룹 → `blocked-group`; text-change → 3종 모두; 혼합 → blocked만; 입력 불변; CLI 빈 0, 가능 0, blocked 1(첫 줄 고정), fixFiles `[]` 1, 파일 오류 1.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step29.json --allow tests/helpers/axe.js,tests/specs/axe-helper.spec.js` → exit 0
