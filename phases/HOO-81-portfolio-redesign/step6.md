# Step 6 — axe-baseline-tooling

- 예상 시간: 20분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~5 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.3 (helper 구성, fixture, 실행 모드)
3. index.json에서 step 0~5가 completed인지 확인한다. 아니면 중단한다.
4. step 5의 axe.js API와 테스트 통과 여부를 확인한다.
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

- `tests/.tmp/**` (subprocess 합성 파일 포함)
- `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖 전부
- 그 밖의 tests 파일
- step 5의 canonical 동작

## 작업

### 1. axe.js에 추가

import 시점에는 fixture를 읽지 않는다.

- `COLLECT_DIR`
- `EXPECTED_FILES` 10개
- `writeCollected`
- `mergeCollected`: 파일이 정확히 10개가 아니면 throw
- `baselineExists`
- `loadBaseline`: 파일이 없으면 throw
- `validateBaseline`
- `checkRegression`: 새 key나 새 target은 오류, 사라진 것은 허용, baseline은 변경하지 않음
- `validateRemediationPlan(plan, baseline, { coverage })`
- CLI
  - `--reset`
  - `--merge [out]` (기본 out: `tests/fixtures/axe-collected.json`)
  - `--assert-empty [path]`
  - `--check-plan [--coverage]`

### 2. axe-helper.spec.js에 추가 (desktop-dark)

- 스키마
  - 통과: 혼합 color-contrast
  - 거부: 합집합 불일치, fix 누락, targets 밖 target, 비어 있지 않은 text-change, 알 수 없는 kind
- 회귀
  - 새 target은 오류
  - 사라진 target은 허용
  - 실행 후 baseline이 그대로인지
- remediation plan
  - 정상 plan은 통과
  - 거부: estMinutes 21, fixFiles 불일치, target 중복, text-change인데 `blocked`가 false, `--coverage`에서 누락
- subprocess: `child_process`로 실행하고 입력은 `tests/.tmp`에 둔다.
  - `--assert-empty`: `[]` → 0. `[{}]`, `{}`, 잘못된 JSON, 파일 없음 → 1
  - `--merge`: 출력은 `tests/.tmp`. 10개 → 0, 9개 → 1, 여분 1개 → 1
  - `--reset` 후 디렉터리가 비어 있다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js` → 통과
- `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 통과
