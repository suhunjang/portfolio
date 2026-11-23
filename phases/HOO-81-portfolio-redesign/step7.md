# Step 7 — hero-featured

- 예상 시간: 20분
- 실행 횟수: 테스트 2회(실패 확인 1회, 통과 1회), verify-scope 1회
- 선행 step: 0~6 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §5, §7, §8.3(회귀 판정), §9
3. index.json에서 step 0~6이 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드에서 다음을 확인한다.
   - hero 마크업과 reveal
   - `setText`, projectGrid
   - `openProjectModal`, `lastFocused`, 이벤트 위임
   - data.js의 index 1, 5, 7
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `index.html` (section#hero 내부만)
- `css/style.css`
- `js/main.js`
- `js/data.js` (`featured: true,` 3줄만)
- `tests/specs/hero.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `css/themes.css`
- 섹션 순서, nav
- 기존 tests와 fixtures(axe-baseline 포함). 새 target을 baseline에 넣지 않는다.

## 작업 (TDD)

### 1. `tests/specs/hero.spec.js` 작성 후 실패 확인

6개 project에서 실행한다. `collectConsoleErrors`는 고정 순서로 쓴다.

대표 카드
- 3개이고, 각각 `button[type=button]`, `data-project`는 1, 5, 7이다.
- 각 카드에 `span.featured-title`과 `span.featured-blurb`가 정확히 1개씩 있다.
- 금지 자손이 0개다.
- title과 blurb가 데이터와 일치한다.
- 두 span의 display가 block이다.
- `#heroTagline`이 `PROFILE.tagline`과 같다.

첫 화면 AC (desktop만)
- 사전 조건: `fonts.ready`, `scrollY === 0`
- 대상 6개 각각
  - visible
  - width·height > 0
  - 자신과 모든 조상이 visibility visible, opacity 1 (`expect.poll`)
  - 1280×800 경계 안

모달
- 대표 카드마다 click으로 열고 button, backdrop, esc로 닫는다. 매번 포커스가 그 카드로 돌아와야 한다.
- Enter로 열고 esc로 닫는 경우도 포커스가 돌아와야 한다.
- 모달 제목이 카드와 일치한다.

기타
- CTA 라벨과 클래스
- eyebrow와 `#typed` 유지
- 카드 background-image가 none

### 2. `js/data.js`

- index 1, 5, 7에 `featured: true,`를 넣는다.

### 3. `index.html`

- hero 순서를 §5대로 바꾼다.

### 4. `js/main.js`

- `setText(heroTagline, PROFILE.tagline)`
- `renderFeaturedProjects(): void`
  - button 안에 span만 쓴다.
  - 텍스트는 `esc()`로 처리한다.
- `openProjectModal(projectIndex, triggerElement = document.activeElement)`
- projectGrid는 `openProjectModal(idx, card)`로 호출한다.
- `#heroFeatured`에 click 위임을 단다.

### 5. `css/style.css`

- span은 block으로 두고, blurb는 2줄 clamp를 허용한다.
- 첫 화면 AC를 맞추도록 여백, 크기, 카드 높이를 조정한다. 문구는 줄이지 않는다.
- STATS: 4열, 720px 이하에서 2×2
- featured: 3열, 1024px 이하 2열, 720px 이하 1열
- 토큰만 쓴다.

### 6. axe 회귀

새 target이 나왔을 때
- 이 step에서 추가한 마크업·스타일 때문에 생긴 신규 위반이면 허용 파일 안에서 고친다.
- 기존 위반의 식별이 깨진 것이면 즉시 중단하고 Harness 재계획으로 돌아간다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`가 모두 통과한다.
