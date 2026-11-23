# Step 3 — content-data-baseline

- 예상 시간: 15분
- 실행 횟수: fixture 생성 1회, content-data spec 2회, 전체 테스트 1회, verify-scope 1회
- 선행 step: 0~2 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §3, §7.1, §7.2-1, §7.3 (readLiveData, normalizeFeatured)
3. index.json에서 step 0~2가 completed인지 확인한다. 아니면 중단한다.
4. data.js 전역 const 목록을 확인한다.
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
- `tests/helpers/content.js`: 신규. `norm`, `readLiveData`, `normalizeFeatured`만 둔다.
- `tests/specs/content-data.spec.js`
- `tests/package.json`: `fixtures` script 추가만

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖의 모든 파일
- 그 밖의 tests 파일
- `extractStatic`과 정적 본문 비교 (step 4에서 한다)

## 작업

1. `make-fixtures.mjs`
   - `git show BASE:js/data.js`를 vm으로 평가해 `baseline-data.json`에 저장한다.
   - `git show BASE:index.html`을 `baseline-index.html`에 저장한다. 이 파일은 step 4에서 쓴다.
   - `fixtures` script를 추가하고 실행한다.
2. `content.js`
   - `norm`
   - `readLiveData(page): Promise<BaselineData>`
   - `normalizeFeatured(data): BaselineData`
     - 입력을 바꾸지 않는다(structuredClone).
     - featured는 index 1, 5, 7에서만 허용한다.
     - 다른 index에 있거나 값이 true가 아니면 throw한다.
   - JSDoc typedef를 단다.
3. `content-data.spec.js` (6개 project, collector 고정 순서)
   - normalizeFeatured
     - 호출 후 입력이 그대로인지 deep copy와 비교한다.
     - 금지 index에 featured가 있으면 throw하는지 확인한다.
   - `normalizeFeatured(await readLiveData(page))`가 `baseline-data.json`과 deep-equal이다.
   - featured는 없거나 정확히 1, 5, 7에만 있다.
   - email·phone·social이 빈 값이다.
   - 렌더 개수
     - stats 4
     - timeline = CAREER 길이
     - project-card 13
     - strengths 6
     - project-title 배열 = baseline

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- content-data.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 모두 통과
