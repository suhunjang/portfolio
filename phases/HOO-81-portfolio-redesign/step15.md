# Step 15 — axe-regression-prune

- 예상 시간: 18분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~14 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.3 (entry key 계약, step 15 회귀 gate와 plan 정리 도구, REGRESSION_GATE, gate/recheck 절차)
3. index.json에서 step 0~14가 completed인지 확인한다. 아니면 중단한다.
4. axe.js의 `checkRegression`, `loadBaseline`, `loadPlan`, `validateRemediationPlan`을 확인한다.
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
- 실제 `tests/fixtures/axe-remediation-plan.json`에는 쓰지 않는다(아직 없음). 테스트는 독립 디렉터리 사본만 쓴다.

## 수정 금지

- `tests/` 밖 전부
- 그 밖의 tests 파일, fixtures
- step 7~14에서 만든 동작

## 작업

1. axe.js에 step 15 계약을 구현한다.
   - `checkCollectedRegression(collected, baseline) → string[]` (`bad-key:`, `new-key:`, `new-target:`)
   - `prunePlan(plan, collected, baseline) → Plan` (순수, 제거만, 추가 없음, fixFiles 재계산은 부분집합)
   - CLI
     - `--check-regression [--collected <f>] [--baseline <f>]`
     - `--prune-plan [--collected <f>] [--baseline <f>] [--plan <f>]`: 읽기 실패 또는 회귀 오류면 쓰지 않고 exit 1. 통과하면 `JSON.stringify(plan, null, 2) + '\n'`으로 쓴다.
2. axe-helper.spec.js (desktop-dark, 독립 디렉터리)
   - `checkCollectedRegression`
     - baseline과 같은 entry → `[]`
     - baseline에 없는 key → `new-key:`
     - baseline key에 없는 target → `new-target:`
     - `key`가 `makeEntryKey(entry)`와 다른 entry → `bad-key:`
     - target이 사라진 경우 → `[]`
   - `prunePlan`
     - 사라진 target 제거, 빈 그룹 삭제, fixFiles 부분집합, id 유지
     - collected에 plan 밖 target이 있어도 추가하지 않는다.
     - blocked 값을 바꾸지 않는다.
     - 입력이 변경되지 않는다.
   - subprocess `--check-regression`: 회귀 없음 → 0, new-target → 1, baseline 없음 → 1, collected 없음 → 1
   - subprocess `--prune-plan` (plan 파일 bytes 보존 self-test)
     - 실행 전 plan 파일의 sha256과 mtime을 기록한다.
     - 회귀 오류(new-target)가 있으면 → exit 1, sha256·mtime 불변
     - collected 파일 없음, baseline JSON 오류 → exit 1, sha256 불변
     - 순차 체인 `sh -c 'node axe.js --check-regression ... && node axe.js --prune-plan ...'`에서 회귀가 실패하면 → exit 1, sha256 불변
     - 회귀 없음 + 사라진 target 1개 → exit 0, 결과 plan에서 그 target이 빠지고 `validateRemediationPlan`(coverage false) 통과

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 통과
