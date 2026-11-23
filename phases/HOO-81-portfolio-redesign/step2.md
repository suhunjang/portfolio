# Step 2 — scope-content

- 예상 시간: 18분
- 실행 횟수: 전체 self-test 1회, verify-scope 1회, 테스트 1회
- 선행 step: 0~1 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §11.1, §11.5(내용 판정)
3. index.json에서 step 0~1이 completed인지 확인한다. 아니면 중단한다.
4. `tests/scripts/verify-scope.mjs`의 `collectInput`, `evaluatePaths`, 기존 self-test를 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/scripts/verify-scope.mjs`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖의 모든 파일
- 그 밖의 tests 파일

## 작업

### 1. `export function checkGitignore(text): string[]`

- null이면 위반이다.
- 끝의 `\n` 1개만 제거한다.
- `split('\n')` 결과가 7줄 배열과 길이·순서·값까지 정확히 같아야 한다.

### 2. `export function evaluateContent(input, { final }): string[]`

- data.js diff 4종: 각각에 대해 다음을 위반으로 본다.
  - `-` 줄이 있다.
  - `featured: true,`가 아닌 `+` 줄이 있다.
  - `+` 줄이 4개 이상이다.
  - final이면 BASE→index와 BASE→worktree가 각각 정확히 3줄이 아니다.
- index.html blob 3종: 하나라도 `Space+Grotesk`가 없으면 위반이다.
- tests/.gitignore blob 2종: 각각 `checkGitignore`로 검사한다.

### 3. `export function evaluateScope(input, opts)`

- `[...evaluatePaths(input), ...evaluateContent(input, opts)]`를 반환한다.
- CLI 기본 동작이 이 함수를 쓰도록 바꾼다. 통과하면 `verify-scope: OK`를 출력한다.
- `--final`을 지원한다.

### 4. `--self-test`에 내용 사례 추가

기존 경로 사례는 그대로 두고 아래를 추가한다.

- data.js
  - 삭제 줄
  - featured가 아닌 추가 줄
  - featured 4줄
  - final에서 featured 2줄 → 위반
  - 금지 변경을 stage한 뒤 worktree만 원복 → 위반
- Space Grotesk 제거를 stage한 뒤 worktree만 원복 → 위반
- gitignore
  - 추가 줄
  - 중복 줄
  - 중간에 빈 줄
  - 순서 변경
  - 주석
  - CRLF
  - 끝 개행 없음 → 통과
  - index 버전만 잘못된 경우 → 위반

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests run verify-scope:selftest && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh npm --prefix tests test`가 모두 exit 0
