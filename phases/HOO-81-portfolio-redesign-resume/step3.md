# Resume Step 3 — axe-classify-occ-batch-2

- 목적: §R5 batch 2(정렬 occurrence 13~24) 분류.
- 20분(2 + 12 + 6) / 선행 0~2 / 공통 §R1 / gate `RGATE 3`
- 허용(exact): 없음
- runtime: R0 + `tests/.tmp/axe-classify/occ-batch-2.json`(이 파일만)
- 추가 금지: 다른 batch·pairs 파일 수정·작성, 조사 스크립트 파일 저장, baseline·plan 작성, 사이트·helper·spec·collected 수정

## 작업
1. `RSNAP 3`
2. step 2와 같은 절차로 occurrence 13~24 → `occ-batch-2.json`.

## AC
- `OCC_CHECK 2 && FULL && VS && RGATE 3 ''`(첫 명령 stdout `occ-check 2: OK 12`)
