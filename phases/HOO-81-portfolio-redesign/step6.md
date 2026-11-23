# Step 6 — axe-collect-tooling

- 예상 시간: 16분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~5 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.3 (helper 계약 중 step 6 수집 파일 관리, 실행 모드)
3. index.json에서 step 0~5가 completed인지 확인한다. 아니면 중단한다.
4. step 5의 axe.js API를 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/helpers/axe.js` (추가만)
- `tests/specs/axe-helper.spec.js` (추가만)

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/axe-helper-test-*/**` (테스트 전용 독립 디렉터리)
- `tests/.tmp/**`의 실행 부산물
- `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`
- 실제 `COLLECT_DIR`(`tests/.tmp/axe-collected`)에는 쓰지 않는다.

## 수정 금지

- `tests/` 밖의 모든 파일
- 그 밖의 tests 파일
- step 5 동작

## 작업

1. axe.js에 추가 (§8.3 step 6 계약)
   - `COLLECT_DIR`, `EXPECTED_FILES`
   - `resolveCollectDir(opts?) → string`
     - 우선순위: `opts.collectDir` → `AXE_COLLECT_DIR` → `COLLECT_DIR`
     - `tests/.tmp/` 밖이면 throw한다.
   - `resetCollected(opts?) → string`
   - `writeCollected(scenario, project, violations, opts?) → string`
     - 파일명이 `EXPECTED_FILES`에 없으면 throw한다.
   - `mergeCollected(opts?: { collectDir, out }) → { entries, outPath }`
     - 파일이 빠졌거나(missing) 남으면(extra) throw한다.
   - CLI
     - `--reset [--dir <d>]`
     - `--merge [--dir <d>] [--out <f>]`
     - throw가 나면 stderr에 쓰고 exit 1
2. axe-helper.spec.js에 추가 (desktop-dark)
   - 각 테스트는 `tests/.tmp/axe-helper-test-{고유}`를 만들어 쓰고, 끝나면 삭제한다.
   - `resolveCollectDir`
     - override, env, 기본값의 우선순위가 맞다.
     - `tests/.tmp` 밖 경로(예: `tests/fixtures`)는 throw한다.
   - `resetCollected` 후 디렉터리가 비어 있다.
   - `writeCollected`: 10개를 쓸 수 있고, 잘못된 scenario면 throw한다.
   - `mergeCollected`
     - 10개 → 성공 (out은 독립 디렉터리)
     - 9개 → missing으로 throw
     - 여분 1개 → extra로 throw
   - subprocess CLI (`child_process` 사용, 항상 `--dir`/`--out`을 독립 디렉터리로 지정)
     - `--reset --dir` → 0
     - `--merge` 정상 → 0
     - `--merge` 9개 → 1
     - `--dir tests/fixtures` → 1 (경로 거부)
   - 실제 수집 디렉터리 보존 검증
     - 테스트 시작 전에 실제 `COLLECT_DIR`의 존재 여부, 파일 목록, 크기, mtime을 스냅샷한다.
     - 위 reset·merge·subprocess 사례를 모두 실행한다.
     - 끝난 뒤 스냅샷이 완전히 같아야 한다.
     - `tests/fixtures/axe-collected.json`도 존재 여부와 내용이 바뀌지 않아야 한다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js` → 통과
- `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 통과
