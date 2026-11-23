# Step 4 — interaction-regression

- 예상 시간: 18분
- 실행 횟수: 테스트 1~2회, verify-scope 1회
- 선행 step: 0~3 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §3, §11.4
3. index.json에서 step 0~3이 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드에서 다음을 확인한다.
   - 모달·lightbox, 이벤트 위임, Esc 처리
   - THEME_KEY, 메뉴, 스크롤스파이, reveal
   - Motion-O의 shots
   - `collectConsoleErrors` 계약
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/specs/interaction.spec.js`
- `tests/specs/first-visit.spec.js`
- `tests/helpers/modal.js`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖 전부
- 기존 tests 파일

## 작업

### 1. `tests/helpers/modal.js`

- `openFirstProjectByClick`
- `openFirstProjectByEnter`
- `closeVia(page, how)`: button, backdrop({x:5, y:5}), esc 중 하나
- `expectFocused`

### 2. `tests/specs/interaction.spec.js` (6개 project, theme fixture)

- 콘솔
  - 각 테스트에서 `const c = collectConsoleErrors(page)`를 goto보다 먼저 호출한다.
  - 마지막에 `await c.finish()`의 두 배열이 모두 `[]`인지 확인한다.
- 테마: 토글하면 바뀌고, reload해도 유지되며, localStorage 값과 일치한다.
- 모달
  - click으로 연 뒤 button, backdrop, esc 각각으로 닫는다. 매번 hidden 상태와 trigger로 돌아온 포커스를 확인한다.
  - Enter로 열고 esc로 닫는 경우도 확인한다.
  - 모달 제목이 해당 카드와 일치하는지 확인한다.
  - `body.modal-open`이 열 때 붙고 닫을 때 해제되는지 확인한다.
- lightbox
  - Esc 1회: lightbox만 닫히고 포커스가 `.shot-zoom`으로 간다.
  - Esc 2회째: 모달이 닫히고 포커스가 카드로 간다.
- 메뉴 (mobile): `aria-expanded`가 토글되고, 링크를 누르면 메뉴가 닫힌다.
- 스크롤스파이 (desktop): `const link = page.locator(.nav-link[href="#projects"])`를 클릭한 뒤 `await expect(link).toHaveClass(/active/)`.
- typing: 재시도 assertion으로 텍스트가 비어 있지 않은지 확인한다.
- reduced motion: 모든 `.reveal`에 `.in`이 붙고, `#typed`가 `roles[0]`이다.

### 3. `tests/specs/first-visit.spec.js` (fixture 없이, desktop-dark만)

- storage가 없는 context에서 colorScheme light로 열면 테마가 light이고 THEME_KEY는 null이다.
- colorScheme dark로 열면 테마가 dark다.

## 완료 기준 (AC)

- BASE 사이트에서 `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`가 모두 통과한다.
