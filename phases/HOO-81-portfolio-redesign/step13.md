# Step 13 — axe-remediation-gate

- 예상 시간: 12분
- 실행 횟수: 수집 1회, 병합 1회, `--check-plan` 1회, 테스트 1회, verify-scope 1회
- 선행 step: 0~12 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.3 (step 13 gate와 재계획 계약)
3. index.json에서 step 0~12가 completed인지 확인한다. 아니면 중단한다.
4. `axe-baseline.json`과 `axe-remediation-plan.json`을 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/fixtures/axe-remediation-plan.json`
  - 사라진 target과 빈 그룹을 제거하는 것만 허용한다.
  - 추가는 금지다.

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**` (`axe-collected/`, `axe-current.json`)
- `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- 사이트 파일 전부
- `axe-baseline.json`, `axe-collected.json`, helper, spec

## 작업

1. 현재 상태를 수집한다.
   - `sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset`
   - `AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js axe-helper.spec.js`
   - `sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge tests/.tmp/axe-current.json`
2. 현재 결과에 baseline 밖의 target이 있으면 즉시 중단하고 보고한다. 앞선 step의 회귀다.
3. plan을 정리한다.
   - 현재 결과에 없는 target을 제거한다.
   - 빈 그룹을 삭제한다.
   - 남은 그룹의 `fixFiles`를 다시 계산한다. 기존 값의 부분집합이어야 한다.
4. 결과를 로그에 남긴다.
   - groups가 `[]`이면: `remediation 불필요`. step 14로 바로 진행할 수 있다.
   - 그룹이 남아 있으면: `Harness 재계획 필요`와 함께 그룹별 id, targets, fixFiles, difficulty, estMinutes, blocked를 적는다.
   - 재계획 시 하네스는 그룹마다 `axe-remediation-{id}` step을 추가한다.
     - allowedPaths는 그룹의 fixFiles로 정확히 제한한다.
     - 각 step은 20분 이하다.
     - AC는 그 그룹의 target이 사라지는 것이다.
     - blocked 그룹은 담당 구현 step을 재개한다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-plan && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`가 모두 통과한다.
