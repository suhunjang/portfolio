# Step 57 — final-verification

- 목적: 스크린샷 spec과 최종 통합 검증(PR 준비까지).
- 17분 / 선행 0~56 / 공통 §9 / gate GATE
- 허용(exact): `tests/specs/screenshots.spec.js`
- runtime: R0 + `tests/screenshots/**`
- 추가 금지: 사이트 파일, 기존 spec·helper·fixtures·scripts·`tests/.gitignore`(실패 시 원인 step 보고·중단)

## 작업
1. `SNAP 57` → `DI`
2. spec: 화면마다 `prepareForAxe` 후 촬영, 6 project page, desktop 대표 모달 3·lightbox·print, 모달 SVG text font-family Space Grotesk. 먼저 단독 통과.
3. AC 후 요약(§11.2 반영 목록, guard 통과, step 0~11 재검증 로그). exact-commit 리뷰·push·PR은 하네스(§FLOW).

## AC
- `DI && W node tests/scripts/make-state-colors.mjs --check && T screenshots.spec.js design-intake.spec.js hero-layout.spec.js component-hit.spec.js state-sequence.spec.js state-colors.spec.js component-hover.spec.js GS && W npm --prefix tests run verify-scope:selftest && AXE --assert-empty && AXE --check-plan --require-empty && FULL && VS -- --final && GATE 57 tests/specs/screenshots.spec.js`
- final: data.js BASE→HEAD/index/worktree 각각 정확히 3줄, index→worktree 0~3줄.
