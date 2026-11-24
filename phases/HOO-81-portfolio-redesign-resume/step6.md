# Resume Step 6 — axe-classify-occ-batch-5

- 목적: §R5 batch 5(정렬 occurrence 41~50) 분류.
- 20분(2 + 2 + 10 + 6) / 선행 0~5 / 공통 §R1 / gate `RGATE 6`
- 허용(exact): 없음
- runtime: R0 + `tests/.tmp/axe-classify/occ-batch-5.json`, `tests/.tmp/axe-classify/server-5.json`(이 두 파일만)
- 추가 금지: 다른 batch·pairs 파일 수정·작성, 조사 스크립트 파일 저장, baseline·plan 작성, 사이트·helper·spec·config·collected 수정, 이 step이 띄우지 않은 프로세스 종료, §R5.1 고정 골격 변경

## 작업
1. `RSNAP 6`
2. `OCC_RUN 5`(§R5.1, step 2와 같은 절차) → `occ-batch-5.json`.

## AC
- `OCC_CHECK 5 && FULL && VS && RGATE 6 ''`(첫 명령 stdout `occ-check 5: OK 10`)
