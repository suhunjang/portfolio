# Step 3 — content-baseline-fixture

- 예상 시간: 20분
- 실행 횟수: fixture 생성 1회, 테스트 1회, verify-scope 1회
- 선행 step: 0~2 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md`의 §3, §6, §7 (특히 §7.3)
3. index.json에서 step 0~2가 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드에서 data.js 전역 const와 index.html 정적 본문의 셀렉터를 확인한다.
5. 다음 경로는 빌더가 수정하지 않는다: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
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
   - `git show BASE:js/data.js`를 `vm`으로 평가해 `baseline-data.json`에 저장한다.
   - `git show BASE:index.html` 결과를 `baseline-index.html`에 저장한다.
   - `fixtures` script를 추가한다.
2. `content-exceptions.json`: §7.2 값을 넣는다.
   - `kickers.base`, `kickers.final`
   - `titles.base`, `titles.final`
   - `featured.indexes` = [1, 5, 7]
   - `subsectionTitleFinal`
3. `content.js`: §7.3 계약대로 구현한다.
   - `norm(s)`
   - `readLiveData(page): Promise<BaselineData>`
   - `normalizeFeatured(data): BaselineData`
     - 입력을 바꾸지 않는다(`structuredClone`).
     - 지정 index가 아닌 곳에 featured가 있으면 throw한다.
   - `extractStatic(page): Promise<StaticContent>`
     - `navLabels`만 `sort()`한다.
     - 나머지 배열은 DOM 순서를 유지한다.
   - JSDoc typedef를 단다.
4. `content.spec.js` (6개 project)
   - normalizeFeatured
     - 호출 후 입력이 그대로인지 확인한다.
     - 금지 index에 featured가 있으면 throw하는지 확인한다.
   - live data를 normalize한 결과가 baseline과 deep-equal이다.
   - featured는 없거나 정확히 1, 5, 7이다.
   - email·phone·social이 비어 있다.
   - 정적 본문
     - baseline-index.html을 JS 비활성 상태로 `setContent`한 결과와 비교한다.
     - kickers와 sectionTitles는 base 또는 final과 정확히 같아야 한다.
     - final이면 `h3.subsection-title`이 1개다.
     - 나머지 필드는 같아야 한다.
   - 렌더 개수
     - stats 4
     - timeline = CAREER 길이
     - project-card 13
     - strengths 6
     - project-title 배열이 baseline과 같다.
   - 콘솔: `collectConsoleErrors`를 고정 순서대로 쓴다(goto 전에 등록).
5. `sh tests/scripts/with-env.sh npm --prefix tests run fixtures`를 실행한다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`가 모두 통과한다.
