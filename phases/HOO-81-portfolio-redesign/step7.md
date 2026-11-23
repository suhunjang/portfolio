# Step 7 — modal-regression

- 예상 시간: 18분
- 실행 횟수: 시작 snapshot 1회, modal-regression spec 2회, 전체 테스트 1회, verify-scope 1회, 범위 gate 1회
- 선행 step: 0~6 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §3(모달 마크업, lightbox), §5(대표 카드와 grid 카드의 같은 data-project), §7.4(modal.js 계약), §11.4, §11.7
3. index.json에서 step 0~6이 completed인지 확인한다. 아니면 중단한다.
4. 다음을 확인한다: `#projectGrid` 카드 셀렉터, `#projectModal`·`#modalBody`·`#modalTitle`·`.modal-close[data-modal-close]` 마크업, 모달 열기·닫기 위임, `modal-open`, `.shot-zoom`이 있는 프로젝트, `ensureLightbox`, Esc 처리 순서
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)과 §11.7 시작 snapshot 명령은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.
8. 범위 gate(§11.7): 이 step의 첫 동작은 `python3 -I tests/scripts/start-snapshot.py tests/.tmp/start-snapshot-step7.json`이다. 어떤 파일도 쓰기 전에 실행한다.

## tracked source 허용 파일 (exact)

- `tests/helpers/modal.js` (신규)
- `tests/specs/modal-regression.spec.js` (신규)

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖 전부
- 기존 tests 파일
- 테마·메뉴·scrollspy·typing·reduced-motion 검사 (step 8에서 한다)

## 작업

1. `modal.js` (§7.4 계약)
   - `GRID_CARD`, `gridCard(page, N)` — 정확히 `page.locator('#projectGrid .project-card[data-project="' + N + '"]')`
   - `openFirstProjectByClick`, `openFirstProjectByEnter` — `GRID_CARD` 범위만 사용
   - `closeVia(page, how)`: button(`#projectModal .modal-close[data-modal-close]`), backdrop({x:5, y:5}), esc
   - `expectFocused`
   - `modalTitle(page)` — 정확히 `page.locator('#projectModal #modalTitle')`
   - `findProjectWithShots(page)` — `#projectGrid .project-card[data-project]`만 탐색한다. 카드마다 열기 → `modal-open` 확인 → `.shot-zoom` 확인 → `closeVia(page, 'button')` → `modal-open` 해제 확인 순서를 지킨다.
2. `modal-regression.spec.js` (6개 project, collector 고정 순서)
   - 모달: click으로 열기, Enter로 열기, `modalTitle` 텍스트가 데이터와 같음, body `modal-open`
   - 닫기: button·backdrop·esc 각 경로로 닫히고 포커스가 트리거 카드로 돌아온다. 닫힌 뒤 `modal-open`이 없다.
   - lightbox (desktop만): `findProjectWithShots`가 index를 반환하고, 탐색이 끝난 뒤 모달이 닫혀 있다. 그 index의 `gridCard` 모달에서 `.shot-zoom`으로 lightbox가 열린다.
   - Esc 2단계: 1회째 lightbox만 닫히고 모달은 열려 있다. 2회째 모달이 닫힌다.

## 완료 기준 (AC)

- BASE 사이트에서 다음이 모두 통과한다: `sh tests/scripts/with-env.sh npm --prefix tests test -- modal-regression.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step7.json --allow tests/helpers/modal.js,tests/specs/modal-regression.spec.js`
