# Step 24 — final-verification

- 예상 시간: 12분
- 실행 횟수: self-test 1회, `--assert-empty` 1회, 테스트 1회, verify-scope `--final` 1회
- 선행 step: 0~23 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` 전체
3. index.json에서 step 0~23이 completed인지 확인한다. 아니면 중단한다.
4. 다음이 있는지 확인한다.
   - specs: smoke, content-data, content-static, interaction, first-visit, axe-helper, axe, featured, hero, structure, layout, focus-modal, focus-lightbox, print
   - fixtures: axe-baseline, axe-remediation-plan, axe-collected
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다. PR 준비까지만 한다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/specs/screenshots.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`, `tests/screenshots/**`

## 수정 금지

- 사이트 파일 전부
- 기존 spec, helper, fixtures, scripts, `tests/.gitignore`
- 실패해도 수정하지 않는다. 원인이 된 step을 보고하고 중단한다.

## 작업

1. `screenshots.spec.js`
   - 6개 project의 page 스크린샷
   - desktop에서 대표 모달 3개, lightbox, print
   - 모달 SVG text의 font-family가 Space Grotesk인지 확인
2. AC 명령을 실행하고 결과를 로그로 요약한다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests run verify-scope:selftest && sh tests/scripts/with-env.sh node tests/helpers/axe.js --assert-empty && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-plan --require-empty && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope -- --final`가 모두 exit 0이다.
- final 판정에서 data.js는 BASE→HEAD/index/worktree가 각각 정확히 3줄, index→worktree는 0~3줄이어야 한다(모두 `GIT_DIFF_PATCH_ARGS`로 수집한 patch 기준).
