# Resume Step 34 — final-verification (원 step 57)

- 목적: 스크린샷 spec과 최종 통합 검증(PR 준비까지).
- 17분 / 선행 0~33 / 공통 원 §9 + §R1·§R2 no-op·§R11 / gate `RGATE 34`
- 허용(exact): `tests/specs/screenshots.spec.js`
- 필수 산출물(REQ): `tests/specs/screenshots.spec.js,tests/specs/design-intake.spec.js,tests/specs/hero-layout.spec.js,tests/specs/component-hit.spec.js,tests/specs/state-sequence.spec.js,tests/specs/state-colors.spec.js,tests/specs/component-hover.spec.js,tests/specs/verify-scope-resume.spec.js,tests/helpers/component-state.js,tests/helpers/state-sequence.js,tests/scripts/make-state-colors.mjs,tests/fixtures/component-state-colors.json`
- runtime: R0 + `tests/screenshots/**`
- 추가 금지: 사이트 파일, 기존 spec·helper·fixtures·scripts·`tests/.gitignore`(실패 시 원인 step 보고·중단)

## 작업
1. `RSNAP 34` → no-op 첫 probe `REQ 34 tests/specs/screenshots.spec.js,tests/specs/design-intake.spec.js,tests/specs/hero-layout.spec.js,tests/specs/component-hit.spec.js,tests/specs/state-sequence.spec.js,tests/specs/state-colors.spec.js,tests/specs/component-hover.spec.js,tests/specs/verify-scope-resume.spec.js,tests/helpers/component-state.js,tests/helpers/state-sequence.js,tests/scripts/make-state-colors.mjs,tests/fixtures/component-state-colors.json`. PASS면 나머지 AC 실행 → 통과 시 `resume step34: no-op`. `screenshots.spec.js`만 없으면 아래 작업 후 완전한 AC 재실행; 그 밖 경로가 없으면 허용 경로 밖 → 원인 step 보고·중단.
2. `DI`. spec(§THEME `test`): 화면마다 `prepareForAxe` 후 촬영, 6 project page, desktop 대표 모달 3·lightbox·print, 모달 SVG text font-family Space Grotesk. 먼저 단독 통과.
3. AC 후 요약(원 §11.2 반영 목록, guard 통과, 원 phase step 0~39 결과, resume 0 verify-scope 호환·1 preflight 3계층·occ-batch 1~14·integrate(evidence 정확 집계)·merge·§R10 분기 로그·§R11 REQ 로그·prune 로그). exact-commit 리뷰·push·PR·SHA 동일 확인은 하네스(§R FLOW).

## AC
- `REQ 34 tests/specs/screenshots.spec.js,tests/specs/design-intake.spec.js,tests/specs/hero-layout.spec.js,tests/specs/component-hit.spec.js,tests/specs/state-sequence.spec.js,tests/specs/state-colors.spec.js,tests/specs/component-hover.spec.js,tests/specs/verify-scope-resume.spec.js,tests/helpers/component-state.js,tests/helpers/state-sequence.js,tests/scripts/make-state-colors.mjs,tests/fixtures/component-state-colors.json && DI && W node tests/scripts/make-state-colors.mjs --check && T screenshots.spec.js design-intake.spec.js hero-layout.spec.js component-hit.spec.js state-sequence.spec.js state-colors.spec.js component-hover.spec.js verify-scope-resume.spec.js GS && W npm --prefix tests run verify-scope:selftest && AXE --assert-empty && AXE --check-plan --require-empty && FULL && VS -- --final && RGATE 34 tests/specs/screenshots.spec.js`(첫 명령 stdout `required-artifacts step134: OK 12`)
- final: data.js BASE→HEAD/index/worktree 각각 정확히 3줄, index→worktree 0~3줄.
