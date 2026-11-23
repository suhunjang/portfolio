# Step 6 — axe-baseline

- 예상 시간: 20분
- 실행 횟수: 수집 테스트 1회, 병합 1회, 일반 테스트 1회, verify-scope 1회
- 선행 step: 0~5 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.1, §8.3 (수집, 분류 범위 확정, 분류 규칙)
3. index.json에서 step 0~5가 completed인지 확인한다. 아니면 중단한다.
4. `tests/helpers/axe.js` API를 확인하고, axe-helper.spec.js가 통과하는지 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/specs/axe.spec.js`
- `tests/fixtures/axe-baseline.json`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**` (`axe-collected/`, `axe-collected.json`)
- `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖 전부
- `tests/helpers/axe.js`를 포함한 기존 tests 파일

## 작업

### 1. `tests/specs/axe.spec.js`

시나리오
- page: 6개 project, reducedMotion reduce
- modal: desktop-dark/light, `#projectModal`
- lightbox: desktop-dark/light, `.lightbox`

모든 시나리오에서 `collectConsoleErrors`를 고정 순서로 쓴다.

모드
- 수집 모드(`AXE_COLLECT=1`): `loadBaseline`을 호출하지 않고 `writeCollected`만 한다.
- 일반 모드
  - `checkRegression(...)` 결과가 `[]`여야 한다.
  - desktop-dark에서 1회: `validateBaseline(loadBaseline())` 결과가 `[]`여야 한다.

### 2. 수집

1. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset`
2. `AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js`
3. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge` (10개 검증 포함, exit 0)

### 3. 분류 범위 확정

- 병합 결과의 key 수와 고유 canonical target 수를 로그에 출력한다.
- 고유 target이 25개를 넘으면 분류하지 않는다. 숫자를 보고하고 중단한다. 하네스가 step을 재분할한다.
- 25개 이하이면 20분 안에 분류할 수 있는 범위로 보고 진행한다.

### 4. fixture 확정

- canonical target마다 §8.3 규칙으로 `fixes` 원소(`target`, `fixKind`, `fixFiles`)를 만든다.
- 항목 `fixFiles`에는 그 합집합을 넣는다.
- `selectors`는 정보로 보존한다.
- `tests/fixtures/axe-baseline.json`에 쓴다. 위반이 없으면 `[]`이다.
- text-change target은 로그에 명시한다.

### 5. 일반 모드로 확인

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset && AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge` → exit 0
- `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 통과. 일반 모드로 실제 스키마와 canonical 회귀 판정까지 확인한다.
