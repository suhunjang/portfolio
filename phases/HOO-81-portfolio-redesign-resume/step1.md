# Resume Step 1 — resume-preflight (검증 전용)

- 목적: §R4 — BASE_HEAD `4b2ec3b325f400edefca0fbcfb8ff83bf739ff89` 후손·허용된 이후 변경 경로·원 phase 상태·blocker·collected·선행 산출물 확인. 파일 변경 없음.
- 15분 / 선행 0 / 공통 원 §9 + §R1 / gate `RGATE 1`
- 허용(exact): 없음
- runtime: R0
- 추가 금지: 원 phase·collected·snapshot 수정, step 40 재설정, 실패 시 수정 시도

## 작업
1. `RSNAP 1`
2. `PREFLIGHT`: BASE_HEAD 이후 변경 경로가 resume 설계·resume phase·`tests/scripts/verify-scope.mjs`·`tests/specs/verify-scope-resume.spec.js`뿐; 원 phase·원 설계·`CLAUDE.md` 불변; 원 step 0~39 completed·step 40 blocked·`147`; collected 불변·strict·12/139/61/78/25; 선행 파일 존재; baseline·plan 부재. 실패 시 중단·보고.
3. `FULL`(axe pending 경로), `VS`.

## AC
- `PREFLIGHT && FULL && VS && RGATE 1 ''`(첫 명령 stdout `resume-preflight: OK`)
