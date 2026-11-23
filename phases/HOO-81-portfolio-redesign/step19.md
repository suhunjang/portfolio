# Step 19 — axe-remediation-gate

- 예상 시간: 15분
- 실행 횟수: helper 검증 1회, 수집 1회, 병합 1회, `--check-coverage` 1회, `--check-plan` 1회, 테스트 1회, verify-scope 1회
- 선행 step: 0~18 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.3 (수집 명령 순서, step 19 gate, 재계획 그룹 step 계약)
3. index.json에서 step 0~18이 completed인지 확인한다. 아니면 중단한다.
4. `axe-baseline.json`과 `axe-remediation-plan.json`을 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/fixtures/axe-remediation-plan.json`: 사라진 target과 빈 그룹을 제거하는 것만 허용한다. 추가는 금지다.

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**` (실제 `COLLECT_DIR`, `axe-current.json`)
- `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- 사이트 파일 전부
- `axe-baseline.json`, `axe-collected.json`, helper, spec

## 작업 (gate 절차 — step 20이 그대로 다시 실행한다)

1. 순차 재수집 (병렬 금지)
   1. `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js`
   2. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset`
   3. `AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js`
   4. 1과 3이 성공한 뒤 `sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge --out tests/.tmp/axe-current.json`
2. 회귀 검사: `checkRegression`을 실행한다. 오류가 있으면 즉시 중단하고 보고한다.
3. plan 재생성
   - 사라진 target을 제거하고, 빈 그룹을 삭제한다.
   - fixFiles를 다시 계산한다. 기존 값의 부분집합이어야 한다.
   - id는 유지한다.
4. coverage 검사: `sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-coverage --collected tests/.tmp/axe-current.json`
   - 현재 수집 target 전체가 남은 groups에 정확히 포함되어야 한다.
   - plan 밖의 잔여 target이 있으면 자동 편입하지 않는다. 재계획 사유로 실패시키고 중단한다.
5. 결과 로그
   - groups가 `[]`이면 `remediation 불필요`를 남긴다.
   - 그룹이 남아 있으면 `Harness 재계획 필요`와 그룹별 상세를 남긴다.
6. 재계획 계약 (하네스가 수행)
   - 그룹마다 step을 step 19와 20 사이에 둔다.
   - 소스 allowedPaths는 그룹 fixFiles만이다.
   - runtime 쓰기: `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`
   - plan은 수정하지 않는다.
   - AC: `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset && AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge --out tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-group-done {id} --collected tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`

## 완료 기준 (AC)

- 작업 1의 순차 체인이 exit 0이다.
- `sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-coverage --collected tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-plan && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`가 통과한다.
