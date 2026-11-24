# Resume Step 32 — final-verification (원 step 57)

- 목적: 스크린샷 spec과 최종 통합 검증(PR 준비까지).
- 17분 / 선행 0~31 / 공통 원 §9 + §R1·§R2 no-op / gate `RGATE 32`
- 허용(exact): `tests/specs/screenshots.spec.js`
- runtime: R0 + `tests/screenshots/**`
- 추가 금지: 사이트 파일, 기존 spec·helper·fixtures·scripts·`tests/.gitignore`(실패 시 원인 step 보고·중단)

## 작업
1. `RSNAP 32` → `DI`
2. spec(§THEME `test`): 화면마다 `prepareForAxe` 후 촬영, 6 project page, desktop 대표 모달 3·lightbox·print, 모달 SVG text font-family Space Grotesk. 먼저 단독 통과.
3. AC 후 요약(원 §11.2 반영 목록, guard 통과, 원 phase step 0~39 결과, resume 0 verify-scope 호환·1 preflight·occ-batch 1~12·integrate·merge·prune 로그). exact-commit 리뷰·push·PR·SHA 동일 확인은 하네스(§R FLOW).

## AC
- `DI && W node tests/scripts/make-state-colors.mjs --check && T screenshots.spec.js design-intake.spec.js hero-layout.spec.js component-hit.spec.js state-sequence.spec.js state-colors.spec.js component-hover.spec.js verify-scope-resume.spec.js GS && W npm --prefix tests run verify-scope:selftest && AXE --assert-empty && AXE --check-plan --require-empty && FULL && VS -- --final && RGATE 32 tests/specs/screenshots.spec.js`
- final: data.js BASE→HEAD/index/worktree 각각 정확히 3줄, index→worktree 0~3줄.
