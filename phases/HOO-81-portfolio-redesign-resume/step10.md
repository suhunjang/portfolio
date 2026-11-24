# Resume Step 10 — axe-classify-occ-batch-9

- 목적: §R5 batch 9(정렬 occurrence 97~108) 분류.
- 20분(2 + 12 + 6) / 선행 0~9 / 공통 §R1 / gate `RGATE 10`
- 허용(exact): 없음
- runtime: R0 + `tests/.tmp/axe-classify/occ-batch-9.json`(이 파일만)
- 추가 금지: 다른 batch·pairs 파일 수정·작성, 조사 스크립트 파일 저장, baseline·plan 작성, 사이트·helper·spec·collected 수정

## 작업
1. `RSNAP 10`
2. step 2와 같은 절차로 occurrence 97~108 → `occ-batch-9.json`.

## AC
- `OCC_CHECK 9 && FULL && VS && RGATE 10 ''`(첫 명령 stdout `occ-check 9: OK 12`)
