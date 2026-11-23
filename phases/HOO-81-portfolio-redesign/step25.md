# Step 25 — axe-remediation-gate

- 예상 시간: 17분
- 실행 횟수: helper 검증 1회, 수집 1회, 병합 1회, `--check-regression`·`--prune-plan`·`--check-coverage`·`--check-plan`·`--check-executable` 각 1회, 테스트 1회, verify-scope 1회
- 선행 step: 0~24 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §7.2, §8.3 (entry key 계약, COLLECT_CHAIN, REGRESSION_GATE, step 13 실행 가능성, step 15 도구, step 25 gate, 재계획 그룹 step 생성 조건)
3. index.json에서 step 0~24가 completed인지 확인한다. 아니면 중단한다.
4. `axe-baseline.json`과 `axe-remediation-plan.json`을 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/fixtures/axe-remediation-plan.json`: `--prune-plan` CLI 실행 결과로만 바뀐다. 손 편집과 추가는 금지다.

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**` (실제 `COLLECT_DIR`, `axe-current.json`)
- `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- 사이트 파일 전부
- `axe-baseline.json`, `axe-collected.json`, helper, spec

## 작업 (gate 절차 — step 26이 그대로 다시 실행한다)

아래 1~6을 하나의 `&&` 체인으로 순차 실행한다. 병렬 금지. 어느 단계든 실패하면 즉시 중단하고 보고한다.

1. COLLECT_CHAIN
   1. `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js`
   2. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset`
   3. `AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js`
   4. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge --out tests/.tmp/axe-current.json`
2. REGRESSION_GATE (plan 수정 전): `sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-regression --collected tests/.tmp/axe-current.json`
   - 실패하면 plan은 건드리지 않는다.
3. plan 정리: `sh tests/scripts/with-env.sh node tests/helpers/axe.js --prune-plan --collected tests/.tmp/axe-current.json`
   - 사라진 target 제거, 빈 그룹 삭제, fixFiles 재계산(부분집합), id 유지. 추가 없음.
4. coverage: `sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-coverage --collected tests/.tmp/axe-current.json`
   - plan 밖 잔여 target이 있으면 자동 편입하지 않는다. 재계획 사유로 실패시키고 중단한다.
5. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-plan`
6. 실행 가능성: `sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-executable`
   - blocked 그룹(text-change 포함)이나 `fixFiles = []` 그룹이 하나라도 있으면 실패한다. remediation step을 만들지 않고 step 26 이후로 진행하지 않는다. Harness 재계획 사유로 보고한다.
7. 결과 로그
   - groups가 `[]`이면 `remediation 불필요`를 남긴다.
   - 그룹이 남아 있고 1~6이 모두 통과했으면 `Harness 재계획 필요`와 그룹별 상세를 남긴다.
8. 재계획 계약 (하네스가 수행)
   - 생성 조건: 6 통과, 그룹 `blocked === false`, `fixFiles.length >= 1`. 하나라도 어기면 생성 금지.
   - 그룹마다 step을 step 25와 26 사이에 둔다.
   - 소스 allowedPaths는 그룹 fixFiles만이다.
   - runtime 쓰기: `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`
   - plan은 수정하지 않는다.
   - AC: `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset && AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge --out tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-regression --collected tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-group-done {id} --collected tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset && AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge --out tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-regression --collected tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --prune-plan --collected tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-coverage --collected tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-plan && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-executable && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → exit 0
