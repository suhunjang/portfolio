# Step 2 — scope-paths

- 예상 시간: 18분
- 실행 횟수: path self-test 1회, verify-scope 1회, 테스트 1회
- 선행 step: 0~1 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §11.1, §11.5(Git diff 인자, 경로 정책), §12
3. index.json에서 step 0~1이 completed인지 확인한다. 아니면 중단한다.
4. BASE `rev-parse`, Harness 파일 목록, `with-env.sh`를 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령(init 포함)과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/scripts/verify-scope.mjs` (신규)
- `tests/package.json` (`verify-scope`, `verify-scope:selftest` script 추가만)

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖 전부
- 위 목록 외의 tests 파일

## 작업

1. 상수 두 개를 정의하고 export한다. 섞어 쓰지 않는다.
   - `GIT_DIFF_PATH_ARGS = ['--no-renames', '--name-only']` (경로 수집 전용)
   - `GIT_DIFF_PATCH_ARGS = ['--no-renames', '--unified=0']` (data.js patch 수집 전용)
2. `export function collectInput({ git = runGit } = {})`을 만든다.
   - `runGit(args): string`은 Git 읽기 명령만 실행한다.
   - committed, index, worktree+untracked 세 층과 `uncommittedHarness`는 `GIT_DIFF_PATH_ARGS`로 수집한다.
   - `dataJsDiffs = { baseHead, baseIndex, baseWorktree, indexWorktree }`는 `GIT_DIFF_PATCH_ARGS` + `-- js/data.js`로 수집한 실제 patch 문자열이다.
   - 그 밖에 index.html blob 3종, gitignore blob 2종, 추적 중인 runtime 경로, 루트 package.json 존재 여부를 모은다.
3. `export function evaluatePaths(input): string[]`로 §11.5 경로 정책을 구현한다.
4. CLI
   - 인자 없이 실행: 경로를 검사한다. 위반이 있으면 exit 1, 없으면 `verify-scope: OK (paths)`를 출력한다.
   - `--self-test`
     - 상수 검증: `GIT_DIFF_PATH_ARGS`와 `GIT_DIFF_PATCH_ARGS`가 위 배열과 정확히 같다.
     - 호출 기록 검증: 가짜 `git`을 주입해 호출 인자를 기록한다. 경로 층 호출은 모두 `GIT_DIFF_PATH_ARGS`를 포함하고 `--unified=0`을 포함하지 않는다. data.js 4구간 호출은 모두 `GIT_DIFF_PATCH_ARGS`를 포함하고 `--name-only`를 포함하지 않는다.
     - 정상 → 0
     - 위반으로 잡아야 하는 경우
       - worktree의 `docs/other.md`
       - README를 stage한 뒤 worktree만 원복
       - assets 추가
       - 루트 package.json
       - `CLAUDE.md` 미커밋
       - `tests/node_modules/x` 추적
       - `.harness/harness.lock.json` 미커밋
     - 허용해야 하는 경우
       - committed에만 있는 `scripts/harness.py`
       - untracked `.harness/runtime/x.json`
       - worktree의 phases index
     - rename 우회(`--no-renames` 형태)는 모두 위반
       - committed: README → tests/fixtures/x.md
       - index: assets/favicon.svg → tests/fixtures/f.svg
       - worktree: docs/superpowers/plans/... → tests/fixtures/p.md
       - index: .claude/settings.json → tests/fixtures/s.json
5. scripts를 추가한다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests run verify-scope:selftest && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh npm --prefix tests test` → 모두 exit 0
