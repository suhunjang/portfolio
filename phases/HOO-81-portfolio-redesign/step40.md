# Step 40 — final-verification

- 목적: 스크린샷 spec과 최종 통합 검증(PR 준비까지만).
- 예상 16분 / 선행 0~39 / 공통 절차 설계 §15
- read-first: 설계 전체; specs(bootstrap, scope-snapshot-paths, scope-snapshot-parse, scope-snapshot-loader, scope-snapshot-state, scope-snapshot-symlink, scope-snapshot-special, scope-snapshot-identity, scope-snapshot-cli, scope-snapshot-parity, smoke, content-data, content-static, modal-regression, ui-regression, first-visit, axe-helper, axe-prepare-page, axe-prepare-modal, axe-prepare-lightbox, axe, featured, hero, structure, layout, focus-modal, focus-lightbox, print), scripts(with-env.sh, start-snapshot.py, scope-snapshot.mjs, verify-scope.mjs, make-fixtures.mjs), helpers(synthetic-repo.js 포함), fixtures(axe-baseline, axe-remediation-plan, axe-collected) 존재
- tracked 허용(exact): `tests/specs/screenshots.spec.js`
- runtime: R0 + `tests/screenshots/**`
- 금지: §15.7, 사이트 파일, 기존 spec·helper·fixtures·scripts·`tests/.gitignore`(기존 spec 실패 시 수정하지 않고 원인 step 보고·중단)

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step40`
2. `screenshots.spec.js`: 각 화면 `prepareForAxe` 후 촬영, 6 project page, desktop 대표 모달 3개·lightbox·print, 모달 SVG text font-family Space Grotesk 확인. 먼저 단독 통과(실패 시 이 파일만 수정).
3. 아래 AC 체인 실행 후 결과 요약.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- screenshots.spec.js && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope:selftest && sh tests/scripts/with-env.sh node tests/helpers/axe.js --assert-empty && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-plan --require-empty && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope -- --final && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step40.json --allow tests/specs/screenshots.spec.js` → exit 0
- final: data.js BASE→HEAD/index/worktree 각각 정확히 3줄, index→worktree 0~3줄(`GIT_DIFF_PATCH_ARGS` patch 기준).
