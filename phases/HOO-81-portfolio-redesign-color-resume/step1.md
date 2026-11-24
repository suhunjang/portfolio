# Color-resume Step 1 — design-wave-verify

- 존재 이유: coordinator wave 1(resume step 18~30, direct Claude worktree worker, §C4·§C5)의 canonical integration을 Harness 안에서 검증하고 전체 checkpoint를 1회 수행한다. 이 step은 worker를 실행·대기하지 않는다.
- ≤30분 / 선행 0 + coordinator wave 1 완료(`tests/.tmp/parallel/wave-1.json`, integration commit = HEAD) / 공통 원 §9 + §C1 / gate `XGATE 1`
- 허용(exact): 없음(검증 전용)
- runtime: R0
- 작업 지시서 승계(읽기 전용): `phases/HOO-81-portfolio-redesign-resume/step18.md`~`step30.md`의 허용 anchor·RED spec·AC(`REQ`·§R10 분기 포함). 내용 복사 없음.
- 추가 금지: 어떤 파일 수정, worker 재실행, 누락 보완 구현(실패면 원인 lane 보고·중단)

## 작업
1. `XSNAP 1` → `WAVE_CHECK 1`(§C6). record 없음이면 `wave-record-missing` fail-closed(파일 변경 없음).
2. 필수 산출물: `REQ 1 tests/specs/featured.spec.js,tests/specs/hero.spec.js,tests/specs/hero-layout.spec.js,tests/specs/structure.spec.js,tests/specs/layout.spec.js,tests/specs/component-hit.spec.js,tests/specs/state-sequence.spec.js,tests/specs/state-colors.spec.js,tests/specs/component-hover.spec.js,tests/specs/component-clamp.spec.js,tests/specs/focus-modal.spec.js,tests/specs/focus-lightbox.spec.js,tests/specs/print.spec.js,tests/helpers/component-state.js,tests/helpers/state-sequence.js,tests/scripts/make-state-colors.mjs,tests/fixtures/component-state-colors.json`(resume §R11 블록, stdout 접두 `required-artifacts step101: OK 17`).
3. canonical 통합 checkpoint 1회(아래 AC).

## AC
- `WAVE_CHECK 1 && REQ 1 <작업 2 목록> && DI && W node tests/scripts/make-state-colors.mjs --check && T featured.spec.js hero.spec.js hero-layout.spec.js structure.spec.js layout.spec.js component-hit.spec.js state-sequence.spec.js state-colors.spec.js component-hover.spec.js component-clamp.spec.js focus-modal.spec.js focus-lightbox.spec.js print.spec.js GS && FULL && VS && XGATE 1 ''`(첫 명령 stdout `wave-check 1: OK 6 lanes`)
