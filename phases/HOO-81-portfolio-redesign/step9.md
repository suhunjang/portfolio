# Step 9 — axe-group-done

- 예상 시간: 12분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~8 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.3 (step 9 그룹 완료 판정, 재계획 그룹 step 계약)
3. index.json에서 step 0~8이 completed인지 확인한다. 아니면 중단한다.
4. axe.js의 `MergedEntry`, `Plan`, `GROUP_ID_RE`를 확인한다.
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
- step 5~8에서 만든 동작

## 작업

1. axe.js
   - `checkGroupDone(collected, plan, groupId) → { done, remaining }`
     - 순수 함수다.
     - collected가 배열이 아니면 `Error('invalid collected')`
     - groupId 형식이 틀리거나 plan에 없으면 `Error('unknown group id: {id}')`
   - CLI: `--check-group-done <id> [--collected <f>] [--plan <f>]`
     - collected 기본값: `tests/.tmp/axe-current.json`
     - done이면 0
     - remaining이 있거나 오류면 1. remaining은 stderr에 출력한다.
2. axe-helper.spec.js (desktop-dark)
   - 그룹 target이 어느 시나리오에도 없으면 `done: true`
   - 한 target이 lightbox 시나리오에만 남아 있으면 `done: false`이고, remaining에 해당 key와 target이 들어간다.
   - 다른 그룹의 target이 남아 있는 것은 결과에 영향을 주지 않는다.
   - unknown id와 형식 오류 id는 throw한다.
   - collected가 `{}`이면 throw한다.
   - 입력이 바뀌지 않는다.
   - subprocess (독립 디렉터리 파일 사용)
     - done → 0
     - remaining 있음 → 1
     - unknown id → 1
     - collected 파일 없음 → 1

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 통과
