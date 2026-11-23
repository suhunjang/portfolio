# Step 9 — focus-trap

- 예상 시간: 18분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~8 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.2
3. index.json에서 step 0~8이 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드에서 모달·lightbox 함수, Tab 리스너, `:focus-visible`을 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `js/main.js`
- `css/style.css` (`:focus-visible` 규칙만)
- `tests/specs/focus.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `index.html`, `js/data.js`, `css/themes.css`
- fixtures, 기존 spec

## 작업 (TDD)

### 1. `tests/specs/focus.spec.js` 먼저 작성

6개 project에서 실행한다.

- 모달: Tab과 Shift+Tab을 각각 20회 눌러도 포커스가 `.modal-dialog` 안에 머문다.
- lightbox
  - Tab과 Shift+Tab 각 10회 동안 포커스가 lightbox 안에 머문다.
  - Esc를 누르면 포커스가 `.shot-zoom`으로 간다.
  - 이어서 Tab 20회 동안 포커스가 모달 안에 머문다.
  - Esc를 다시 누르면 포커스가 trigger로 간다.
- 버튼이나 backdrop으로 닫아도 포커스가 trigger로 복귀한다.
- 키보드 도달: toggle, nav, 대표 카드, project-card에 도달할 수 있고, outline이 none이 아니다.

### 2. `js/main.js`

- `trapFocus(container, { returnFocusTo } = {}): () => void`
  - 스택 구조, Tab 핸들러는 1개만 둔다.
  - `release()`는 여러 번 호출해도 안전하다.
- 모달과 lightbox에 연결한다.
- 기존 Tab 고정 리스너는 제거한다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`가 모두 통과한다.
- axe에서 새 key와 새 target이 0건이다.
