# Step 55 — final-verification

- 목적: 스크린샷 spec과 최종 통합 검증(intake·guard·상태 색 fixture 포함, PR 준비까지만).
- 예상 17분 / 선행 0~54 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 전체; 모든 specs·scripts·helpers·fixtures 존재
- tracked 허용(exact): `tests/specs/screenshots.spec.js`
- runtime: R0 + `tests/screenshots/**`
- 금지: §15.7, 사이트 파일, 기존 spec·helper·fixtures·scripts·`tests/.gitignore`(실패 시 원인 step 보고·중단)

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step55` → `python3 -I tests/scripts/design-intake-check.py`
2. `screenshots.spec.js`: 각 화면 `prepareForAxe` 후 촬영, 6 project page, desktop 대표 모달 3개·lightbox·print, 모달 SVG text font-family Space Grotesk. 먼저 단독 통과.
3. AC 체인 후 요약(§16 반영 목록, guard 통과, step 0~11 재검증 로그). 이후 exact-commit Astra 리뷰·push·PR은 하네스가 수행한다.

## AC

- `python3 -I tests/scripts/design-intake-check.py && sh tests/scripts/with-env.sh node tests/scripts/make-state-colors.mjs --check && sh tests/scripts/with-env.sh npm --prefix tests test -- screenshots.spec.js design-intake.spec.js hero-layout.spec.js component-hit.spec.js state-sequence.spec.js state-colors.spec.js component-hover.spec.js css-parse.spec.js color-vocab.spec.js design-guard-color-rules.spec.js design-guard-color.spec.js design-guard-css.spec.js design-guard.spec.js && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope:selftest && sh tests/scripts/with-env.sh node tests/helpers/axe.js --assert-empty && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-plan --require-empty && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope -- --final && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step55.json --allow tests/specs/screenshots.spec.js` → exit 0
- final: data.js BASE→HEAD/index/worktree 각각 정확히 3줄, index→worktree 0~3줄.
