# Step 15 — section-layout

- 예상 시간: 15분
- 실행 횟수: layout spec 2회, 전체 테스트 1회, verify-scope 1회
- 선행 step: 0~14 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §6, §9
3. index.json에서 step 0~14가 completed인지 확인한다. 아니면 중단한다.
4. 섹션 CSS, timeline 구조, 그리드 규칙을 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `css/style.css` (섹션 여백, Career, 그리드, `.subsection-title` 규칙만)
- `tests/specs/layout.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `index.html`, `js/*`, `css/themes.css`
- fixtures, helper, 기존 spec

## 작업 (TDD)

1. `layout.spec.js`를 먼저 작성한다. 6개 project에서 실행한다.
   - 가로 스크롤이 없다.
   - projectGrid와 strengthsGrid의 열: 1280에서 3, 768에서 2, 375에서 1
   - Career
     - 375에서는 세로로 쌓인다.
     - 768·1280에서는 가로다(card.left >= period.right - 1, top 차이 < 24).
   - 375에서 highlights가 보인다.
   - section gap: career~contact의 padding-top이 모두 같다.
   - `.subsection-title`의 font-weight가 h2 이하다.
2. style.css
   - 섹션 여백을 통일한다.
   - Career: 721px 이상에서 2열, 그 이하에서 1열
   - 그리드: 3열, 1024px 이하 2열, 720px 이하 1열
   - `.subsection-title` 스타일을 추가한다.
   - 기존 토큰만 쓴다.
3. axe 새 target은 step 12와 같은 규칙을 따른다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- layout.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 모두 통과
