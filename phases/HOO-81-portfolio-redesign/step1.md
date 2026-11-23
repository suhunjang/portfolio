# Step 1 — scope-paths

- 예상 시간: 18분
- 실행 횟수: path self-test 1회, verify-scope 1회, 테스트 1회
- 선행 step: 0 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §11.1, §11.5(경로 정책, `--no-renames`), §12
3. index.json에서 step 0이 completed인지 확인한다. 아니면 중단한다.
4. BASE `rev-parse`, Harness 파일 목록, `with-env.sh`를 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 빌더와 검증 스크립트에 허용된다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/scripts/verify-scope.mjs` (신규)
- `tests/package.json` (`verify-scope`, `verify-scope:selftest` script 추가만)

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖 전부
- 위 목록 외 tests 파일

## 작업

### 1. 상수

`export const GIT_DIFF_PATH_ARGS = ['--no-renames', '--name-only']`

### 2. `export function collectInput()`

- 세 층의 경로를 모두 `GIT_DIFF_PATH_ARGS`로 수집한다.
  - committed: BASE HEAD
  - index: `--cached BASE`
  - worktree: BASE + `ls-files --others --exclude-standard`
- `uncommittedHarness`: HEAD 기준 cached diff, worktree diff, untracked. diff는 모두 `--no-renames`
- data.js diff 4종: `--no-renames --unified=0`. BASE→HEAD, BASE→index, BASE→worktree, index→worktree
- index.html blob 3종, tests/.gitignore blob 2종
- 추적 중인 runtime 경로
- 루트 package.json 존재 여부

### 3. `export function evaluatePaths(input): string[]`

§11.5의 경로 정책을 구현한다.

### 4. CLI

- 인자 없음: 경로 검사를 실행한다. 위반이 있으면 exit 1, 없으면 `verify-scope: OK (paths)`.
- `--self-test`: 아래 경로 사례를 검증한다.
  - 정상 → 0
  - worktree `docs/other.md` → 위반
  - README를 stage한 뒤 worktree만 원복 → 위반
  - assets 추가 → 위반
  - 루트 package.json → 위반
  - `CLAUDE.md` 미커밋 → 위반
  - `tests/node_modules/x` 추적 → 위반
  - committed에만 있는 `scripts/harness.py` → 허용
  - `.harness/harness.lock.json` 미커밋 → 위반
  - `.harness/runtime/x.json` untracked → 허용
  - `phases/HOO-81-portfolio-redesign/index.json` worktree → 허용
  - rename 우회 (합성 입력은 `--no-renames` 결과 형태, 즉 삭제 경로와 추가 경로가 모두 나열됨)
    - committed: `README.md` → `tests/fixtures/x.md` → README 쪽에서 위반
    - index: `assets/favicon.svg` → `tests/fixtures/f.svg` → 위반
    - worktree: `docs/superpowers/plans/2026-07-29-quiet-executive-redesign.md` → `tests/fixtures/p.md` → 위반
    - index: `.claude/settings.json` → `tests/fixtures/s.json` → 위반(uncommittedHarness)
  - `GIT_DIFF_PATH_ARGS`에 `--no-renames`가 포함되어 있다.

### 5. scripts 추가

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests run verify-scope:selftest && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh npm --prefix tests test`가 모두 exit 0이다.
