# Resume Step 12 — axe-classify-occ-batch-11

- 목적: §R5 batch 11(정렬 occurrence 121~132) 분류.
- 20분(2 + 12 + 6) / 선행 0~11 / 공통 §R1 / gate `RGATE 12`
- 허용(exact): 없음
- runtime: R0 + `tests/.tmp/axe-classify/occ-batch-11.json`(이 파일만)
- 추가 금지: 다른 batch·pairs 파일 수정·작성, 조사 스크립트 파일 저장, baseline·plan 작성, 사이트·helper·spec·collected 수정

## 작업
1. `RSNAP 12`
2. step 2와 같은 절차로 occurrence 121~132 → `occ-batch-11.json`.

## AC
- `OCC_CHECK 11 && FULL && VS && RGATE 12 ''`(첫 명령 stdout `occ-check 11: OK 12`)
