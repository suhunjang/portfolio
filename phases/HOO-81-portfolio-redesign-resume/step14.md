# Resume Step 14 — axe-classify-pair-integrate

- 목적: §R6 — occ-batch 1~12의 139 occurrence를 25 pair로 통합, 배치를 넘는 pair 포함 모든 occurrence 판정 일치 검사.
- 12분 / 선행 0~13 / 공통 §R1 / gate `RGATE 14`
- 허용(exact): 없음
- runtime: R0 + `tests/.tmp/axe-classify/pairs.json`(이 파일만)
- 추가 금지: occ-batch 파일 수정, baseline·plan 작성, 사이트·helper·spec·collected 수정, 불일치 pair 임의 결정

## 작업
1. `RSNAP 14`
2. 12개 배치 읽기(누락·중복이면 중단) → pair별 판정 일치 확인(불일치면 `classification-inconsistent:{pair}` exit 1, 파일 미작성, 재계획) → `pairs.json` 작성(§R6 형식).

## AC
- `INTEGRATE_CHECK && FULL && VS && RGATE 14 ''`(첫 명령 stdout `integrate-check: OK 25 139`)
