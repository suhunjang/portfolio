# Step 2 — content-baseline-fixture

- 예상 시간: 18분
- 실행 횟수: fixture 생성 1회, 테스트 1회(웹서버 1회), verify-scope 1회
- 선행 step: 0, 1 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(하네스 계약 포함), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서 두 개를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §3, §6, §7
3. index.json에서 step 0과 1이 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드에서 data.js의 전역 const와 index.html 정적 본문의 위치를 확인한다.
5. read-only 경로
   - `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`
   - 하네스 managed 파일: `scripts/**`, `.claude/**`, `.codex/**`, `templates/**`, `harness-manifest.json`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. git add·commit·push는 하네스만 한다. 빌더는 working tree만 수정한다. main 직접 변경, merge, deploy는 금지다.
7. BASE = `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`
8. 공통 실행 계약: npm·node 명령은 모두 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/scripts/make-fixtures.mjs`
- `tests/fixtures/baseline-data.json`
- `tests/fixtures/baseline-index.html`
- `tests/fixtures/content-exceptions.json`
- `tests/helpers/content.js`
- `tests/specs/content.spec.js`
- `tests/package.json` (`fixtures` script 추가만)

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`
- `tests/.npm-cache/**`
- `tests/test-results/**`
- `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖의 모든 파일
- 위 목록에 없는 tests 파일

## 작업

1. `make-fixtures.mjs`를 작성한다.
   - `git show BASE:js/data.js`의 출력 끝에 `;({PROFILE,STATS,CAREER,VIS_ACCENT,PROJECTS,STRENGTHS,SKILLS})`를 붙여 `vm.runInNewContext`로 평가한다.
   - 평가 결과를 `baseline-data.json`에 저장한다.
   - `git show BASE:index.html`의 출력을 `baseline-index.html`에 저장한다.
   - `tests/package.json`에 `fixtures` script를 추가한다.
2. `content-exceptions.json`을 만든다. 설계 §7의 값을 그대로 넣는다.
   - `kickers.base`, `kickers.final`
   - `titles.base`, `titles.final`
   - `featured.indexes`: [1, 5, 7]
   - `subsectionTitleFinal`
3. `tests/helpers/content.js`에 다음 함수를 만든다.
   - `readLiveData`
   - `normalizeFeatured`: 지정한 index 외에 featured가 있으면 throw한다.
   - `extractStatic`: 아래 항목을 공백 정규화해서 추출한다.
     - title, meta description
     - nav 라벨(정렬)
     - eyebrow, CTA
     - kicker, section-title, section-sub
     - id가 없는 about p, points, meta dt
     - contact h3·p, footer
4. `tests/specs/content.spec.js`를 작성한다. 6개 project에서 실행한다.
   - live data에 normalizeFeatured를 적용한 결과가 baseline과 deep-equal이다.
   - featured는 0개이거나, 정확히 1, 5, 7이다.
   - email, phone, social이 빈 문자열이다.
   - 정적 본문
     - baseline-index.html을 `javaScriptEnabled: false` 상태에서 `setContent`로 열어 extractStatic 결과를 현재 페이지와 비교한다.
     - kickers와 titles는 base 또는 final 중 하나와 같아야 한다.
     - final이면 `h3.subsection-title`이 정확히 1개다.
     - nav는 정렬 후 비교해서 같아야 한다.
     - 나머지 항목은 같아야 한다.
   - 렌더 개수
     - `#heroStats li` 4개
     - timeline 항목 수가 CAREER 길이와 같다.
     - project-card 13개
     - strengths 6개
     - `.project-title` 배열이 baseline과 같다.
5. `sh tests/scripts/with-env.sh npm --prefix tests run fixtures`를 실행한다. 결과 파일은 working tree에 남긴다. 커밋은 하네스가 한다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`가 모두 통과한다.
