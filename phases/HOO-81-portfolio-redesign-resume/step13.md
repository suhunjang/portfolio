# Resume Step 13 — axe-classify-occ-batch-12

- 목적: §R5 batch 12(정렬 occurrence 133~139) 분류.
- 15분(2 + 7 + 6) / 선행 0~12 / 공통 §R1 / gate `RGATE 13`
- 허용(exact): 없음
- runtime: R0 + `tests/.tmp/axe-classify/occ-batch-12.json`(이 파일만)
- 추가 금지: 다른 batch·pairs 파일 수정·작성, 조사 스크립트 파일 저장, baseline·plan 작성, 사이트·helper·spec·collected 수정

## 작업
1. `RSNAP 13`
2. step 2와 같은 절차로 occurrence 133~139 → `occ-batch-12.json`.

## AC
- `OCC_CHECK 12 && FULL && VS && RGATE 13 ''`(첫 명령 stdout `occ-check 12: OK 7`)
