# Step 10 — axe-collect

- 예상 시간: 15분
- 실행 횟수: helper 검증 1회, 수집 1회, 병합 1회, 일반 테스트 1회, verify-scope 1회
- 선행 step: 0~9 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.1, §8.3 (실행 모드, 수집 명령 순서, step 10)
3. index.json에서 step 0~9가 completed인지 확인한다. 아니면 중단한다.
4. axe helper API를 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/specs/axe.spec.js` (신규)
- `tests/fixtures/axe-collected.json` (병합 결과)

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**` (실제 `COLLECT_DIR` 포함)
- `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖 전부
- helper와 그 밖의 tests 파일
- `axe-baseline.json`, plan

## 작업

### 1. `axe.spec.js`

- 시나리오 10개를 만든다. collector는 고정 순서로 쓴다.
- 수집 모드: `writeCollected`만 한다.
- 일반 모드
  - 맨 앞에서 `resolveBaselineMode()`를 호출한다. baseline이 없으면 기본적으로 throw하므로 실패한다.
  - check: `checkRegression`, `validateBaseline`(desktop-dark에서 1회), plan이 있으면 `validateRemediationPlan`(coverage false)
  - skip(`AXE_ALLOW_MISSING_BASELINE=1`일 때): `test.skip`, 사유 `baseline 미생성(step 10 최초 수집 전용)`

### 2. 수집 (순차, 병렬 금지)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js`
   - helper 합성 검증과 실제 디렉터리 보존 증명
2. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset`
3. `AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js`
4. 1과 3이 모두 성공한 뒤에 `sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge`를 실행해 `tests/fixtures/axe-collected.json`을 만든다.
5. 로그에 key 수, 고유 target 수, ruleId별 분포를 남긴다.

### 3. 최초 일반 실행

- `AXE_ALLOW_MISSING_BASELINE=1` 옵션은 이 명령 하나에서만 쓴다: `AXE_ALLOW_MISSING_BASELINE=1 sh tests/scripts/with-env.sh npm --prefix tests test`
- 이 시점에 옵션 없이 기본 실행하면 실패한다. 기본 누락 실패 계약에 따른 의도된 결과다.
- 하네스는 이 step을 아래 AC로 검증한다.
- step 11에서 baseline이 생기면 기본 testCommand가 다시 통과한다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset && AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge` → exit 0
- `AXE_ALLOW_MISSING_BASELINE=1 sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 통과
