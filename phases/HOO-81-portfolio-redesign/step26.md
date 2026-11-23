# Step 26 — focus-trap-lightbox

- 예상 시간: 16분
- 실행 횟수: focus-lightbox spec 2회, 전체 테스트 1회, verify-scope 1회
- 선행 step: 0~25 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.2 (step 26 범위)
3. index.json에서 step 0~25가 completed인지 확인한다. 아니면 중단한다.
4. step 25의 `trapFocus`, `ensureLightbox`, 기존 lightbox Tab 고정 리스너, `.shot-zoom`, `:focus-visible` 규칙을 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `js/main.js`: lightbox 열기·닫기의 trap 연결과 기존 lightbox Tab 리스너 제거만
- `css/style.css`: `:focus-visible` 규칙만
- `tests/specs/focus-lightbox.spec.js` (신규)

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `index.html`, `js/data.js`, `css/themes.css`
- `trapFocus` 시그니처와 모달 연결(step 25)
- fixtures, helper, 기존 spec(`focus-modal.spec.js` 포함)

## 작업 (TDD)

1. `focus-lightbox.spec.js`를 먼저 작성해 실패를 확인한다 (desktop-dark/light).
   - 중첩: `findProjectWithShots`로 찾은 grid 카드 모달 → `.shot-zoom`으로 lightbox 열기 → Tab/Shift+Tab이 lightbox 안에서만 순환한다(모달 trap 일시정지).
   - 해제·재개: Esc 1회 → lightbox 닫힘, 포커스가 `.shot-zoom`으로 복귀, 이후 Tab이 다시 모달 경계 안에서 순환한다. Esc 2회째 → 모달 닫힘, 트리거로 복귀.
   - 기존 리스너 제거: lightbox를 3회 열고 닫은 뒤에도 Tab 1회가 정확히 한 칸만 이동한다.
   - outline: 키보드로 도달한 `.featured-card`, `.project-card`, 모달 닫기 버튼, `.shot-zoom`의 computed `outline-style`이 `none`이 아니다.
2. main.js
   - lightbox 열 때 push(returnFocusTo = `.shot-zoom`), 닫을 때 release.
   - 기존 lightbox Tab 고정 리스너를 제거한다.
3. style.css: `:focus-visible` outline을 유지·보강한다(토큰만 사용).

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- focus-lightbox.spec.js focus-modal.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 모두 통과
