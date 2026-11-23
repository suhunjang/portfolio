# Step 8 — section-order-layout

- 예상 시간: 20분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~7 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §6, §7, §8.3(canonical 식별, 회귀 판정), §9, §11.4
3. index.json에서 step 0~7이 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드에서 다음을 확인한다.
   - 섹션, nav, scroll-hint
   - 스크롤스파이 배열, skillsGrid
   - timeline
   - content-exceptions의 final 값
   - axe-baseline의 canonical target 목록
5. 빌더가 읽기만 하는 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
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
- fixtures(axe-baseline 포함), 기존 spec, `tests/helpers/axe.js`
- 섹션 표에 없는 문구

## 작업 (TDD)

### 1. `tests/specs/layout.spec.js` 먼저 작성

6개 project에서 실행한다.

- 구조
  - 섹션 순서, nav, kicker, h2가 §6 표와 같다.
  - subsection-title이 1개 있다.
  - skillsGrid가 about 안에 있고, 그룹 제목은 h4다.
  - contact 구성과 scroll-hint href가 맞다.
- 레이아웃
  - 가로 스크롤이 없다.
  - 그리드 열 수: 1280에서 3, 768에서 2, 375에서 1
  - STATS: 375에서 2×2, 768/1280에서 4×1
  - Career: 375에서 세로, 768/1280에서 가로 배치(좌표로 확인)
  - 375에서 highlights가 visible이다.
- 스크롤스파이 (desktop): `const link = page.locator(.nav-link[href="#about"])`를 클릭한 뒤 `await expect(link).toHaveClass(/active/)`
- heading: h1은 1개이고 레벨을 건너뛰지 않는다.

### 2. `index.html`

- 섹션을 이동한다.
- kicker 번호를 다시 매긴다.
- Stack &amp; Contact 섹션을 분리한다.
- nav, scroll-hint, section-alt를 바꾼다.

### 3. `js/main.js`

- 스크롤스파이 배열을 바꾼다.
- skill-group 제목을 h4로 바꾼다.

### 4. `css/style.css`

- 섹션 여백을 통일한다.
- Career와 그리드를 반응형으로 만든다.
- `.subsection-title` 스타일을 추가한다.

### 5. axe canonical 식별 점검 (필수)

- 일반 모드로 axe 회귀 판정을 실행한다.
- 새 key나 새 canonical target이 나오면 다음처럼 판단한다.
  - 기존 baseline 위반과 같은 요소·같은 규칙인데 key만 달라진 경우(섹션 이동, kicker 변경 등): canonical 식별이 보존되지 않은 것이다.
    - 즉시 구현을 중단한다.
    - 해당 key와 selector를 보고한다.
    - Harness 재계획으로 돌아간다.
  - 이 step에서 새로 만든 요소(예: `h3.subsection-title`)의 실제 신규 위반: 허용 파일 안에서 고친다.
- 어느 경우든 새 target을 baseline에 자동으로 넣지 않는다. `tests/fixtures/axe-baseline.json`과 `tests/helpers/axe.js`는 수정하지 않는다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`가 모두 통과한다.
- content.spec가 final로 판정된다.
- axe에서 새 key와 새 target이 0건이다.
