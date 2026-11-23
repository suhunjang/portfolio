# Step 7 — axe-canonical

- 예상 시간: 18분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~6 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.1, §8.3 (canonical 식별, 안정성 범위, step 7 계약)
3. index.json에서 step 0~6이 completed인지 확인한다. 아니면 중단한다.
4. JS 렌더 영역, `data-project`, landmark를 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/helpers/axe.js` (신규)
- `tests/specs/axe-helper.spec.js` (신규)

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖 전부
- 기존 tests 파일

## 작업

1. `axe.js`에 step 7 계약을 구현한다: `ALIASES`, `canonicalTargetInPage`, `canonicalFromDescriptor`, `runAxe`
2. `axe-helper.spec.js` (desktop-dark에서 `page.setContent`로 실제 axe 실행)
   - a) `section#career` subtree 전체를 이동하고, h3를 span으로 바꾸고, 텍스트를 01→04로 바꿔도 key가 같다.
   - a2) h3만 section 밖으로 이동하면 key가 달라진다.
   - b) `[data-project=5]` 안에서 div를 p로 바꿔도 key가 같다.
   - c) 텍스트가 다르면 key가 다르다.
   - d) `project:5`와 `featured:5`는 서로 다른 key다.
   - e) alias가 적용되면 key가 같다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 통과
