# Color-resume Step 5 — final-verification

- 존재 이유: 통합된 최종 상태에서 전체 suite, UI·시각, 접근성, print, focus, design-intake, VS final을 1회 수행하고 PR 준비 요약을 남긴다.
- 시간: agent 예상 ≤20분, Harness hard timeout 30분. 선행 0~4. 공통 규칙: 원 §9 + §C1. gate: `XGATE 5`.
- 허용(exact): `tests/specs/screenshots.spec.js`(신규, resume step34 작업 2 기준)
- runtime: R0 + `tests/screenshots/**`
- 추가 금지: 사이트 파일, 기존 spec·helper·fixtures·scripts 수정. 실패하면 원인 wave·lane을 보고하고 중단한다.

## 작업
1. `XSNAP 5` → `DI`
2. `screenshots.spec.js`(§THEME `test`)를 작성하고 단독으로 통과시킨다.
   - 화면마다 `prepareForAxe`를 거친 뒤 촬영한다.
   - 6 project 각각의 page
   - desktop에서 대표 모달 3개, lightbox, print
   - 모달 SVG text의 font-family가 Space Grotesk인지 확인한다.
3. 아래 AC를 1회 실행한 뒤 요약을 남긴다. 요약 항목:
   - 승계 범위(원 0~39, resume 0~16)
   - wave 1 lane 결과와 integration commit
   - wave 2 rule·shard와 `HOO81_COLOR_V52_ALLOW`
   - axe 위반 0
   - 보존 항목(텍스트·숫자·서체·6 섹션·13 PROJECTS·순서·레이아웃)
- exact-commit Astra 리뷰, push, OPEN PR, tested = reviewed = pushed = PR-head SHA 확인은 §C FLOW를 따른다.

## AC
- `DI && W node tests/scripts/make-state-colors.mjs --check && T screenshots.spec.js featured.spec.js hero.spec.js hero-layout.spec.js structure.spec.js layout.spec.js component-hit.spec.js state-sequence.spec.js state-colors.spec.js component-hover.spec.js component-clamp.spec.js focus-modal.spec.js focus-lightbox.spec.js print.spec.js axe.spec.js design-intake.spec.js verify-scope-resume.spec.js parallel-wave.spec.js GS && W npm --prefix tests run verify-scope:selftest && AXE --assert-empty && AXE --check-plan --require-empty && FULL && VS -- --final && XGATE 5 tests/specs/screenshots.spec.js tests/specs/screenshots.spec.js`
- final 조건: data.js는 BASE→HEAD, index, worktree 각각에서 정확히 3줄(`featured: true,`)이고, index→worktree 차이는 0~3줄이다.
