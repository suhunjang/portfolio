# Resume Step 16 — axe-classify-pair-integrate

- 목적: §R6 — occ-batch 1~14의 139 occurrence를 25 pair로 통합, 배치를 넘는 pair 포함 모든 occurrence 판정 일치·evidence 정확 집계 검사.
- 12분 / 선행 0~15 / 공통 §R1 / gate `RGATE 16`
- 허용(exact): 없음
- runtime: R0 + `tests/.tmp/axe-classify/pairs.json`(이 파일만)
- 추가 금지: occ-batch·server 파일 수정, baseline·plan 작성, 사이트·helper·spec·collected 수정, 불일치 pair 임의 결정, evidence 요약·재정렬·중복 제거

## 작업
1. `RSNAP 16`
2. batch 1→14 순서·각 `occurrences` 배열 순서로 읽기(누락·중복이면 중단) → pair별 판정 일치 확인(불일치면 `classification-inconsistent:{pair}` exit 1, 파일 미작성, 재계획) → pair별 evidence 목록 L을 같은 순서로 수집 → `pairs.json` 작성(§R6 형식, `evidence` = `'; '.join(L)`).

## AC
- `INTEGRATE_CHECK && FULL && VS && RGATE 16 ''`(첫 명령 stdout `integrate-check: OK 25 139`)
