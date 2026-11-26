# Resume Step 13 — axe-classify-occ-batch-12

- 목적: §R5 batch 12(정렬 occurrence 111~120) 분류.
- 20분(2 + 2 + 10 + 6) / 선행 0~12 / 공통 §R1 / gate `RGATE 13`
- 허용(exact): 없음
- runtime: R0 + `tests/.tmp/axe-classify/occ-batch-12.json`, `tests/.tmp/axe-classify/server-12.json`(이 두 파일만)
- 추가 금지: 다른 batch·pairs 파일 수정·작성, 조사 스크립트 파일 저장, baseline·plan 작성, 사이트·helper·spec·config·collected 수정, 이 step이 띄우지 않은 프로세스에 신호, §R5.1 고정 골격 변경

## 작업
1. `RSNAP 13`
2. `OCC_RUN 12`(§R5.1, step 2와 같은 절차) → `occ-batch-12.json`.

## AC
- `OCC_CHECK 12 && FULL && VS && RGATE 13 ''`(첫 명령 stdout `occ-check 12: OK 10`)
