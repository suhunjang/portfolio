# Step 7 — axe-baseline-regression

- 예상 시간: 16분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~6 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.3 (step 7 baseline 스키마·회귀 판정, fixture)
3. index.json에서 step 0~6이 completed인지 확인한다. 아니면 중단한다.
4. axe.js의 `Violation` 타입과 수집 함수를 확인한다.
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

- `tests/` 밖의 모든 파일
- 그 밖의 tests 파일
- fixtures (아직 만들지 않는다)
- step 5·6의 동작

## 작업

### 1. axe.js에 추가 (§8.3 step 7 계약)

- `BASELINE_PATH`
- `baselineExists(path = BASELINE_PATH): boolean`
- `loadBaseline(path = BASELINE_PATH): BaselineEntry[]`
  - 파일 없음, JSON 오류, 배열 아님 → throw
- `validateBaseline(entries: unknown): string[]`
  - 필수 필드가 있는지
  - fixKind가 열거값인지
  - target마다 fix가 정확히 1개이고, 그 target이 targets 안에 있는지
  - text-change이면 fixFiles가 빈 배열인지
  - fixFiles가 허용된 4개 파일의 부분집합인지
  - 항목의 fixFiles가 합집합인지
- `checkRegression(violations, baseline, scenario, project): string[]`
  - 순수 함수다. 입력을 바꾸지 않는다.
  - `new-key:{key}`, `new-target:{key}:{target}`를 반환한다.
  - 사라진 것은 허용한다.
- `assertEmptyFile(path = BASELINE_PATH): { ok, reason? }`
- CLI: `--assert-empty [path]` → ok이면 0, 아니면 1

### 2. axe-helper.spec.js에 추가 (desktop-dark)

- `validateBaseline`
  - 통과: 혼합 color-contrast (target 2개가 각각 css-token, css-rule)
  - 거부: 합집합 불일치, fix 누락, targets 밖의 target, 빈 배열이 아닌 text-change, 알 수 없는 fixKind, 허용 밖 파일
- `checkRegression`
  - 새 key → `new-key`
  - 새 target → `new-target`
  - 사라진 target → `[]`
  - 호출 전후 deep copy를 비교해 입력이 불변인지 확인한다.
- `loadBaseline`: 파일 없음, 잘못된 JSON, `{}`는 모두 throw한다. 테스트 파일은 독립 디렉터리에 둔다.
- subprocess `--assert-empty <독립 디렉터리 파일>`
  - `[]` → 0
  - `[{}]` → 1
  - `{}` → 1
  - 잘못된 JSON → 1
  - 파일 없음 → 1

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js` → 통과
- `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 통과
