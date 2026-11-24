# Resume Step 3 — axe-classify-batch-3

- 목적: §R4 batch 3(정렬 pair 25) 분류.
- 9분(2 + 1 + 6) / 선행 0~2 / 공통 §R1 / gate `RGATE 3`
- 허용(exact): 없음
- runtime: R0 + `tests/.tmp/axe-classify/batch-3.json`(이 파일만)
- 추가 금지: batch-1·2 수정, 조사 스크립트 파일 저장, baseline·plan 작성, 사이트·helper·spec·collected 수정

## 작업
1. `RSNAP 3`
2. step 1과 같은 절차로 pair 25 → `batch-3.json`(불일치면 `classification-inconsistent:{pair}` exit 1).

## AC
- `BATCH_CHECK 3 && FULL && VS && RGATE 3 ''`(첫 명령 stdout `batch-check 3: OK 1`)
