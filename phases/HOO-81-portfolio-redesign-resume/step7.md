# Resume Step 7 — axe-classify-occ-batch-6

- 목적: §R5 batch 6(정렬 occurrence 51~60) 분류.
- 20분(2 + 2 + 10 + 6) / 선행 0~6 / 공통 §R1 / gate `RGATE 7`
- 허용(exact): 없음
- runtime: R0 + `tests/.tmp/axe-classify/occ-batch-6.json`, `tests/.tmp/axe-classify/server-6.json`(이 두 파일만)
- 추가 금지: 다른 batch·pairs 파일 수정·작성, 조사 스크립트 파일 저장, baseline·plan 작성, 사이트·helper·spec·config·collected 수정, 이 step이 띄우지 않은 프로세스 종료, §R5.1 고정 골격 변경

## 작업
1. `RSNAP 7`
2. `OCC_RUN 6`(§R5.1, step 2와 같은 절차) → `occ-batch-6.json`.

## AC
- `OCC_CHECK 6 && FULL && VS && RGATE 7 ''`(첫 명령 stdout `occ-check 6: OK 10`)
