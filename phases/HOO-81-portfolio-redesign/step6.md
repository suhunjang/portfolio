# Step 6 — axe-collect-tooling

- 예상 시간: 16분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~5 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.3 (step 6 계약, 수집 명령 순서)
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
- `tests/.tmp/**` 실행 부산물
- `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`
- 실제 `COLLECT_DIR`(`tests/.tmp/axe-collected`)에는 쓰지 않는다.

## 수정 금지

- `tests/` 밖 전부
- 그 밖의 tests 파일
- step 5 동작

## 작업

1. axe.js에 step 6 계약을 구현한다.
   - `COLLECT_DIR`, `EXPECTED_FILES`
   - `resolveCollectDir`, `resetCollected`, `writeCollected`, `mergeCollected`
   - CLI: `--reset [--dir]`, `--merge [--dir] [--out]`
2. axe-helper.spec.js에 추가한다 (desktop-dark). 각 테스트는 `tests/.tmp/axe-helper-test-{고유}` 디렉터리를 쓰고 끝나면 삭제한다.
   - `resolveCollectDir`: 우선순위가 맞는지, `tests/.tmp` 밖이면 throw하는지
   - `reset`: 실행 후 디렉터리가 비어 있다.
   - `write`: 10개를 쓸 수 있고, 잘못된 scenario면 throw한다.
   - `merge`: 10개면 성공, 9개면 missing, 여분 1개면 extra
   - subprocess CLI (항상 `--dir`/`--out`을 독립 디렉터리로 지정)
     - `--reset` → 0
     - `--merge` 정상 → 0
     - `--merge` 9개 → 1
     - `--dir tests/fixtures` → 1
   - 실제 수집 디렉터리 보존
     - 시작 전에 실제 `COLLECT_DIR`의 존재 여부, 목록, 크기, mtime을 스냅샷으로 남긴다.
     - 위 사례를 모두 실행한 뒤 스냅샷과 같은지 확인한다.
     - `tests/fixtures/axe-collected.json`도 바뀌지 않았는지 확인한다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 통과
