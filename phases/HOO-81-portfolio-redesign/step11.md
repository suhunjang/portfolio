# Step 11 — axe-baseline-projection

- 예상 시간: 16분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~10 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.3 (entry key 계약, step 11 투영·양방향 일치, fixture)
3. index.json에서 step 0~10이 completed인지 확인한다. 아니면 중단한다.
4. axe.js의 `MergedEntry`, `BaselineEntry`, `makeEntryKey`, `loadBaseline`을 확인한다.
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

- `tests/.tmp/axe-helper-test-*/**`, `tests/.tmp/**`
- `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖 전부
- 그 밖의 tests 파일, fixtures
- step 7~10에서 만든 동작

## 작업

1. axe.js에 step 11 계약을 구현한다.
   - `PROJECTION_FIELDS`, `projectEntry`, `compareCollectedBaseline`
   - CLI: `--check-baseline-match [--collected <f>] [--baseline <f>]` (`--collected` 기본 `tests/fixtures/axe-collected.json`)
2. axe-helper.spec.js (desktop-dark, 독립 디렉터리)
   - `projectEntry`
     - baseline 항목에서 `fixes`, `fixFiles`를 버리고 7개 필드만 남긴다.
     - 미정렬·중복 targets/selectors를 정렬·중복 제거한다.
     - key 불일치, 필드 누락 → throw
   - `compareCollectedBaseline`
     - 같은 내용(baseline은 fixes 포함) → `ok`
     - collected에만 있는 entry → `missingEntries`에 key 1건, `ok` false
     - baseline에만 있는 entry → `extraEntries`에 key 1건, `ok` false
     - 같은 key에서 collected에만 있는 target → `missingTargets` 1건
     - 같은 key에서 baseline에만 있는 target → `extraTargets` 1건
     - impact 다름 → `fieldMismatches`에 `{key, field: 'impact'}`
     - selectors 다름 → `fieldMismatches`에 `{key, field: 'selectors'}`
     - 한쪽에 중복 key → throw
     - 두 입력이 변경되지 않는다.
   - subprocess `--check-baseline-match`
     - 일치 → 0
     - missing entry, extra entry, missing target, extra target, impact 불일치 각각 → 1
     - collected 파일 없음, baseline JSON 오류 → 1

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 통과
