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
4. `verify-scope.mjs`의 `collectInput`, `evaluatePaths`, self-test를 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용된다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/scripts/verify-scope.mjs`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖 전부
- 그 밖의 tests 파일

## 작업

1. `checkGitignore(text)`
   - null이면 위반이다.
   - 끝의 `\n` 1개만 제거한 뒤 줄 배열이 7줄과 정확히 일치해야 한다.
2. `evaluateContent(input, { final })`
   - data.js 4구간: 삭제 금지, `featured: true,` 외 금지, 3줄 초과 금지. final이면 정확히 3줄.
   - index.html 3종: `Space+Grotesk`가 있어야 한다.
   - tests/.gitignore 2종: `checkGitignore`를 적용한다.
3. `evaluateScope(input, opts) = [...evaluatePaths, ...evaluateContent]`
   - CLI 기본 동작을 이 함수로 바꾼다.
   - 통과하면 `verify-scope: OK`를 출력한다.
   - `--final`을 지원한다.
4. self-test에 내용 사례를 추가한다. 경로 사례와 rename 사례는 유지한다.
   - data.js: 삭제, featured 외 줄, featured 4줄, final에서 2줄, stage 후 worktree만 원복
   - Space Grotesk: stage 후 worktree만 원복
   - gitignore: 추가, 중복, 빈 줄, 순서, 주석, CRLF
   - gitignore 끝 개행 없음 → 통과
   - gitignore index 버전만 잘못됨

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests run verify-scope:selftest && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh npm --prefix tests test`가 모두 exit 0이다.
