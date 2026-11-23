# Step 14 — axe-current-checks

- 예상 시간: 16분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~13 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.3 (entry key 계약, step 14 현재 수집 결과 판정, gate, recheck, finalize, 재계획 그룹 step 계약)
3. index.json에서 step 0~13이 completed인지 확인한다. 아니면 중단한다.
4. axe.js에서 `MergedEntry`, `makeEntryKey`, `Plan`, `GROUP_ID_RE`를 확인한다.
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
- step 7~13에서 만든 동작

## 작업

1. axe.js에 step 14 계약을 구현한다.
   - `checkGroupDone(collected, plan, groupId) → { done, remaining }`
   - `checkCollectedCoverage(collected, plan) → { ok, uncovered }`: plan에 없는 target을 자동으로 편입하지 않는다.
   - `countCollectedTargets(collected) → number`: (key, target) 쌍 개수
   - CLI (`--collected` 기본값은 `tests/.tmp/axe-current.json`)
     - `--check-group-done <id>`
     - `--check-coverage`: uncovered가 있으면 `재계획 필요: plan 밖 잔여 target`을 출력하고 exit 1
     - `--assert-no-violations`: 0이 아니면 exit 1
2. axe-helper.spec.js (desktop-dark, 파일은 독립 디렉터리에 둔다)
   - `checkGroupDone`
     - 그룹 target이 사라짐 → done
     - lightbox 시나리오에만 남음 → remaining 1건 (key는 `lightbox:desktop-*:*`)
     - 다른 그룹의 잔여 target은 결과에 영향을 주지 않는다.
     - unknown id, 형식 오류 id → throw
     - collected가 `{}` → throw
   - `checkCollectedCoverage`
     - 모든 target이 groups에 포함됨 → ok
     - plan에 없는 target 1개 → uncovered 1건
     - groups가 비어 있는데 target이 1개 남음 → uncovered
     - 입력이 변경되지 않음
   - `countCollectedTargets`
     - `[]` → 0
     - target 2개인 entry 1개와 1개인 entry 1개 → 3
     - 같은 canonical target이 `page:desktop-dark:r`과 `page:desktop-light:r` 두 entry에 있음 → 2
   - subprocess
     - `--check-group-done`: done → 0, remaining → 1, unknown → 1, 파일 없음 → 1
     - `--check-coverage`: 완전 포함 → 0, 잔여 → 1, 파일 없음 → 1
     - `--assert-no-violations`: `[]` → 0, target 1개 → 1, 파일 없음 → 1
     - 회귀 허점 사례
       - baseline에 target이 남아 있고 수집 결과에도 같은 target이 남아 있는 경우
       - `checkRegression`은 `[]`를 반환해도 `--assert-no-violations`는 1이어야 한다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 통과
