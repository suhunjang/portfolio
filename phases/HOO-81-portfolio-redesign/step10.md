# Step 10 — axe-classify

- 예상 시간: 20분 이하. 산정 결과 이를 넘으면 즉시 재계획한다.
- 실행 횟수: 조사 스크립트 수회(`tests/.tmp`), 테스트 1회, `--check-plan` 1회, verify-scope 1회
- 선행 step: 0~9 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.3 (fixture, 분류, plan, 단계)
3. index.json에서 step 0~9가 completed인지 확인한다. 아니면 중단한다.
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

- `tests/.tmp/**`
- `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- 사이트 파일 전부
- helper, spec, `axe-collected.json`, 그 밖의 tests 파일

## 작업

1. 시간 산정 (가장 먼저)
   - target을 묶음으로 나눈다.
   - 예상 시간 = 묶음마다 (2분 + target 수 × 1분)을 합하고 5분을 더한다.
   - 결과를 로그에 남긴다.
   - 20분을 넘으면 즉시 중단한다. 파일은 쓰지 않는다. 묶음을 보고하고 재계획을 요청한다.
   - 위반이 0건이면 baseline `[]`, plan `{ groups: [] }`를 쓰고 6번으로 간다.
2. target 조사: `tests/.tmp`의 임시 Playwright 스크립트를 래퍼로 실행해 출처를 판별한다.
   - computed 색상
   - `var(--토큰)` 출처
   - JS 렌더 영역 여부
   - 정적 속성 여부
3. `axe-baseline.json`: §8.3 스키마를 따른다.
   - target마다 fixes 1개
   - 항목 fixFiles는 합집합
   - selectors 보존
4. `axe-remediation-plan.json`
   - (같은 fixFiles, 난이도) 기준으로 그룹을 만든다.
   - 그룹마다 다음을 채운다.
     - `id`: 소문자 kebab-case, 고유. 예: `contrast-token-1`
     - `difficulty`
     - `estMinutes`: 20 이하. 넘으면 그룹을 분할한다.
     - `fixFiles`, `blocked`, `reason`
   - 모든 target이 정확히 한 그룹에 속해야 한다.
5. 금지
   - 수집 결과에 없는 target을 추가하지 않는다.
   - 자동으로 편입하지 않는다.
6. 일반 모드로 확인한다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-plan --coverage && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 모두 통과
