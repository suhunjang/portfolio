# Resume Step 2 — axe-classify-occ-batch-1

- 목적: §R5 batch 1(정렬 occurrence 1~12) 분류.
- 20분(2 + 12 + 6) / 선행 0~1 / 공통 §R1 / gate `RGATE 2`
- 허용(exact): 없음
- runtime: R0 + `tests/.tmp/axe-classify/occ-batch-1.json`(이 파일만)
- 추가 금지: 다른 batch·pairs 파일, 조사 스크립트 파일 저장, baseline·plan 작성, 사이트·helper·spec·collected 수정

## 작업
1. `RSNAP 2`
2. §R5 정렬 → occurrence 1~12 각각 그 scenario·project 맥락에서 조사(`W node --input-type=module -` stdin, §THEME null-only, `prepareForAxe`) → 배치 내 같은 pair 판정 불일치면 `classification-inconsistent:{pair}` exit 1(파일 미작성, 재계획) → `occ-batch-1.json` 작성.

## AC
- `OCC_CHECK 1 && FULL && VS && RGATE 2 ''`(첫 명령 stdout `occ-check 1: OK 12`)
