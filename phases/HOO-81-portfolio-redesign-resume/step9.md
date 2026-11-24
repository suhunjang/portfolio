# Resume Step 9 — axe-classify-occ-batch-8

- 목적: §R5 batch 8(정렬 occurrence 71~80) 분류.
- 20분(2 + 2 + 10 + 6) / 선행 0~8 / 공통 §R1 / gate `RGATE 9`
- 허용(exact): 없음
- runtime: R0 + `tests/.tmp/axe-classify/occ-batch-8.json`, `tests/.tmp/axe-classify/server-8.json`(이 두 파일만)
- 추가 금지: 다른 batch·pairs 파일 수정·작성, 조사 스크립트 파일 저장, baseline·plan 작성, 사이트·helper·spec·config·collected 수정, 이 step이 띄우지 않은 프로세스 종료, §R5.1 고정 골격 변경

## 작업
1. `RSNAP 9`
2. `OCC_RUN 8`(§R5.1, step 2와 같은 절차) → `occ-batch-8.json`.

## AC
- `OCC_CHECK 8 && FULL && VS && RGATE 9 ''`(첫 명령 stdout `occ-check 8: OK 10`)
