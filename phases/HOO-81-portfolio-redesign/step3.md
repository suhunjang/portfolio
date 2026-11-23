# Step 3 — interaction-regression

- 예상 시간: 18분
- 실행 횟수: 테스트 1~2회(각 웹서버 1회), verify-scope 1회
- 선행 step: 0~2 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(하네스 계약 포함), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md`의 §3, §11.4
3. index.json에서 step 0~2가 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드를 확인한다.
   - 모달·lightbox 관련 함수, 이벤트 위임, Esc 처리
   - `THEME_KEY`, 메뉴, 스크롤스파이, reveal
   - Motion-O의 shots
   - theme fixture의 null 조건
5. 다음은 read-only다.
   - `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`
   - 하네스 managed 파일: `scripts/**`, `.claude/**`, `.codex/**`, `templates/**`, `harness-manifest.json`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. git add·commit·push는 하네스만 한다. main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 모두 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/specs/interaction.spec.js`
- `tests/specs/first-visit.spec.js`
- `tests/helpers/modal.js`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`
- `tests/.npm-cache/**`
- `tests/test-results/**`
- `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖의 모든 파일
- 기존 tests 파일

## 작업

### 1. `tests/helpers/modal.js`

- `openFirstProjectByClick`
- `openFirstProjectByEnter`
- `closeVia(page, how)`: how는 button, backdrop, esc 중 하나다. backdrop은 {x:5, y:5}를 클릭한다.
- `expectFocused`

### 2. `tests/specs/interaction.spec.js`

6개 project에서 theme fixture를 사용한다.

- 테마
  - 토글하면 테마가 바뀐다.
  - reload해도 바뀐 테마가 유지되고, localStorage 값과 일치한다.
- 모달
  - click으로 연 뒤 button, backdrop, esc 각각으로 닫는다. 매번 hidden 상태인지, 포커스가 trigger로 돌아왔는지 확인한다.
  - Enter로 열고 esc로 닫았을 때도 포커스가 trigger로 돌아온다.
  - `#modalTitle`이 연 프로젝트와 일치한다.
  - `body.modal-open`이 열 때 붙고 닫을 때 해제된다.
- lightbox
  - `.shot-zoom`으로 연다.
  - Esc 1회: lightbox만 닫히고 포커스가 `.shot-zoom`으로 간다.
  - Esc 2회째: 모달이 닫히고 포커스가 카드로 간다.
- 메뉴 (mobile만)
  - `aria-expanded`가 토글된다.
  - 링크를 클릭하면 메뉴가 닫힌다.
- 스크롤스파이 (desktop만)
  - `const link = page.locator(.nav-link[href="#projects"])`를 클릭한다.
  - `await expect(link).toHaveClass(/active/)` 재시도 assertion으로 확인한다.
  - 고정 대기는 쓰지 않는다.
- typing: `#typed`가 빈 문자열이 아닌지 재시도 assertion으로 확인한다.
- reduced motion: `reducedMotion: reduce` context에서 모든 `.reveal`에 `.in`이 붙고, `#typed`가 `roles[0]`이다.
- 콘솔 에러 0건

### 3. `tests/specs/first-visit.spec.js`

- theme fixture 없이 `@playwright/test` 기본 test를 사용한다.
- desktop-dark에서만 실행한다.
- storage 없이 `newContext({ colorScheme: light })`로 열면 `data-theme=light`이고 THEME_KEY 값은 null이다.
- 같은 방식으로 colorScheme이 dark면 `data-theme=dark`다.

## 완료 기준 (AC)

- BASE 사이트에서 `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`가 모두 통과한다.
