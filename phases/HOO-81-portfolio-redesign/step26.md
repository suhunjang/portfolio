# Step 26 — focus-trap-modal

- 예상 시간: 17분
- 실행 횟수: 시작 snapshot 1회, focus-modal spec 2회, 전체 테스트 1회, verify-scope 1회, 범위 gate 1회
- 선행 step: 0~25 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.2 (trapFocus 계약, step 26 범위), §11.7
3. index.json에서 step 0~25가 completed인지 확인한다. 아니면 중단한다.
4. `openProjectModal`, `closeProjectModal`, `lastFocused`, 모달 내부 포커스 가능 요소를 확인한다. lightbox 코드와 기존 lightbox Tab 리스너 위치도 확인하되 건드리지 않는다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)과 §11.7 시작 snapshot 명령은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.
8. 범위 gate(§11.7): 이 step의 첫 동작은 `python3 -I tests/scripts/start-snapshot.py tests/.tmp/start-snapshot-step26.json`이다. 어떤 파일도 쓰기 전에 실행한다.

## tracked source 허용 파일 (exact)

- `js/main.js`: `trapFocus` 추가, `openProjectModal`·`closeProjectModal`의 trap 연결만
- `tests/specs/focus-modal.spec.js` (신규)

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `index.html`, `js/data.js`, `css/*`
- lightbox 관련 코드(`ensureLightbox`, lightbox 열기·닫기, 기존 lightbox Tab 리스너)
- fixtures, helper, 기존 spec

## 작업 (TDD)

1. `focus-modal.spec.js`를 먼저 작성해 실패를 확인한다 (desktop-dark/light, mobile-dark).
   - 모달 경계 순환: 마지막 포커스 요소에서 Tab → 첫 요소, 첫 요소에서 Shift+Tab → 마지막 요소. 포커스가 모달 밖으로 나가지 않는다.
   - 닫기 복귀: button·backdrop·esc 각각 닫은 뒤 포커스가 트리거 카드로 돌아온다.
   - `#heroFeatured` 카드와 `#projectGrid` 카드 양쪽 트리거에서 확인한다.
   - 같은 모달을 연속 2회 열고 닫아도 Tab 핸들러가 중복되지 않는다(순환이 한 칸씩만 이동).
2. main.js
   - `trapFocus(container, { returnFocusTo })`를 §8.2 계약대로 구현한다(스택, document Tab 핸들러 1개, release 다중 호출 안전).
   - 모달 열 때 push(returnFocusTo = trigger), 닫을 때 release.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- focus-modal.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step26.json --allow js/main.js,tests/specs/focus-modal.spec.js` → 모두 통과
