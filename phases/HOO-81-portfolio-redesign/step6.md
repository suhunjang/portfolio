# Step 6 — ui-regression

- 예상 시간: 16분
- 실행 횟수: ui-regression·first-visit spec 2회, 전체 테스트 1회, verify-scope 1회
- 선행 step: 0~5 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §3(기타), §6(스크롤스파이 locator 예시), §7.4, §11.4
3. index.json에서 step 0~5가 completed인지 확인한다. 아니면 중단한다.
4. 다음을 확인한다: `THEME_KEY`, 테마 토글, `#menuToggle`·`#navLinks.open`·`aria-expanded`, 스크롤스파이, `runTyping`, reduced-motion 분기
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/specs/ui-regression.spec.js` (신규)
- `tests/specs/first-visit.spec.js` (신규)

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖 전부
- 기존 tests 파일 (`modal.js`, `modal-regression.spec.js` 포함)
- 모달·lightbox 검사 (step 5 범위)

## 작업

1. `ui-regression.spec.js` (6개 project, collector 고정 순서)
   - 테마: 토글 시 `data-theme`과 `THEME_KEY` 저장값이 바뀌고, 새로고침 후 유지된다.
   - 메뉴 (mobile): 토글하면 `#navLinks.open`과 `aria-expanded="true"`, 링크 클릭 후 닫힌다.
   - 스크롤스파이 (desktop), 정확히 다음 문법을 쓴다:
     - `const link = page.locator('.nav-link[href="#projects"]');`
     - `await link.click();`
     - `await expect(link).toHaveClass(/active/);`
   - typing: 일반 모드에서 `#typed` 텍스트가 시간에 따라 바뀐다.
   - reduced-motion: `reducedMotion: 'reduce'` context에서 `#typed`가 `roles[0]`로 고정되고 `.reveal`이 즉시 `.in`을 가진다.
2. `first-visit.spec.js`: fixture 없이 desktop-dark에서 실행한다. `colorScheme` light와 dark 각각에서 저장값이 없을 때 시스템 설정을 따르는지 확인한다.

## 완료 기준 (AC)

- BASE 사이트에서 다음이 모두 통과한다: `sh tests/scripts/with-env.sh npm --prefix tests test -- ui-regression.spec.js first-visit.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`
