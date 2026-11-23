# Step 9 — axe-collect-tooling

- 예상 시간: 18분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~8 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.3 (entry key와 병합 단위, step 9 계약, 수집 명령 순서)
3. index.json에서 step 0~8이 completed인지 확인한다. 아니면 중단한다.
4. axe.js에 이미 있는 API를 확인한다.
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
- 실제 `COLLECT_DIR`에는 쓰지 않는다.

## 수정 금지

- `tests/` 밖 전부
- 그 밖의 tests 파일
- step 7의 동작

## 작업

1. axe.js에 step 9 계약을 구현한다.
   - `makeEntryKey({ scenario, project, ruleId })` → `${scenario}:${project}:${ruleId}`. 빈 값이나 `:` 포함 시 throw
   - `COLLECT_DIR`, `EXPECTED_FILES`
   - `resolveCollectDir`, `resetCollected`, `writeCollected`
   - `mergeCollected`: (scenario, project, ruleId)마다 entry 1개, targets·selectors 중복 제거·정렬, entries는 key 정렬, `key = makeEntryKey(entry)`
   - CLI: `--reset [--dir]`, `--merge [--dir] [--out]`
2. axe-helper.spec.js에 추가한다 (desktop-dark, 각 테스트는 독립 디렉터리 사용 후 삭제).
   - `makeEntryKey`
     - `{page, desktop-dark, color-contrast}` → `page:desktop-dark:color-contrast`
     - 빈 ruleId, `:`가 들어간 project → throw
   - 병합 단위
     - 한 파일에 같은 ruleId violation 2개, 같은 target 중복 → entry 1개, targets 중복 제거·오름차순
     - 같은 canonical target이 `page-desktop-dark`와 `page-desktop-light`에 있음 → entry 2개로 보존, 각각 key가 다름
     - 같은 target이 `page-desktop-dark`와 `modal-desktop-dark`에 있음 → entry 2개
     - 모든 entry에서 `key === makeEntryKey(entry)`
   - `resolveCollectDir`: 우선순위가 맞는지, `tests/.tmp` 밖 경로를 거부하는지
   - `reset` 후 디렉터리가 비어 있는지
   - `write`: 10개 기록, 잘못된 scenario면 throw
   - `merge`: 10개 → 성공, 9개 → missing, 여분 1개 → extra
   - subprocess CLI (모두 `--dir`/`--out` 지정)
     - reset → 0
     - merge 정상 → 0
     - merge 9개 → 1
     - `--dir tests/fixtures` → 1
   - 실제 수집 디렉터리 보존
     - 실행 전후 `COLLECT_DIR`의 스냅샷(존재 여부, 목록, 크기, mtime)이 같다.
     - `tests/fixtures/axe-collected.json`이 바뀌지 않는다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 통과
