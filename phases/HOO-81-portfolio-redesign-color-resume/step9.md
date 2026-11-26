# Color-resume Step 9 — final-verification

- 존재 이유: 통합된 최종 상태에서 전체 suite, UI·시각, 접근성, print, focus, design-intake, VS final을 1회 수행하고 PR 준비 요약을 남긴다.
- 시간: agent 예상 ≤20분. 근거: spec 1개 작성과 명령 실행. Harness hard timeout은 30분.
- 선행: 0~8
- 공통 규칙: 원 §9 + §C1
- gate: `XGATE 9`
- 허용(exact): `tests/specs/screenshots.spec.js`(신규, resume step34 작업 2 기준)
- runtime: R0 + `tests/screenshots/**`
- 추가 금지: 사이트 파일, 기존 spec·helper·fixtures·scripts 수정. 실패하면 원인 wave·lane을 보고하고 중단한다.

## 작업
1. `XSNAP 9` → `DI`
2. `screenshots.spec.js`(§THEME `test`)를 작성하고 단독으로 통과시킨다.
   - 각 화면은 `prepareForAxe` 후에 찍는다.
   - 6 project의 page를 찍는다.
   - desktop에서 대표 모달 3개, lightbox, print를 찍는다.
   - 모달 SVG text의 font-family가 Space Grotesk인지 확인한다.
3. AC를 1회 실행한다.
4. 요약을 남긴다. 담을 내용:
   - 승계: 원 0~39, resume 0~16
   - wave 1: lane·attempt 결과와 integration commit
   - wave 2: rule·shard와 `HOO81_COLOR_V52_ALLOW`
   - axe 위반 0
   - 보존 항목
   - Astra v59 대응(§C11)
5. exact-commit Astra, push, OPEN PR, SHA 동일 확인은 §C FLOW를 따른다.

## AC
- `DI && W node tests/scripts/make-state-colors.mjs --check && T screenshots.spec.js featured.spec.js hero.spec.js hero-layout.spec.js structure.spec.js layout.spec.js component-hit.spec.js state-sequence.spec.js state-colors.spec.js component-hover.spec.js component-clamp.spec.js focus-modal.spec.js focus-lightbox.spec.js print.spec.js axe.spec.js design-intake.spec.js verify-scope-resume.spec.js parallel-wave.spec.js parallel-wave-contract.spec.js parallel-wave-anchor.spec.js parallel-wave-run.spec.js parallel-wave-record.spec.js parallel-wave-manifest.spec.js GS && W npm --prefix tests run verify-scope:selftest && AXE --assert-empty && AXE --check-plan --require-empty && FULL && VS -- --final && XGATE 9 tests/specs/screenshots.spec.js tests/specs/screenshots.spec.js`
- final 조건:
  - `js/data.js`는 BASE→HEAD, index, worktree 각각에서 정확히 3줄(`featured: true,`)이다.
  - index→worktree 차이는 0~3줄이다.
