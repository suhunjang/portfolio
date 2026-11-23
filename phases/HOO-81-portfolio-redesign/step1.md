# Step 1 — scope-paths

- 예상 시간: 18분
- 실행 횟수: path self-test 1회, verify-scope 1회, 테스트 1회
- 선행 step: 0 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §11.1, §11.5(경로 정책), §12
3. index.json에서 step 0이 completed인지 확인한다. 아니면 중단한다.
4. 다음을 확인한다: BASE에 대한 `git rev-parse`, 저장소 루트의 Harness 파일 목록, `with-env.sh`
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령(checkout, switch, add, commit, push, reset, stash, merge, rebase, tag 등)과 Harness 운영 명령(`harness --project-root . ...`)은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 빌더와 검증 스크립트가 써도 된다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 모두 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/scripts/verify-scope.mjs` (신규)
- `tests/package.json`: `verify-scope`, `verify-scope:selftest` script 추가만 허용

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖의 모든 파일
- 위 목록 외 tests 파일

## 범위

이 step에서 하는 것
- Git 상태 수집
- 세 층(committed, index, worktree)의 경로 정책
- 네 구간 diff와 blob 수집

다음 step(scope-content)으로 넘기는 것
- data.js, index.html, tests/.gitignore의 내용 판정

## 작업

### 1. `export function collectInput()`

Node 표준 라이브러리와 Git 읽기 명령만 쓴다.

- BASE 상수와 저장소 루트(`git rev-parse --show-toplevel`)
- 세 층의 경로 목록
  - committed: `git diff --name-only BASE HEAD`
  - index: `git diff --cached --name-only BASE`
  - worktree: `git diff --name-only BASE`와 `git ls-files --others --exclude-standard`의 합집합
- `uncommittedHarness`: 아래 세 결과에 나타나는 하네스 소유 경로
  - `git diff --cached --name-only HEAD`
  - `git diff --name-only HEAD`
  - untracked 목록
- data.js diff 4종 (`--unified=0`): BASE→HEAD, BASE→index, BASE→worktree, index→worktree
- index.html blob 3종: HEAD, index(`git show :index.html`), working
- tests/.gitignore blob 2종: index, working. 없으면 null
- 추적 중인 runtime 경로: `git ls-files`와 `git ls-tree -r --name-only HEAD`에서 runtime 접두사로 시작하는 경로
- 루트 package.json 존재 여부

### 2. `export function evaluatePaths(input): string[]`

설계 §11.5의 경로 정책을 그대로 구현한다.

- 빌더 허용 경로: 사이트 파일 5개, tests 파일 4개, tests 하위 디렉터리 4개
- 하네스 소유 경로: committed 층은 면제, `uncommittedHarness`에 있으면 위반
- 하네스 런타임 경로: 면제
- 그 밖의 경로: 위반
- runtime 경로가 추적되면 위반
- 루트 package.json이 있으면 위반

### 3. CLI

- 인자 없음: `collectInput()` → `evaluatePaths()`를 실행한다. 위반이 있으면 exit 1, 없으면 `verify-scope: OK (paths)`를 출력한다.
- `--self-test`: 아래 경로 사례를 검증한다. 하나라도 기대와 다르면 exit 1.
  - 정상 → 위반 0
  - worktree `docs/other.md` → 위반
  - README 변경을 stage한 뒤 worktree만 원복 → 위반
  - assets 추가 → 위반
  - 루트 package.json → 위반
  - `CLAUDE.md` 미커밋 수정 → 위반
  - `tests/node_modules/x` 추적 → 위반
  - committed 층에만 있는 `scripts/harness.py` → 위반 아님
  - `.harness/harness.lock.json` 미커밋 수정 → 위반
  - `.harness/runtime/x.json` untracked → 위반 아님
  - `phases/HOO-81-portfolio-redesign/index.json` worktree 수정 → 위반 아님

### 4. scripts 추가

- `verify-scope`: `node scripts/verify-scope.mjs`
- `verify-scope:selftest`: `node scripts/verify-scope.mjs --self-test`

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests run verify-scope:selftest && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh npm --prefix tests test`가 모두 exit 0이다.
