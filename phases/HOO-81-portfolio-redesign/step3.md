# Step 3 — content-baseline-fixture

- 예상 시간: 20분
- 실행 횟수: fixture 생성 1회, 테스트 1회, verify-scope 1회
- 선행 step: 0~2 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §3, §6, §7
3. index.json에서 step 0~2가 completed인지 확인한다. 아니면 중단한다.
4. data.js 전역 const와 index.html 정적 본문의 셀렉터를 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. BASE = `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`
8. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/scripts/make-fixtures.mjs`
- `tests/fixtures/baseline-data.json`
- `tests/fixtures/baseline-index.html`
- `tests/fixtures/content-exceptions.json`
- `tests/helpers/content.js`
- `tests/specs/content.spec.js`
- `tests/package.json` (`fixtures` script 추가만)

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖의 모든 파일
- 그 밖의 tests 파일

## 작업

1. `make-fixtures.mjs`
   - BASE 시점 data.js를 vm으로 평가해 JSON으로 저장한다.
   - BASE 시점 index.html을 저장한다.
   - `fixtures` script를 추가한다.
2. `content-exceptions.json`에 §7.2의 예외를 담는다.
3. `content.js`를 §7.3 계약대로 구현하고 JSDoc을 붙인다.
4. `content.spec.js` (6개 project, collector 고정 순서)
   - normalizeFeatured: 입력을 바꾸지 않는지, 잘못된 입력에서 throw하는지 확인한다.
   - deep-equal
   - featured 위치
   - 연락처가 비어 있는지
   - 정적 본문: §7.2 예외 외에는 BASE와 같아야 한다.
   - 렌더 개수
5. `sh tests/scripts/with-env.sh npm --prefix tests run fixtures`를 실행한다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- content.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 모두 통과
