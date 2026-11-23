# Step 14 — axe-finalize

- 예상 시간: 10분
- 실행 횟수: `--assert-empty` 1회, 테스트 1회, verify-scope 1회
- 선행 step: 0~13 completed, 그리고 재계획으로 추가된 `axe-remediation-*` step이 있다면 모두 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.3 (step 14 finalize)
3. index.json에서 선행 step이 모두 completed인지 확인한다. 재계획으로 추가된 remediation step도 포함한다. 아니면 중단한다.
4. 전제 조건: `tests/fixtures/axe-remediation-plan.json`의 groups가 `[]`여야 한다. 아니면 중단하고 재계획을 요청한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/fixtures/axe-baseline.json` (`[]`로 바꾸는 것만 허용)

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- 사이트 파일 전부, helper, spec, 다른 fixture

## 작업

1. `axe-baseline.json`을 `[]`로 바꾼다.
2. 일반 모드로 axe 전체를 실행한다. baseline이 비었으므로 위반이 하나라도 있으면 실패한다.
3. 실패하면 baseline을 되돌리지 않는다. 실패한 key와 target을 보고하고 중단한 뒤 재계획을 요청한다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh node tests/helpers/axe.js --assert-empty && sh tests/scripts/with-env.sh node tests/helpers/axe.js --check-plan && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`가 모두 exit 0이다.
- 즉 빈 배열 검증과 일반 axe 전체 검사가 모두 성공해야 한다.
