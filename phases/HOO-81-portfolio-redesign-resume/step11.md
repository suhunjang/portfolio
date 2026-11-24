# Resume Step 11 — axe-classify-occ-batch-10

- 목적: §R5 batch 10(정렬 occurrence 109~120) 분류.
- 20분(2 + 12 + 6) / 선행 0~10 / 공통 §R1 / gate `RGATE 11`
- 허용(exact): 없음
- runtime: R0 + `tests/.tmp/axe-classify/occ-batch-10.json`(이 파일만)
- 추가 금지: 다른 batch·pairs 파일 수정·작성, 조사 스크립트 파일 저장, baseline·plan 작성, 사이트·helper·spec·collected 수정

## 작업
1. `RSNAP 11`
2. step 2와 같은 절차로 occurrence 109~120 → `occ-batch-10.json`.

## AC
- `OCC_CHECK 10 && FULL && VS && RGATE 11 ''`(첫 명령 stdout `occ-check 10: OK 12`)
