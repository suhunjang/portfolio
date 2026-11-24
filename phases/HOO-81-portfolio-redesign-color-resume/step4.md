# Color-resume Step 4 — final-verification

- 존재 이유: 통합 최종 상태에서 전체 suite·UI·시각·접근성·print·focus·design-intake·VS final을 1회 수행하고 PR 준비 요약을 남긴다.
- ≤30분 / 선행 0~3 / 공통 원 §9 + §C1 / gate `XGATE 4`
- 허용(exact): `tests/specs/screenshots.spec.js`(신규, resume step34 작업 2 기준)
- runtime: R0 + `tests/screenshots/**`
- 추가 금지: 사이트 파일, 기존 spec·helper·fixtures·scripts 수정(실패면 원인 wave·lane 보고·중단)

## 작업
1. `XSNAP 4` → `DI`.
2. `screenshots.spec.js`(§THEME `test`): 화면마다 `prepareForAxe` 후 촬영, 6 project page, desktop 대표 모달 3·lightbox·print, 모달 SVG text font-family Space Grotesk. 단독 통과 확인.
3. 아래 AC 1회. 요약: 승계 범위(원 0~39·resume 0~16), wave 1 lane 결과·integration commit, wave 2 rule·shard·색 변경 목록(`HOO81_COLOR_V52_ALLOW`), axe 0, 보존 항목(텍스트·숫자·서체·6 섹션·13 PROJECTS·순서·레이아웃). exact-commit Astra 리뷰·push·OPEN PR·tested=reviewed=pushed=PR-head SHA 확인은 §C FLOW.

## AC
- `DI && W node tests/scripts/make-state-colors.mjs --check && T screenshots.spec.js featured.spec.js hero.spec.js hero-layout.spec.js structure.spec.js layout.spec.js component-hit.spec.js state-sequence.spec.js state-colors.spec.js component-hover.spec.js component-clamp.spec.js focus-modal.spec.js focus-lightbox.spec.js print.spec.js axe.spec.js design-intake.spec.js verify-scope-resume.spec.js GS && W npm --prefix tests run verify-scope:selftest && AXE --assert-empty && AXE --check-plan --require-empty && FULL && VS -- --final && XGATE 4 tests/specs/screenshots.spec.js tests/specs/screenshots.spec.js`
- final: data.js BASE→HEAD/index/worktree 각각 정확히 3줄(`featured: true,`), index→worktree 0~3줄.
