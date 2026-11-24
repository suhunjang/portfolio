# Resume Step 21 — final-verification (원 step 57)

- 목적: 스크린샷 spec과 최종 통합 검증(PR 준비까지).
- 17분 / 선행 0~20 / 공통 원 §9 + §R1 / gate `RGATE 21`
- 허용(exact): `tests/specs/screenshots.spec.js`
- runtime: R0 + `tests/screenshots/**`
- 추가 금지: 사이트 파일, 기존 spec·helper·fixtures·scripts·`tests/.gitignore`(실패 시 원인 step 보고·중단)

## 작업
1. `RSNAP 21` → `DI`
2. spec(§THEME `test`): 화면마다 `prepareForAxe` 후 촬영, 6 project page, desktop 대표 모달 3·lightbox·print, 모달 SVG text font-family Space Grotesk. 먼저 단독 통과.
3. AC 후 요약(원 §11.2 반영 목록, guard 통과, 원 phase step 0~39 결과·resume 0 preflight·batch 1~3·merge 로그). exact-commit 리뷰·push·PR은 하네스(§R FLOW).

## AC
- `DI && W node tests/scripts/make-state-colors.mjs --check && T screenshots.spec.js design-intake.spec.js hero-layout.spec.js component-hit.spec.js state-sequence.spec.js state-colors.spec.js component-hover.spec.js GS && W npm --prefix tests run verify-scope:selftest && AXE --assert-empty && AXE --check-plan --require-empty && FULL && VS -- --final && RGATE 21 tests/specs/screenshots.spec.js`
- final: data.js BASE→HEAD/index/worktree 각각 정확히 3줄, index→worktree 0~3줄.
