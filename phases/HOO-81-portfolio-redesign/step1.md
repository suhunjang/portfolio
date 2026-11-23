# Step 1 — scope-verifier

- 예상 시간: 20분
- 실행 횟수: self-test 1회, verify-scope 1회, 테스트 1회(웹서버 1회)
- 선행 step: 0 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 그것도 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §11.1, §11.2, §11.5, §12
3. index.json에서 step 0이 completed인지 확인한다. 아니면 중단한다.
4. 다음을 확인한다.
   - BASE에 대한 `git rev-parse`가 성공한다.
   - `index.html`에 `Space+Grotesk`가 있다.
   - `tests/.gitignore`가 정확히 7줄이다.
   - `with-env.sh`가 있다.
   - 저장소 루트의 Harness 파일 목록(`.harness/harness.lock.json`, `.harness/policy.json` 등)
5. 빌더 read-only 경로
   - `CLAUDE.md`, `docs/**`, `phases/**`
   - `.harness/**`, `.claude/**`, `.codex/**`
   - `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. git과 Harness 운영 명령(`harness --project-root . ...`)은 하네스만 실행한다. main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm과 node 명령은 모두 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/scripts/verify-scope.mjs`
- `tests/package.json`: scripts에 `verify-scope`, `verify-scope:selftest`를 추가하는 것만 허용

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`
- `tests/.npm-cache/**`
- `tests/test-results/**`
- `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖 전부
- 위 목록 외의 tests 파일

## 작업

`tests/scripts/verify-scope.mjs`를 Node 표준 라이브러리만으로 작성한다. §11.5를 그대로 구현한다.

### 1. `collectInput()`

- 층별 경로: committed, index, worktree(untracked 포함)
- `uncommittedHarness`: 하네스 소유 경로 중 다음에 나타나는 것
  - `git diff --cached --name-only HEAD`
  - `git diff --name-only HEAD`
  - untracked
- data.js diff 4종: BASE→HEAD, BASE→index, BASE→worktree, index→worktree
- index.html 3종: HEAD, index, working
- tests/.gitignore 2종: `git show :tests/.gitignore`, working. 없으면 null
- 추적 중인 runtime 경로: `git ls-files`와 `git ls-tree -r --name-only HEAD`에서 runtime 접두사로 시작하는 것
- 루트 package.json 존재 여부

### 2. 경로 분류

- 빌더 허용
  - 사이트 파일 5개
  - `tests/package.json`, `tests/package-lock.json`, `tests/.gitignore`, `tests/playwright.config.js`
  - `tests/helpers/`, `tests/specs/`, `tests/fixtures/`, `tests/scripts/` 하위
- 하네스 소유
  - 목록: `CLAUDE.md`, `pytest.ini`, `.python-version`, `.gitattributes`, `.gitignore`, `.claude/` 하위, `.codex/` 하위, `.harness/harness.lock.json`, `.harness/policy.json`, 설계 문서, 레거시 `scripts/`, `templates/`, `harness-manifest.json`
  - committed 층에서는 면제한다. `uncommittedHarness`에 있으면 위반이다.
- 하네스 런타임: 위 두 파일을 제외한 `.harness/` 하위, `.venv/`, `phases/HOO-81-portfolio-redesign/` 하위. 모든 층에서 면제한다.
- 그 밖의 경로는 위반이다.

### 3. 내용 판정

- data.js 4종
  - `-` 줄이 있으면 위반이다.
  - `featured: true,`가 아닌 `+` 줄이 있으면 위반이다.
  - `+` 줄이 3개를 넘으면 위반이다.
  - final에서는 BASE→index와 BASE→worktree의 `+` 줄이 정확히 3개가 아니면 위반이다.
- index.html 3종: 하나라도 `Space+Grotesk`가 없으면 위반이다.
- tests/.gitignore 2종: `checkGitignore(text)`로 검사한다.
  - null이면 위반이다.
  - 끝의 `\n` 1개만 제거하고, 다른 정규화는 하지 않는다.
  - `split('\n')` 결과가 `[node_modules/, .npm-cache/, .pw-browsers/, .tmp/, test-results/, playwright-report/, screenshots/]`와 길이, 순서, 값이 정확히 같아야 한다.
  - 그렇지 않으면 위반이다. 빈 줄, 중복, 주석, CRLF, 순서 변경, 추가 줄이 모두 여기에 해당한다.
- runtime 경로가 추적되면 위반이다.
- 루트 package.json이 있으면 위반이다.

### 4. CLI

- 인자 없음: 실제 저장소를 검사한다. 위반이 있으면 exit 1, 없으면 `verify-scope: OK`를 출력한다.
- `--final`: final 판정을 적용한다.
- `--self-test`: 아래 사례를 검증한다. 기대와 다르면 exit 1.
  1. 정상 → 위반 0
  2. worktree에 `docs/other.md`
  3. README 변경을 stage한 뒤 worktree만 복원 → 위반
  4. assets 추가
  5. 루트 package.json
  6. data.js 삭제 줄
  7. featured가 아닌 추가 줄
  8. featured 4줄
  9. final에서 featured 2줄
  10. data.js 금지 변경을 stage한 뒤 worktree만 복원 → 위반
  11. Space Grotesk 제거를 stage한 뒤 worktree만 복원 → 위반
  12. `CLAUDE.md` 미커밋 수정
  13. gitignore 추가 줄
  14. gitignore 중복 줄(`.tmp/` 2회) → 위반
  15. gitignore 중간 빈 줄 → 위반
  16. gitignore 순서 변경 → 위반
  17. gitignore 주석 줄 → 위반
  18. gitignore 끝 개행 없음 → 통과
  19. index 버전 gitignore만 잘못됨(working은 정상) → 위반
  20. `tests/node_modules/x` 추적
  21. committed 층에만 `scripts/harness.py` → 위반 아님
  22. `.harness/harness.lock.json` 미커밋 수정 → 위반
  23. `.harness/runtime/x.json` untracked → 위반 아님

### 5. scripts

- `verify-scope`: `node scripts/verify-scope.mjs`
- `verify-scope:selftest`: `node scripts/verify-scope.mjs --self-test`

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests run verify-scope:selftest && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh npm --prefix tests test`가 모두 exit 0
