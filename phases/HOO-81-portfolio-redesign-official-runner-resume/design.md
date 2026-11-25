# HOO-81 Official Runner Continuation

## Goal
HOO-107 이후 official Harness 2.0.1 경로로 historical resume step 18~30을 승계하고, color-contrast 61 occurrence와 nested-interactive 78 occurrence를 해결한다.

## Immutable scope
- Original phase step 0~39 completed/40 blocked와 resume step 0~16 completed/17 blocked evidence를 수정·삭제·재실행하지 않는다.
- 문구·수치·서체 asset/weight·정보구조(hero→Career→Projects→Strengths→About→Contact)·대표 프로젝트 3개·PROJECTS 13개 및 순서를 보존한다.
- 새 문구·섹션·이미지·아이콘·프로젝트·placeholder 실콘텐츠화를 금지한다.
- css/themes.css는 read-only다. 변경 필요 판정 시 중단·재계획한다.
- 색 변경은 검증된 color-contrast 61 occurrence를 고치는 최소 token/role 변경만 허용한다. unrelated palette redesign은 금지한다.

## Execution
- BASE_HEAD: 5a34759acf16e7beb96c415101c152d6e786c4b3
- step 0~11, 각 agent 예상 20분 이하, hard timeout 30분.
- wave A, wave B, a11y wave는 exact-file disjoint worktree lane으로 실행하고 official deterministic fan-in/retry/recovery를 사용한다. lane 실패 시 실패 lane만 fresh retry하며 partial fan-in은 금지한다.
- worker는 commit/push/merge, canonical phase index 수정, source 범위 밖 쓰기를 하지 않는다.
- menu open은 mobile-dark에서만, modal open은 6 project에서 별도 검증한다. FULL/UI/accessibility는 canonical step 9/11에서만 수행한다.

## Final gate
FULL, focused/UI, screenshots, axe 0, menu/modal, final diff 계약, verify-scope --final을 통과한다. BASE→HEAD/index/worktree 변경은 allowedPaths와 이 phase 파일뿐이어야 하고 HEAD→index와 index→worktree는 clean이어야 한다. js/data.js는 기존 3 records의 featured:true 추가만 허용한다. 구현 후 exact-commit Astra CLEAN, push, OPEN PR, tested/reviewed/pushed/PR head SHA 동일성을 확인한다.
