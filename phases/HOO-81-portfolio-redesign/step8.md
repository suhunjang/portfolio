# Step 8 — axe-classify

- 예상 시간: 20분 이하. 아래 산정에서 초과가 예상되면 즉시 재계획한다.
- 실행 횟수: 조사 스크립트 수회(`tests/.tmp`), 테스트 1회, `--check-plan` 1회, verify-scope 1회
- 선행 step: 0~7 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.3 (fixture, 분류, remediation plan, 단계)
3. index.json에서 step 0~7이 completed인지 확인한다. 아니면 중단한다.
4. `tests/fixtures/axe-collected.json`이 있는지 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/fixtures/axe-baseline.json` (신규)
- `tests/fixtures/axe-remediation-plan.json` (신규)

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**` (조사용 임시 스크립트와 출력)
- `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- 사이트 파일 전부
- helper, spec, `axe-collected.json`, 그 밖의 tests 파일

## 작업

1. 시간 산정 (가장 먼저 한다)
   - 고유 canonical target을 (ruleId, 추정 출처 파일) 묶음으로 나눈다.
   - 묶음별 예상 시간 = 2분 + target 수 × 1분
   - 전체 예상 시간 = 묶음 합계 + 검증 5분
   - 결과를 로그에 남긴다.
   - 20분을 넘으면 즉시 중단한다. 파일은 쓰지 않는다. 묶음 목록을 보고하고 Harness 재계획(묶음별 classify step으로 분할)을 요청한다.
   - 위반이 0건이면 baseline은 `[]`, plan은 `{ groups: [] }`로 쓰고 6번으로 건너뛴다.
2. target을 조사한다.
   - `tests/.tmp`에 임시 Playwright 스크립트를 두고 래퍼로 실행한다.
   - 각 target의 computed color/background, `var(--토큰)` 출처, JS 렌더 영역 포함 여부, 정적 속성 여부를 확인한다.
3. `axe-baseline.json`을 만든다.
   - §8.3 스키마를 따른다.
   - target마다 `fixes`를 하나씩 둔다.
   - `fixFiles`는 합집합이다.
   - `selectors`를 보존한다.
4. `axe-remediation-plan.json`을 만든다.
   - target을 (fixFiles 동일, 난이도) 기준으로 그룹으로 묶는다.
   - 그룹마다 difficulty, estMinutes(20 이하, 넘으면 그룹을 분할), fixFiles, blocked(text-change가 있으면 true), reason을 적는다.
   - 모든 baseline target이 정확히 한 그룹에 속해야 한다.
5. 금지 사항
   - 수집 결과에 없는 target은 추가하지 않는다.
   - 이후 step에서 나올 target을 미리 넣지 않는다(자동 편입 금지).
6. 일반 모드로 확인한다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-plan --coverage && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`가 모두 통과한다.
- 이 단계부터 일반 모드에서 실제 스키마와 canonical 회귀 판정이 함께 실행된다.
