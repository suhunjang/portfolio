# Step 29 — axe-remediation-recheck

- 예상 시간: 17분
- 실행 횟수: helper 검증 1회, 수집 1회, 병합 1회, regression·prune·coverage·executable·require-empty·no-violations 검사 각 1회, 테스트 1회, verify-scope 1회
- 선행 step: 0~28 completed. 재계획으로 추가된 `axe-remediation-*` step도 모두 completed여야 한다.

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.3 (entry key 계약, REGRESSION_GATE, step 16 실행 가능성, step 29 recheck)
3. index.json에서 선행 step이 모두 completed인지 확인한다. 아니면 중단한다.
4. `step28.md`의 gate 절차를 읽는다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact) — gate와 같다

- `tests/fixtures/axe-remediation-plan.json`: `--prune-plan` 실행 결과로만 바뀐다. 손 편집과 추가는 금지다.

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- 사이트 파일 전부
- `axe-baseline.json`, `axe-collected.json`, helper, spec

## 작업

1. step 28 작업 1~6을 같은 순서로 실행한다: COLLECT_CHAIN → REGRESSION_GATE(plan 수정 전) → `--prune-plan` → `--check-coverage` → `--check-plan` → `--check-executable`
2. `--check-plan --require-empty`로 groups가 `[]`인지 확인한다.
3. `--assert-no-violations --collected tests/.tmp/axe-current.json`으로 현재 수집 결과의 (key, target) 수가 정확히 0인지 확인한다.
   - baseline에 target이 남아 있어도 회귀 판정은 통과하는 허점이 있다. 이 검사로 그 허점을 막는다.
4. 하나라도 실패하면 중단한다.
   - 남은 그룹 또는 잔여 target을 보고한다.
   - 재계획을 요청한다.
   - plan을 임의로 비우지 않는다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset && AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge --out tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-regression --collected tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --prune-plan --collected tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-coverage --collected tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-plan && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-executable && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-plan --require-empty && sh tests/scripts/with-env.sh node tests/helpers/axe.js --assert-no-violations --collected tests/.tmp/axe-current.json && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → exit 0
