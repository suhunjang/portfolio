# Color-resume Step 6 — design-wave-verify

- 존재 이유: `COORD_WAVE1`(§C10)의 canonical integration을 git object 수준에서 검증하고, 18~30 전체 checkpoint를 1회 수행한다. worker를 실행하거나 기다리지 않는다.
- 시간: agent 예상 ≤20분. 근거: 명령 실행만 하고 구현은 없다. Harness hard timeout은 30분.
- 선행: 0~5와 `COORD_WAVE1` 완료. 완료 조건은 `tests/.tmp/parallel/current-wave-1.json`이 있고 integration commit이 HEAD인 것이다.
- 공통 규칙: 원 §9 + §C1
- gate: `XGATE 6`
- 허용(exact): 없음(검증 전용)
- runtime: R0 + `tests/.tmp/parallel/idx-*`
- 작업 지시서: `phases/HOO-81-portfolio-redesign-resume/step18.md`~`step30.md`를 읽기 전용으로 승계한다.
- 추가 금지: 파일 수정, worker 재실행, 누락분 보완 구현. 실패하면 실패한 spec과 `plan-retry --spec` 판정 근거를 보고하고 중단한다.

## 작업
1. `XSNAP 6`
2. pointer가 없으면 `verify-record`가 `record:missing-current`로 fail-closed한다. 파일은 바꾸지 않는다.
3. 아래 AC를 1회 실행한다. PASS한 뒤에만 `COORD_CLEANUP 1`을 할 수 있다.

## AC
- `PW verify-record --wave 1 --current && REQ 6 tests/specs/featured.spec.js,tests/specs/hero.spec.js,tests/specs/hero-layout.spec.js,tests/specs/structure.spec.js,tests/specs/layout.spec.js,tests/specs/component-hit.spec.js,tests/specs/state-sequence.spec.js,tests/specs/state-colors.spec.js,tests/specs/component-hover.spec.js,tests/specs/component-clamp.spec.js,tests/specs/focus-modal.spec.js,tests/specs/focus-lightbox.spec.js,tests/specs/print.spec.js,tests/helpers/component-state.js,tests/helpers/state-sequence.js,tests/scripts/make-state-colors.mjs,tests/fixtures/component-state-colors.json && DI && W node tests/scripts/make-state-colors.mjs --check && T featured.spec.js hero.spec.js hero-layout.spec.js structure.spec.js layout.spec.js component-hit.spec.js state-sequence.spec.js state-colors.spec.js component-hover.spec.js component-clamp.spec.js focus-modal.spec.js focus-lightbox.spec.js print.spec.js GS && FULL && VS && XGATE 6 ''`
- 첫 명령 stdout: `parallel-wave verify-record: OK wave 1 6 lanes`
- `REQ` stdout: `required-artifacts step106: OK 17`
