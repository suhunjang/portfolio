# Color-resume Step 2 — design-wave-verify

- 존재 이유: coordinator wave 1(prologue P 18 → A·B·C·D·E 병렬, direct Claude worktree worker, §C4·§C5)의 canonical integration을 git object 수준에서 검증하고, 전체 checkpoint를 1회 돈다. worker를 실행하거나 기다리지 않는다.
- 시간: agent 예상 ≤20분, Harness hard timeout 30분. gate: `XGATE 2`.
- 선행: step 0~1과 coordinator wave 1. wave 1 완료 조건은 runtime·external record가 있고 integration commit이 HEAD인 것이다.
- 공통 규칙: 원 §9 + §C1.
- 허용(exact): 없음(검증 전용)
- runtime: R0 + `tests/.tmp/parallel/idx-*`
- 작업 지시서: `phases/HOO-81-portfolio-redesign-resume/step18.md`~`step30.md`를 읽기 전용으로 승계한다.
- 추가 금지: 파일 수정, worker 재실행, 누락분 보완 구현. 실패하면 원인 lane과 직렬 재시도 대상을 보고하고 중단한다.

## 작업
1. `XSNAP 2`
2. record가 없으면 `wave-record-missing`으로 fail-closed한다. 파일은 바꾸지 않는다.
3. `PW verify-record --wave 1 --runtime tests/.tmp/parallel/wave-1.json --external <payload.runId로 정한 SCR>/record-wave-1.json`. external 경로는 runtime envelope의 `payload.runId`로 결정한다.
4. 산출물 확인: `REQ 2 tests/specs/featured.spec.js,tests/specs/hero.spec.js,tests/specs/hero-layout.spec.js,tests/specs/structure.spec.js,tests/specs/layout.spec.js,tests/specs/component-hit.spec.js,tests/specs/state-sequence.spec.js,tests/specs/state-colors.spec.js,tests/specs/component-hover.spec.js,tests/specs/component-clamp.spec.js,tests/specs/focus-modal.spec.js,tests/specs/focus-lightbox.spec.js,tests/specs/print.spec.js,tests/helpers/component-state.js,tests/helpers/state-sequence.js,tests/scripts/make-state-colors.mjs,tests/fixtures/component-state-colors.json`(resume §R11)
5. 아래 AC를 1회 실행한다. PASS한 뒤에만 coordinator가 wave 1 cleanup을 할 수 있다(§C6).

## AC
- `PW verify-record --wave 1 --runtime tests/.tmp/parallel/wave-1.json --external <SCR>/record-wave-1.json && REQ 2 <작업 4 목록> && DI && W node tests/scripts/make-state-colors.mjs --check && T featured.spec.js hero.spec.js hero-layout.spec.js structure.spec.js layout.spec.js component-hit.spec.js state-sequence.spec.js state-colors.spec.js component-hover.spec.js component-clamp.spec.js focus-modal.spec.js focus-lightbox.spec.js print.spec.js GS && FULL && VS && XGATE 2 ''`
- 첫 명령 stdout: `parallel-wave verify-record: OK wave 1 6 lanes`
