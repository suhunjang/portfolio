# Step 40 — axe-classify

- 목적: §6.4 baseline(fix `requiresColorChange` 결정적 기록)·§6.5 plan(그 값에서 blocked·reason 도출)을 계약대로만 생성.
- ≤20분(초과 산정 시 즉시 재계획) / 선행 0~39 / 공통 §9 / gate GATE
- 허용(exact): `tests/fixtures/axe-baseline.json`, `tests/fixtures/axe-remediation-plan.json`(신규)
- runtime: R0
- 추가 금지: 사이트 파일, helper·spec·axe-collected.json, 계약 밖 필드, 조사 결과와 다른 `requiresColorChange`

## 작업
1. `SNAP 40`
2. 산정(묶음별 2분 + target×1분, 합 + 6분) > 20이면 쓰지 않고 재계획. 위반 0이면 `[]`·`{ "groups": [] }`.
3. 조사: `tests/.tmp/axe-classify-<pid>/` 임시 Playwright 스크립트(`W`, `prepareForAxe`)가 target마다 `{ key, target, fixKind, requiresColorChange, evidence }`를 `tests/.tmp`에만 기록. 기록 기준(결정적): 위반 해소에 기존 색 값·색 custom property·색 적용 위치(어떤 요소에 어떤 색 역할) 중 하나라도 바꿔야 하면 `requiresColorChange: true`, 크기·여백·레이아웃·속성·마크업·렌더만으로 해소되면 false; fixKind `css-token`은 항상 true, `js-render`·`static-markup`·`text-change`는 항상 false, `css-rule`은 위 기준. `evidence`에 판정 근거(선언·속성 이름)를 남긴다.
4. baseline: collected entry마다 §6.4 형식(fixes는 targets 순서 1:1, fixFiles = FIX_FILES_BY_KIND, `requiresColorChange` = 3의 기록값, entry fixFiles 합집합).
5. plan: §6.5 형식(PlanTarget 정렬, id 정렬, coverage 완전). 각 그룹 blocked·reason은 대응 fix에서만 도출(text-change → `text change excluded`, `requiresColorChange` true → `color change excluded (HOO-81 §16.3)`, 둘 다면 `text change excluded; color change excluded (HOO-81 §16.3)`, 조각 없으면 blocked false·`""`). blocked가 있으면 `--check-executable` 실패로 재계획.

## AC
- `AXE --check-baseline-match --collected tests/fixtures/axe-collected.json && AXE --check-plan --coverage && AXE --check-executable && AXE --check-regression --collected tests/fixtures/axe-collected.json && FULL && VS && GATE 40 tests/fixtures/axe-baseline.json,tests/fixtures/axe-remediation-plan.json`
