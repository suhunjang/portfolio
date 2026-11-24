# Resume Step 0 — resume-preflight (검증 전용)

- 목적: resume BASE_HEAD `4b2ec3b325f400edefca0fbcfb8ff83bf739ff89`·원 phase 상태·blocker·collected·선행 산출물 확인. 파일 변경 없음.
- 15분 / 선행 없음 / 공통 원 §9 + §R1 / gate `RGATE 0`
- 허용(exact): 없음
- runtime: R0
- 추가 금지: 원 phase 파일·collected·snapshot 수정, step 40 재설정

## 작업
1. `RSNAP 0`(created/reused 아니면 중단·보고).
2. `PREFLIGHT`(§R3): HEAD가 `4b2ec3b325f400edefca0fbcfb8ff83bf739ff89`의 후손이고 그 이후 변경 경로가 resume 설계·`phases/HOO-81-portfolio-redesign-resume/**`뿐; 원 phase index.json(BASE_HEAD 기준, 이후 불변)에서 step 0~39 completed, step 40 blocked·`147` 근거; collected가 BASE_HEAD와 동일·strict 7필드·12 entry·61/78·25 pair; 선행 helper·spec·fixture 존재; baseline·plan 아직 없음. 실패 시 중단·보고(수정 시도 금지).
3. 기존 검증 재실행: `FULL`(axe는 pending 경로), `VS`.

## AC
- `PREFLIGHT && FULL && VS && RGATE 0 ''`(첫 명령 stdout `resume-preflight: OK`)
