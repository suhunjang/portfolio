# Step 22 — axe-classify

- 목적: baseline과 remediation plan 확정.
- 예상 20분 이하(초과 산정 시 즉시 재계획) / 선행 0~21 / 공통 절차 설계 §15
- read-first: 설계 §7.2, §8.3(step 16 투영, step 18 실행 가능성, fixture, FIX_FILES_BY_KIND, step 22); `axe-collected.json` 존재
- tracked 허용(exact): `tests/fixtures/axe-baseline.json`(신규), `tests/fixtures/axe-remediation-plan.json`(신규)
- runtime: R0
- 금지: §15.7, 사이트 파일, helper·spec·axe-collected.json

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step22`
2. 시간 산정 먼저: 묶음별 (2분 + target × 1분) 합 + 6분. 20분 초과면 파일을 쓰지 않고 중단·재계획. 위반 0건이면 baseline `[]`, plan `{ groups: [] }`.
3. 조사: `tests/.tmp` 임시 Playwright 스크립트(래퍼 사용, `prepareForAxe`로 준비)로 computed 색, `var(--토큰)` 출처, JS 렌더 여부, 정적 속성 여부를 보고 fixKind 판별.
4. baseline: collected entry마다 projectEntry 7필드 + `fixes`, `fixFiles`(FIX_FILES_BY_KIND와 정확히, 항목은 합집합).
5. plan: kebab-case 고유 id, difficulty·estMinutes(≤20)·fixFiles·blocked·reason, coverage 완전, 자동 편입 금지. blocked(text-change 포함)는 사실대로 기록하며 이 경우 AC의 `--check-executable`이 실패해 재계획으로 끝난다.

## AC

- `sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-baseline-match --collected tests/fixtures/axe-collected.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-plan --coverage && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-executable && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-regression --collected tests/fixtures/axe-collected.json && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step22.json --allow tests/fixtures/axe-baseline.json,tests/fixtures/axe-remediation-plan.json` → exit 0 (기본 testCommand가 옵션 없이 통과)
