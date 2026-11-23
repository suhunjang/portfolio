# Step 5 — hero-featured

- 예상 시간: 20분
- 실행 횟수: 테스트 2회(실패 확인 1회, 통과 1회), verify-scope 1회
- 선행 step: 0~4 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(하네스 계약 포함), `README.md`. 하위 디렉터리의 `CLAUDE.md`/`AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`: 토큰, accent 제한, 그라데이션 금지
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md`: §5(첫 화면 측정 포함), §7, §8.3(회귀 판정), §9
3. index.json에서 step 0~4가 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드를 확인한다.
   - hero 마크업과 여백
   - `setText`, projectGrid
   - `openProjectModal(idx)`, `lastFocused`, 이벤트 위임
   - data.js의 index 1, 5, 7 `title:` 줄
5. 빌더 read-only 경로
   - `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`
   - 하네스 managed 파일: `scripts/**`, `.claude/**`, `.codex/**`, `templates/**`, `harness-manifest.json`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. git add·commit·push는 하네스만 한다. main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 모두 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `index.html` (section#hero 내부만)
- `css/style.css`
- `js/main.js`
- `js/data.js` (`featured: true,` 3줄 추가만)
- `tests/specs/hero.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`
- `tests/.npm-cache/**`
- `tests/test-results/**`
- `tests/playwright-report/**`

## 수정 금지

- `css/themes.css`
- 섹션 순서, nav
- 기존 tests와 fixtures (axe-baseline 포함)

## 작업 (TDD)

### 1. `tests/specs/hero.spec.js` 작성 → 실패 확인

6개 project에서 실행한다.

- 대표 카드
  - 카드가 3개다.
  - `data-project`가 1, 5, 7이다.
  - title과 blurb가 데이터와 일치한다.
- `#heroTagline`이 `PROFILE.tagline`이다.
- 첫 화면 측정 (desktop, scrollY 0)
  - 대상: `#heroName`, `#heroTagline`, `#heroStats`, `.featured-title` 3개
  - 각각 `y >= 0`이고 `y + height <= 800`이다.
- 모달
  - 대표 카드마다 click으로 연 뒤 button, backdrop, esc로 닫는다. 매번 포커스가 그 카드로 돌아와야 한다.
  - Enter로 열고 esc로 닫을 때도 포커스가 카드로 돌아와야 한다.
  - `#modalTitle`이 해당 프로젝트와 일치한다.
- CTA: primary는 프로젝트 보기, ghost는 연락하기
- eyebrow와 `#typed`가 유지된다.
- `.featured-card`의 background-image가 none이다.

### 2. `js/data.js`

- index 1, 5, 7에서 `title:` 바로 다음 줄에 `featured: true,`를 추가한다.

### 3. `index.html` hero 순서

1. eyebrow
2. h1
3. `p.hero-tagline#heroTagline`
4. h2.hero-role
5. summary
6. CTA
7. `#heroStats`
8. `div#heroFeatured`

### 4. `js/main.js`

- `setText(heroTagline, PROFILE.tagline)`를 추가한다.
- `renderFeaturedProjects(): void`를 구현한다.
- `openProjectModal(projectIndex, triggerElement = document.activeElement)`로 바꾼다.
- projectGrid에서는 `openProjectModal(idx, card)`로 호출한다.
- `#heroFeatured`에 click 위임을 둔다.

### 5. `css/style.css`

- 대표 제목 3개가 1280×800 초기 화면 안에 들어오게 한다. 문구는 줄이지 않는다.
  - 히어로 세로 여백을 줄인다.
  - eyebrow와 typing 크기를 줄인다.
  - 대표 카드는 썸네일 없이 낮은 높이로 만든다. blurb는 2줄 clamp를 허용한다.
- STATS: 기본 4열, 720px 이하에서 2×2
- `#heroFeatured`: 기본 3열, 1024px 이하 2열, 720px 이하 1열
- 기존 토큰만 쓴다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 모두 통과
- content와 interaction에 회귀가 없다.
- axe 회귀 판정에서 baseline 밖의 새 key와 새 target이 0건이다. 새로 생긴 것은 이 step에서 해결한다.
