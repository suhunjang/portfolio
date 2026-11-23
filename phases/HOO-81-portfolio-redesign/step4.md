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
   - 모달, lightbox, 이벤트 위임, Esc 처리
   - THEME_KEY, 메뉴, 스크롤스파이, reveal
   - Motion-O의 shots
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

- `tests/` 밖의 모든 파일
- 기존 tests 파일

## 작업

1. `modal.js`
   - `openFirstProjectByClick`, `openFirstProjectByEnter`
   - `closeVia(page, how)`: button, backdrop({x:5, y:5}), esc
   - `expectFocused`
2. `interaction.spec.js` (6개 project, collector는 고정 순서로)
   - 테마: 토글, reload 후 유지, localStorage 값
   - 모달: 닫기 경로별 결과와 포커스 복귀, Enter로 열기, 제목, `modal-open` 클래스
   - lightbox: Esc 2단계 닫기
   - 메뉴 (mobile)
   - 스크롤스파이 (desktop): `const link = page.locator(.nav-link[href="#projects"])` 클릭 후 `await expect(link).toHaveClass(/active/)`
   - typing, reduced motion
3. `first-visit.spec.js`: fixture를 쓰지 않고 desktop-dark에서만 실행한다. light와 dark를 각각 확인한다.

## 완료 기준 (AC)

- BASE 사이트에서 `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`가 모두 통과한다.
