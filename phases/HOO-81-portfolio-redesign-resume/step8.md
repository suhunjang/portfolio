# Resume Step 8 — axe-classify-occ-batch-7

- 목적: §R5 batch 7(정렬 occurrence 73~84) 분류.
- 20분(2 + 12 + 6) / 선행 0~7 / 공통 §R1 / gate `RGATE 8`
- 허용(exact): 없음
- runtime: R0 + `tests/.tmp/axe-classify/occ-batch-7.json`(이 파일만)
- 추가 금지: 다른 batch·pairs 파일 수정·작성, 조사 스크립트 파일 저장, baseline·plan 작성, 사이트·helper·spec·collected 수정

## 작업
1. `RSNAP 8`
2. step 2와 같은 절차로 occurrence 73~84 → `occ-batch-7.json`.

## AC
- `OCC_CHECK 7 && FULL && VS && RGATE 8 ''`(첫 명령 stdout `occ-check 7: OK 12`)
