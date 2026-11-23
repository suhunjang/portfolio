# Step 12 — section-order-layout

- 예상 시간: 20분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~11 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §6, §7, §8.3(canonical 안정성 보장 범위, 회귀), §9, §11.4
3. index.json에서 step 0~11이 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드에서 다음을 확인한다.
   - 섹션, nav, scroll-hint, 스크롤스파이, skillsGrid, timeline
   - content-exceptions의 final
   - baseline canonical 목록
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `index.html`
- `css/style.css`
- `js/main.js`
- `tests/specs/layout.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `js/data.js`, `css/themes.css`
- fixtures, helper, 기존 spec
- 섹션 표 밖의 문구

## 작업 (TDD)

### 1. `layout.spec.js` 먼저 작성 (6개 project)

- 구조
  - 섹션 순서가 §6 표와 같다.
  - subsection, skill-group h4, contact, scroll-hint
- 레이아웃
  - 가로 스크롤이 없다.
  - 그리드 열 수
  - STATS: 375에서 2×2, 768·1280에서 4×1
  - Career: 375에서 세로, 768·1280에서 가로
  - highlights가 보인다.
- 스크롤스파이 (desktop)
  - `const link = page.locator(.nav-link[href="#about"])`를 클릭한다.
  - `await expect(link).toHaveClass(/active/)`
- heading 계층

### 2. `index.html`

- 섹션은 subtree 전체를 통째로 옮긴다. 그래야 anchor(`section[id]`)가 유지된다.
- kicker를 바꾼다.
- Stack &amp; Contact를 분리한다.
- nav, scroll-hint, section-alt를 바꾼다.

### 3. `main.js`

- 스크롤스파이 배열을 바꾼다.
- skill-group 제목을 h4로 바꾼다.

### 4. `style.css`

- 섹션 여백, Career, 그리드, subsection-title

### 5. axe canonical 점검 (필수)

일반 모드로 회귀 판정을 실행한다. 새 key나 target이 나오면 원인에 따라 처리한다.

- 식별 상실: 같은 요소·같은 규칙인데 key만 바뀐 경우다. 예를 들어 요소가 anchor 경계 밖으로 이동한 경우.
  - 즉시 중단한다.
  - key와 selector를 보고한다.
  - 재계획을 요청한다.
- 이 step에서 새로 만든 요소의 실제 신규 위반: 허용 파일 안에서 고친다.
- 어떤 경우에도 baseline에 자동 편입하지 않는다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`가 모두 통과한다.
- content.spec에서 final이 성립한다.
