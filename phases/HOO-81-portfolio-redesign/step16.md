# Step 16 — axe-plan-executable

- 예상 시간: 14분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~15 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §7.2(예외 밖 콘텐츠 변경), §8.3 (step 16 실행 가능성 검사, gate, 재계획 그룹 step 생성 조건)
3. index.json에서 step 0~15가 completed인지 확인한다. 아니면 중단한다.
4. axe.js의 `Plan`, `loadPlan`, `validateRemediationPlan`, `FIX_FILES_BY_KIND`를 확인한다.
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
- step 8·12~15의 동작

## 작업

1. axe.js에 step 16 계약을 구현한다.
   - `validateRemediationExecutable(plan, baseline) → string[]` (`blocked-group:{id}`, `text-change:{id}:{target}`, `empty-fixfiles:{id}`)
   - CLI: `--check-executable [--plan <f>] [--baseline <f>]`. 오류가 있으면 첫 줄 `Harness 재계획 필요: 실행 불가 remediation 그룹`과 목록을 stderr에 출력하고 exit 1
2. axe-helper.spec.js (desktop-dark, 독립 디렉터리)
   - `{ groups: [] }` → `[]`
   - css-token 그룹(blocked false, fixFiles `[css/themes.css]`) → `[]`
   - blocked true인 css-rule 그룹 → `blocked-group:{id}`
   - text-change target을 가진 그룹(blocked true, fixFiles `[]`) → `blocked-group`, `text-change`, `empty-fixfiles` 세 오류 모두
   - 정상 그룹 + blocked 그룹 혼합 → blocked 그룹 오류만 있고 결과 배열 길이 ≥ 1 (하나라도 있으면 전체 실패)
   - 입력이 변경되지 않는다.
   - subprocess `--check-executable`
     - 빈 groups → 0
     - 실행 가능 그룹만 → 0
     - blocked 그룹 1개 → 1, stderr 첫 줄이 `Harness 재계획 필요: 실행 불가 remediation 그룹`
     - fixFiles `[]` 그룹 → 1
     - plan 없음, baseline JSON 오류 → 1

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 통과
