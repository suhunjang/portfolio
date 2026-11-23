# Step 1 — scope-verifier

- 예상 시간: 20분
- 실행 횟수: self-test 1회, verify-scope 1회, 테스트 1회(웹서버 1회)
- 선행 step: 0 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(하네스 계약 포함), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §11.1, §11.2, §11.5, §12
3. index.json에서 step 0이 completed인지 확인한다. 아니면 중단한다.
4. 다음을 확인한다.
   - `git rev-parse d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`가 성공한다.
   - `index.html`에 `Space+Grotesk`가 있다.
   - `tests/.gitignore`가 7줄이다.
   - `tests/scripts/with-env.sh`가 존재한다.
   - 저장소 루트의 하네스 managed 파일 목록
5. 다음은 read-only다.
   - `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`
   - 하네스 managed 파일: `scripts/**`, `.claude/**`, `.codex/**`, `templates/**`, `harness-manifest.json`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. git checkout·add·commit·push는 하네스만 한다. main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 모두 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/scripts/verify-scope.mjs`
- `tests/package.json` (scripts에 `verify-scope`, `verify-scope:selftest` 추가만)

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`
- `tests/.npm-cache/**`
- `tests/test-results/**`
- `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖 전부
- 위 목록 외 tests 파일

## 작업

`tests/scripts/verify-scope.mjs`를 Node 표준 라이브러리만으로 작성한다. 설계 §11.5를 그대로 구현한다.

### 1. 상수

- `BASE = d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`
- 루트는 `git rev-parse --show-toplevel`로 구한다.

### 2. `collectInput()`

- 층별 경로
  - `committed`: `git diff --name-only BASE HEAD`
  - `index`: `git diff --cached --name-only BASE`
  - `worktree`: `git diff --name-only BASE`와 untracked 파일
- `uncommittedHarness`: 하네스 소유 경로 중 다음 결과에 나타나는 것
  - `git diff --cached --name-only HEAD`
  - `git diff --name-only HEAD`
  - untracked 파일
- data.js diff 4종 (`--unified=0`)
  - `BASE HEAD`
  - `--cached BASE`
  - `BASE`
  - 인자 없음 (index→worktree)
- index.html 3종: HEAD, index, working
- tests/.gitignore 2종: index, working
- 추적 중인 runtime 경로: `git ls-files`와 `git ls-tree -r --name-only HEAD`에서 다음 접두사로 시작하는 경로
  - `tests/node_modules/`, `tests/.npm-cache/`, `tests/.pw-browsers/`, `tests/.tmp/`, `tests/test-results/`, `tests/playwright-report/`, `tests/screenshots/`
- 루트 package.json 존재 여부

### 3. `export function evaluateScope(input, { final }) => string[]`

경로 분류
- 빌더 허용
  - 사이트 5개 파일
  - `tests/package.json`, `tests/package-lock.json`, `tests/.gitignore`, `tests/playwright.config.js`
  - `tests/helpers/`, `tests/specs/`, `tests/fixtures/`, `tests/scripts/` 하위
- 하네스 소유
  - `CLAUDE.md`, `harness-manifest.json`, `pytest.ini`, `.python-version`, `.gitattributes`, `.gitignore`
  - `scripts/`, `.claude/`, `.codex/`, `templates/` 하위
  - 설계 문서
  - committed 층에서는 면제한다. `uncommittedHarness`에 있으면 위반이다.
- 하네스 런타임: `.harness/`, `.venv/`, `phases/HOO-81-portfolio-redesign/` 하위는 모든 층에서 면제한다.
- 위 분류 어디에도 속하지 않는 경로가 어느 층에든 있으면 위반이다.

내용 판정
- data.js: diff 4종 각각에 대해 다음 중 하나라도 해당하면 위반이다.
  - `-` 줄이 있다.
  - `featured: true,`가 아닌 `+` 줄이 있다.
  - `+` 줄이 4개 이상이다.
  - final인데 BASE→index나 BASE→worktree의 `+` 줄이 3개가 아니다.
- index.html: 3종 중 하나라도 `Space+Grotesk`가 없으면 위반이다.
- tests/.gitignore: 2종의 줄 집합이 7줄과 다르거나 파일이 없으면 위반이다.
- 추적 중인 runtime 경로가 있으면 위반이다.
- 루트 package.json이 있으면 위반이다.

### 4. CLI

- 인자 없음: 실제 저장소를 검사한다. 위반이 있으면 exit 1, 없으면 `verify-scope: OK`를 출력하고 exit 0.
- `--final`: final 판정으로 검사한다.
- `--self-test`: 아래 사례를 돌려 기대와 다르면 exit 1.
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
  13. gitignore에 추가 줄
  14. `tests/node_modules/x` 추적
  15. committed 층의 `scripts/harness.py` → 위반 아님

### 5. scripts 추가

- `verify-scope`: `node scripts/verify-scope.mjs`
- `verify-scope:selftest`: `node scripts/verify-scope.mjs --self-test`

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests run verify-scope:selftest && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh npm --prefix tests test` → 모두 exit 0
