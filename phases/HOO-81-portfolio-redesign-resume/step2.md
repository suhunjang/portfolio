# Resume Step 2 — axe-classify-batch-2

- 목적: §R4 batch 2(정렬 pair 13~24) 분류.
- 20분(2 + 12 + 6) / 선행 0~1 / 공통 §R1 / gate `RGATE 2`
- 허용(exact): 없음
- runtime: R0 + `tests/.tmp/axe-classify/batch-2.json`(이 파일만)
- 추가 금지: batch-1 수정, 다른 batch 파일, 조사 스크립트 파일 저장, baseline·plan 작성, 사이트·helper·spec·collected 수정

## 작업
1. `RSNAP 2`
2. step 1과 같은 절차로 pair 13~24 → `batch-2.json`(불일치면 `classification-inconsistent:{pair}` exit 1).

## AC
- `BATCH_CHECK 2 && FULL && VS && RGATE 2 ''`(첫 명령 stdout `batch-check 2: OK 12`)
