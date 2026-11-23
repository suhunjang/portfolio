# Step 4 — scope-content

- 예상 시간: 19분
- 실행 횟수: 시작 snapshot 1회, 전체 self-test 1회, verify-scope 1회, 테스트 1회, 범위 gate 1회
- 선행 step: 0~3 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §11.1, §11.5(Git diff 인자, 내용 판정, final 규칙, 합성 테스트), §11.7
3. index.json에서 step 0~3이 completed인지 확인한다. 아니면 중단한다.
4. `verify-scope.mjs`의 `GIT_DIFF_PATH_ARGS`, `GIT_DIFF_PATCH_ARGS`, `collectInput`, `evaluatePaths`, self-test를 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령(init 포함)과 Harness 운영 명령은 하네스만 실행한다. 합성 테스트는 가짜 git 주입으로만 한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)과 §11.7 시작 snapshot 명령은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.
8. 범위 gate(§11.7): 이 step의 첫 동작은 `python3 -I tests/scripts/start-snapshot.py tests/.tmp/start-snapshot-step4.json`이다. 어떤 파일도 쓰기 전에 실행한다.

## tracked source 허용 파일 (exact)

- `tests/scripts/verify-scope.mjs`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖 전부
- 그 밖의 tests 파일
- 두 Git diff 인자 상수의 값

## 작업

1. `checkGitignore(text)`
   - null이면 위반
   - 끝의 `\n` 1개만 제거한 뒤, 정확히 7줄과 일치해야 한다.
2. `checkDataJsDiff(patchText, { requireExactly3 })`
   - 입력은 `GIT_DIFF_PATCH_ARGS`로 얻은 실제 patch 문자열이다.
   - `---`/`+++` 헤더를 제외한 삭제 줄, trim 후 `featured: true,`가 아닌 추가 줄, 3줄 초과는 위반
   - `requireExactly3`이면 정확히 3줄이어야 한다.
3. `evaluateContent(input, { final })`
   - `input.dataJsDiffs`의 4구간 patch를 그대로 `checkDataJsDiff`에 넘긴다.
   - BASE→HEAD, BASE→index, BASE→worktree: `requireExactly3: final`
   - index→worktree: 항상 `requireExactly3: false`
   - index.html 3종과 gitignore 2종도 함께 검사한다.
4. `evaluateScope = [...evaluatePaths, ...evaluateContent]`
   - CLI 기본 동작으로 쓴다. 통과하면 `verify-scope: OK`를 출력한다.
   - `--final`을 지원한다.
5. self-test에 사례를 추가한다. 기존 사례는 유지한다.
   - patch 전달 합성 테스트 (가짜 git 주입, 실제 저장소 변경 없음)
     - 가짜 git: 인자에 `GIT_DIFF_PATCH_ARGS`가 모두 있고 `js/data.js` 대상이면 `diff --git`·`@@`·`+    featured: true,` 3줄을 담은 patch를 반환한다. 인자에 `--name-only`가 있으면 `js/data.js`라는 이름만 반환한다.
     - `evaluateContent(collectInput({ git: fake }), { final: true })` → data.js 위반 0
     - 같은 patch에 `+    title: 'x',`를 추가 → 위반 1 이상 (patch 내용이 실제로 판정에 쓰인다는 증명)
     - data.js 구간을 `--name-only`로 호출하도록 바꾼 가짜 수집기 결과(`js/data.js` 문자열) → final에서 3줄 미달 위반 (이름 목록으로는 통과하지 못함을 증명)
   - data.js 위반: 삭제 줄, featured 외 줄, featured 4줄, stage 후 worktree만 원복
   - final
     - BASE→HEAD/index/worktree 각 3줄이고 index→worktree 0줄 → 위반 0
     - BASE→HEAD 0줄 → 위반
     - BASE→index 2줄 → 위반
     - index→worktree에 featured 외 줄 → 위반
   - Space Grotesk 제거를 stage한 뒤 worktree만 원복 → 위반
   - gitignore 위반: 추가 줄, 중복, 빈 줄, 순서 변경, 주석, CRLF, index 버전만 잘못됨
   - gitignore 통과: 끝 개행 없음

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests run verify-scope:selftest && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step4.json --allow tests/scripts/verify-scope.mjs` → 모두 exit 0
