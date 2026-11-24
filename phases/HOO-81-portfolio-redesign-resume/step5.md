# Resume Step 5 — axe-classify-occ-batch-4

- 목적: §R5 batch 4(정렬 occurrence 37~48) 분류.
- 20분(2 + 12 + 6) / 선행 0~4 / 공통 §R1 / gate `RGATE 5`
- 허용(exact): 없음
- runtime: R0 + `tests/.tmp/axe-classify/occ-batch-4.json`(이 파일만)
- 추가 금지: 다른 batch·pairs 파일 수정·작성, 조사 스크립트 파일 저장, baseline·plan 작성, 사이트·helper·spec·collected 수정

## 작업
1. `RSNAP 5`
2. step 2와 같은 절차로 occurrence 37~48 → `occ-batch-4.json`.

## AC
- `OCC_CHECK 4 && FULL && VS && RGATE 5 ''`(첫 명령 stdout `occ-check 4: OK 12`)
