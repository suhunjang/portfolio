# Step 1 — scope-verifier

- 예상 시간: 15분
- 실행 횟수: self-test 1회, verify-scope 1회, 테스트 1회
- 선행 step: 0 completed

## 공통: 시작 전 필수 확인 (read-first)

1. `README.md`를 읽는다. `CLAUDE.md` 또는 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서 두 개를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md`: §11 범위 검사, §12
3. index.json에서 step 0이 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드에서 다음을 확인한다.
   - `index.html` Google Fonts 링크에 `Space+Grotesk`가 있다.
   - `js/data.js`의 PROJECTS index 1, 5, 7 제목
   - `git rev-parse d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`가 성공한다.
5. `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`는 읽기 전용이다. 문서 변경은 하네스만 한다.
6. main 직접 변경, merge, deploy는 금지다.

## 허용 파일 (exact)

- `tests/scripts/verify-scope.mjs`
- `tests/package.json`: scripts에 `verify-scope`, `verify-scope:selftest`를 추가하는 것만 허용

## 수정 금지

- `tests/` 밖의 모든 파일
- 위 목록에 없는 기존 tests 파일

## 작업

1. `tests/scripts/verify-scope.mjs`를 Node 표준 라이브러리만으로 작성한다.
   - `BASE = d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`
   - 저장소 루트는 `git rev-parse --show-toplevel`로 구해 git 명령의 cwd로 쓴다.
   - 변경 경로 = 다음 세 결과의 합집합
     - `git diff --name-only BASE`
     - `git diff --cached --name-only BASE`
     - `git ls-files --others --exclude-standard`
2. 같은 파일에 `export function evaluateScope({ changedPaths, dataJsDiff, indexHtml, rootPackageJsonExists, final }) => string[]`를 구현한다. 규칙은 다음과 같다.
   - a) 빌더 허용 경로: `index.html`, `css/style.css`, `css/themes.css`, `js/main.js`, `js/data.js`, 그리고 `tests/`로 시작하는 경로
   - b) 하네스 면제 경로:
     - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md`
     - `phases/HOO-81-portfolio-redesign/`로 시작하는 경로
     - `.harness/`로 시작하는 경로
   - c) a, b 어디에도 해당하지 않는 경로는 위반이다.
   - d) dataJsDiff(`git diff --unified=0 BASE -- js/data.js`) 검사
     - 헤더를 제외하고 `-`로 시작하는 줄이 있으면 위반이다.
     - `+` 줄의 trim 결과가 정확히 `featured: true,`가 아니면 위반이다.
     - `+` 줄이 3개를 넘으면 위반이다.
     - final 모드에서는 `+` 줄이 정확히 3개가 아니면 위반이다.
   - e) indexHtml의 fonts.googleapis.com href에 `Space+Grotesk`가 없으면 위반이다.
   - f) 루트 package.json이 있으면 위반이다.
3. CLI 동작을 구현한다.
   - 인자가 없으면 실제 저장소를 검사한다.
     - 위반이 있으면 stderr에 목록을 출력하고 exit 1로 끝낸다.
     - 위반이 없으면 `verify-scope: OK`를 출력하고 exit 0으로 끝낸다.
   - `--final`: final 모드로 검사한다.
   - `--self-test`: 내장 케이스를 evaluateScope로 돌려 기대한 위반이 검출되는지 확인한다. 하나라도 어긋나면 exit 1로 끝낸다. 내장 케이스는 다음과 같다.
     - 금지 docs 파일 변경
     - README 변경
     - assets 추가
     - 루트 package.json 존재
     - data.js 삭제 줄
     - data.js에 featured 외 다른 추가 줄
     - featured 4줄
     - final 모드에서 featured 2줄
     - Space Grotesk 제거
     - 정상 케이스(위반 0건)
4. `tests/package.json` scripts에 다음을 추가한다.
   - `verify-scope`: `node scripts/verify-scope.mjs`
   - `verify-scope:selftest`: `node scripts/verify-scope.mjs --self-test`

## 완료 기준 (AC)

- `npm --prefix tests run verify-scope:selftest` → exit 0
- `npm --prefix tests run verify-scope` → exit 0
- `npm --prefix tests test` → 통과
