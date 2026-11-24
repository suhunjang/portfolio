# Resume Step 1 — axe-classify-batch-1

- 목적: §R4 batch 1(정렬 pair 1~12) 분류.
- 20분(2 + 12 + 6) / 선행 0 / 공통 §R1 / gate `RGATE 1`
- 허용(exact): 없음(tracked 변경 없음)
- runtime: R0 + `tests/.tmp/axe-classify/batch-1.json`(이 파일만 쓴다)
- 추가 금지: 다른 batch 파일, 조사 스크립트 파일 저장, baseline·plan 작성, 사이트·helper·spec·collected 수정

## 작업
1. `RSNAP 1`
2. §R4 정렬로 pair 1~12 산출 → occurrence마다 조사(`W node --input-type=module -` stdin, §THEME null-only 테마 context, `prepareForAxe`) → 판정 일치 확인(불일치면 `classification-inconsistent:{pair}` exit 1, 파일 미작성, 재계획) → `batch-1.json` 작성.

## AC
- `BATCH_CHECK 1 && FULL && VS && RGATE 1 ''`(첫 명령 stdout `batch-check 1: OK 12`)
