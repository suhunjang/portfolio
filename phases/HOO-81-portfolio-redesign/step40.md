# Step 40 — axe-classify

- 목적: §6.4 baseline·§6.5 plan을 계약대로만 생성(색 변경 필요 target은 blocked).
- ≤20분(초과 산정 시 즉시 재계획) / 선행 0~39 / 공통 §9 / gate GATE
- 허용(exact): `tests/fixtures/axe-baseline.json`, `tests/fixtures/axe-remediation-plan.json`(신규)
- runtime: R0
- 추가 금지: 사이트 파일, helper·spec·axe-collected.json, 계약 밖 필드

## 작업
1. `SNAP 40`
2. 산정(묶음별 2분 + target×1분, 합 + 6분) > 20이면 쓰지 않고 재계획. 위반 0이면 `[]`·`{ "groups": [] }`.
3. `tests/.tmp` 임시 Playwright 스크립트(`W`, `prepareForAxe`)로 fixKind 판별 → baseline(fixes 1:1, FIX_FILES_BY_KIND, 합집합) → plan(정렬, coverage 완전, blocked·reason). blocked가 있으면 `--check-executable` 실패로 재계획.

## AC
- `AXE --check-baseline-match --collected tests/fixtures/axe-collected.json && AXE --check-plan --coverage && AXE --check-executable && AXE --check-regression --collected tests/fixtures/axe-collected.json && FULL && VS && GATE 40 tests/fixtures/axe-baseline.json,tests/fixtures/axe-remediation-plan.json`
