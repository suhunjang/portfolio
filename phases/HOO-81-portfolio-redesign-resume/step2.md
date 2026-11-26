# Resume Step 2 — axe-classify-occ-batch-1

- 목적: §R5 batch 1(정렬 occurrence 1~10) 분류. 이 step의 첫 `OCC_RUN`이 일반 Node helper import·config 대응 자가 검사를 겸한다.
- 20분(2 + 2 + 10 + 6) / 선행 0~1 / 공통 §R1 / gate `RGATE 2`
- 허용(exact): 없음
- runtime: R0 + `tests/.tmp/axe-classify/occ-batch-1.json`, `tests/.tmp/axe-classify/server-1.json`(이 두 파일만)
- 추가 금지: 다른 batch·pairs 파일, 조사 스크립트 파일 저장, baseline·plan 작성, 사이트·helper·spec·config·collected 수정, 이 step이 띄우지 않은 프로세스에 신호, §R5.1 고정 골격(cleanup·보호 구간·신호 처리) 변경

## 작업
1. `RSNAP 2`
2. `OCC_RUN 1`(§R5.1 골격 그대로: `W env OCC_BATCH=1 node --input-type=module -`; import·config 대조; 하나의 `try { 서버 probe·spawn·server-1.json·readiness(250ms·15000ms)·chromium.launch·occurrence 처리·occ-batch-1.json 기록 } finally { await cleanup() }`; occurrence마다 `newContext({ baseURL, viewport, colorScheme })` → `installProjectTheme(context, { project: { name } })` → `newPage` → `page.goto('/')` → `prepareForAxe(page, { scenario })` → 조사 → `context.close()`; 멱등 `cleanup()` = context·browser close(try) + 소유 서버만 SIGTERM→5000ms→SIGKILL→5000ms exit 확인(finally); SIGINT 130·SIGTERM 143은 같은 cleanup 후 exit).
3. 배치 내 같은 pair 판정 불일치면 `classification-inconsistent:{pair}` exit 1(파일 미작성, 재계획). `occ-env: import-failed|config-mismatch|port-foreign|server-not-ready|server-kill-failed`면 중단·재계획.

## AC
- `OCC_CHECK 1 && FULL && VS && RGATE 2 ''`(첫 명령 stdout `occ-check 1: OK 10`)
