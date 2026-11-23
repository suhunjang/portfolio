# Step 8 — axe-remediation-plan-schema

- 예상 시간: 16분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~7 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.3 (step 8 plan 계약, remediation plan 규칙)
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

- `tests/` 밖의 모든 파일
- 그 밖의 tests 파일, fixtures
- step 5~7의 동작

## 작업

### 1. axe.js에 추가 (§8.3 step 8 계약)

- `PLAN_PATH`
- `GROUP_ID_RE = /^[a-z0-9]+(?:-[a-z0-9]+)*$/`
- `loadPlan(path = PLAN_PATH): Plan`
  - 파일 없음, JSON 오류, 객체 아님, `groups`가 배열 아님 → throw
- `validateRemediationPlan(plan, baseline, { coverage } = {}): string[]`
  - id 형식이 `GROUP_ID_RE`에 맞는지
  - id가 고유한지
  - target이 baseline의 부분집합이고 그룹 사이에 중복이 없는지
  - fixFiles가 합집합과 같은지
  - estMinutes가 1~20 정수인지
  - difficulty가 열거값인지
  - text-change가 있으면 blocked인지
  - coverage를 요구하면 모든 baseline target이 포함되는지
  - 오류 메시지 형식은 `group[{i}].{field}: {이유}`
- CLI: `--check-plan [--coverage] [--plan <f>] [--baseline <f>]`
  - 파일 없음, 파싱 실패, 오류가 1개 이상이면 exit 1

### 2. axe-helper.spec.js에 추가 (desktop-dark)

- id 형식
  - 통과: `color-token-1`, `a`, `x2`
  - 거부: `Group-1`(대문자), `a--b`, `-a`, `a-`, `a_b`, 빈 문자열
- id 중복: 두 그룹이 같은 id를 쓰면 거부한다.
- 나머지 규칙
  - 통과: 정상 plan
  - 거부: estMinutes 21, estMinutes 0, fixFiles 불일치, 그룹 간 target 중복, text-change인데 blocked가 false, difficulty 이상값, coverage 누락
- subprocess 실패 사례: 모든 파일을 독립 디렉터리에 두고 `--plan`과 `--baseline`으로 지정한다.
  - 정상 → 0
  - plan 파일 없음 → 1
  - plan JSON 오류 → 1
  - 대문자 id → 1
  - 중복 id → 1
  - `--coverage`에서 누락 → 1
  - baseline 파일 없음 → 1

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js` → 통과
- `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 통과
