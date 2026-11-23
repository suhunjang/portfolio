# Step 17 — axe-classify

- 예상 시간: 20분 이하. 산정 결과가 20분을 넘으면 즉시 재계획한다.
- 실행 횟수: 조사 스크립트 수회, 일치·plan·실행 가능성·회귀 검사 각 1회, 테스트 1회, verify-scope 1회
- 선행 step: 0~16 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §7.2, §8.3 (entry key 계약, step 11 투영, step 13 실행 가능성, fixture, `FIX_FILES_BY_KIND`, plan, step 17)
3. index.json에서 step 0~16이 completed인지 확인한다. 아니면 중단한다.
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

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- 사이트 파일 전부
- helper, spec, `axe-collected.json`, 그 밖의 tests 파일

## 작업

1. 시간 산정 (가장 먼저)
   - 계산식: 각 묶음 (2분 + target 수 × 1분)의 합 + 5분
   - 20분을 넘으면 즉시 중단하고 재계획을 요청한다. 파일은 쓰지 않는다.
   - 위반이 0건이면 baseline은 `[]`, plan은 `{ groups: [] }`로 쓰고 5번으로 간다.
2. 조사
   - `tests/.tmp`의 임시 Playwright 스크립트를 래퍼로 실행한다. 대상 화면은 `prepareForAxe`로 준비한다.
   - 다음을 근거로 fixKind를 판별한다: computed 색상, `var(--토큰)` 출처, JS 렌더 영역 여부, 정적 속성 여부
3. `axe-baseline.json`
   - axe-collected.json의 entry마다 항목 1개를 만든다. `projectEntry` 7개 필드를 그대로 옮기고 `fixes`, `fixFiles`만 덧붙인다.
   - fixFiles는 `FIX_FILES_BY_KIND`와 정확히 같게 쓴다.
   - 항목의 fixFiles는 합집합으로 쓴다.
4. `axe-remediation-plan.json`
   - id는 kebab-case로, 서로 겹치지 않게 짓는다.
   - 그룹마다 difficulty, estMinutes(20 이하), fixFiles, blocked, reason을 채운다.
   - 모든 canonical target이 어느 한 그룹에 포함되어야 한다(coverage).
   - 자동 편입은 금지한다.
   - text-change가 필요하거나 그 밖의 이유로 blocked 그룹이 생기면 plan에 사실대로 기록한다. 이 경우 아래 AC의 `--check-executable`이 실패하므로 step은 실패로 끝나고 Harness 재계획을 요청한다. 콘텐츠 예외를 스스로 만들지 않는다.
5. 옵션 없이 기본 일반 모드로 확인한다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-baseline-match --collected tests/fixtures/axe-collected.json && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-plan --coverage && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-executable && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-regression --collected tests/fixtures/axe-collected.json && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 모두 통과. 기본 testCommand가 옵션 없이 통과해야 한다.
