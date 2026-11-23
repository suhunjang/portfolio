# Step 11 — axe-collect

- 예상 시간: 15분
- 실행 횟수: helper 검증 1회, 수집 1회, 병합 1회, 일반 테스트 1회, verify-scope 1회
- 선행 step: 0~10 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.1, §8.3 (실행 모드, 수집 명령 순서, step 11)
3. index.json에서 step 0~10이 completed인지 확인한다. 아니면 중단한다.
4. axe helper API를 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/specs/axe.spec.js` (신규)
- `tests/fixtures/axe-collected.json`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**` (실제 `COLLECT_DIR` 포함)
- `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖 전부
- helper와 그 밖의 tests 파일
- `axe-baseline.json`, plan

## 작업

1. `axe.spec.js`
   - 10개 시나리오를 작성한다. collector는 고정 순서로 사용한다.
   - 수집 모드에서는 `writeCollected`만 실행한다.
   - 일반 모드에서는 `resolveBaselineMode()`를 먼저 호출한다. baseline이 없으면 기본적으로 throw로 실패한다.
     - check일 때: `checkRegression`, `validateBaseline`(desktop-dark 1회), plan이 있으면 `validateRemediationPlan`(coverage false)
     - skip일 때: `test.skip`
2. 수집 (순차, 병렬 금지)
   1. `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js`
   2. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset`
   3. `AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js`
   4. 1과 3이 성공한 뒤 `sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge`
   5. key 수, target 수, ruleId별 분포를 로그로 남긴다.
3. 최초 일반 실행
   - 옵션은 이 명령에서만 사용한다: `AXE_ALLOW_MISSING_BASELINE=1 sh tests/scripts/with-env.sh npm --prefix tests test`
   - 옵션 없는 기본 실행이 이 시점에 실패하는 것은 의도된 결과다.
   - 하네스는 아래 AC로 검증한다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset && AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge` → exit 0
- `AXE_ALLOW_MISSING_BASELINE=1 sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 통과
