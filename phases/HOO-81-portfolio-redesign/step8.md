# Step 8 — axe-remediation-plan-schema

- 예상 시간: 16분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~7 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.3 (step 8 계약, plan 규칙)
3. index.json에서 step 0~7이 completed인지 확인한다. 아니면 중단한다.
4. axe.js의 `BaselineEntry`와 `validateBaseline`을 확인한다.
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

- `tests/` 밖 전부
- 그 밖의 tests 파일, fixtures
- step 5~7에서 만든 동작

## 작업

1. axe.js에 step 8 계약을 구현한다.
   - `PLAN_PATH`, `GROUP_ID_RE`, `loadPlan`
   - `validateRemediationPlan(plan, baseline, { coverage, requireEmpty })`
   - CLI: `--check-plan [--coverage] [--require-empty] [--plan] [--baseline]`
2. axe-helper.spec.js에 추가한다 (desktop-dark).
   - id 형식
     - 통과: `color-token-1`, `a`, `x2`
     - 거부: `Group-1`, `a--b`, `-a`, `a-`, `a_b`, 빈 문자열
   - 중복 id는 거부한다.
   - 기타 규칙
     - 정상 plan은 통과한다.
     - 거부: estMinutes 21, estMinutes 0, fixFiles 불일치, 그룹 간 중복, text-change인데 blocked 아님, difficulty 이상값, coverage 누락
   - `requireEmpty`: `{ groups: [] }`는 통과하고, 그룹이 1개 있으면 `groups: expected empty` 오류다.
   - subprocess (파일은 독립 디렉터리에 둔다)
     - 정상 → 0
     - plan 없음, JSON 오류, 대문자 id, 중복 id, coverage 누락, baseline 없음 → 1
     - `--require-empty`: 빈 groups → 0, 그룹 1개 → 1
     - 스키마는 정상이어도 그룹이 남아 있으면 `--require-empty`는 1이어야 한다. 단순 schema check와 구분되는지 확인하는 사례다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 통과
