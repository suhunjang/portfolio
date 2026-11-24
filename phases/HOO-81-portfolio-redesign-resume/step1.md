# Resume Step 1 — resume-preflight (검증 전용)

- 목적: §R4 — BASE_HEAD `4b2ec3b325f400edefca0fbcfb8ff83bf739ff89` 후손, 이후 commit 경로 허용 목록, 보호 경로 3계층(commit·index·worktree + 원 phase untracked) 불변, 원 phase 상태·blocker·collected·선행 산출물 확인. 파일 변경 없음.
- 15분 / 선행 0 / 공통 원 §9 + §R1 / gate `RGATE 1`
- 허용(exact): 없음
- runtime: R0
- 추가 금지: 원 phase·원 설계·`CLAUDE.md`·collected·snapshot 수정, step 40 재설정, 실패 시 수정 시도, `--exit-code`로 diff 판정 대체

## 작업
1. `RSNAP 1`
2. `PREFLIGHT`(§R4 블록 그대로). 보호 경로 P = `phases/HOO-81-portfolio-redesign/`, `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md`, `CLAUDE.md`, `tests/fixtures/axe-collected.json`에 대해 각각 실행:
   - (a) `git diff --no-renames --name-only 4b2ec3b325f400edefca0fbcfb8ff83bf739ff89 HEAD -- P`
   - (b) `git diff --cached --no-renames --name-only HEAD -- P`
   - (c) `git diff --no-renames --name-only -- P`
   - (c′) `git ls-files --others --exclude-standard -- phases/HOO-81-portfolio-redesign/`
   출력이 하나라도 있으면 `preflight: protected-changed:{commit|index|worktree|untracked}:{paths}`로 중단. 이어 이후 commit 경로가 resume 설계·resume phase·`tests/scripts/verify-scope.mjs`·`tests/specs/verify-scope-resume.spec.js`뿐; 원 step 0~39 completed·step 40 blocked·`147`; collected strict·12/139/61/78/25; 선행 파일(Playwright 설치 `tests/node_modules/@playwright/test/index.js`, `tests/playwright.config.js` 포함) 존재; baseline·plan 부재. 실패 시 중단·보고.
3. `FULL`(axe pending 경로), `VS`.

## AC
- `PREFLIGHT && FULL && VS && RGATE 1 ''`(첫 명령 stdout `resume-preflight: OK`)
