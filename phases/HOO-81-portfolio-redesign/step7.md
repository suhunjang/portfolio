# Step 7 — axe-collect

- 예상 시간: 15분
- 실행 횟수: 수집 1회, 병합 1회, 테스트 1회, verify-scope 1회
- 선행 step: 0~6 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.1, §8.3 (실행 모드, 단계)
3. index.json에서 step 0~6이 completed인지 확인한다. 아니면 중단한다.
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

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖 전부
- helper와 그 밖의 tests 파일
- `tests/fixtures/axe-baseline.json` (다음 step에서 만든다)

## 범위

10개 시나리오 구현, 수집, 병합까지만 한다. 분류는 다음 step에서 한다.

## 작업

### 1. `axe.spec.js`

- 시나리오: page 6개, modal 2개, lightbox 2개. 모두 collector를 고정 순서로 쓴다.
- 수집 모드: `writeCollected`만 한다.
- 일반 모드
  - `baselineExists()`가 false면 `test.skip`한다. 사유: `baseline 미생성(step 8 이전)`
  - true면 다음 세 가지를 확인한다.
    - `checkRegression`이 `[]`
    - desktop-dark에서 1회 `validateBaseline`이 `[]`
    - plan이 있으면 `validateRemediationPlan(..., { coverage: false })`이 `[]`

### 2. 수집

1. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset`
2. `AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js axe-helper.spec.js`
3. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge`: 10개 파일을 검증하고 `tests/fixtures/axe-collected.json`에 쓴다.
4. 로그에 다음을 남긴다: key 수, 고유 canonical target 수, ruleId별 target 수

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset && AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js axe-helper.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge` → exit 0
- `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 통과
