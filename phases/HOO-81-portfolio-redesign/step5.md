# Step 5 — hero-featured

- 예상 시간: 20분
- 실행 횟수: 테스트 2회(실패 확인 1회 + 통과 1회), verify-scope 1회
- 선행 step: 0~4 completed

## 공통: 시작 전 필수 확인 (read-first)

1. `README.md`를 읽는다. `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서 두 개를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md` — 토큰, accent 사용처 제한, 그라데이션·글로우 금지
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` — §5 전체, §7, §9
3. index.json에서 step 0~4가 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드를 확인한다.
   - `index.html` section#hero의 순서
   - `js/main.js`의 `setText` 호출부, projectGrid 렌더링, `openProjectModal(idx)` 시그니처와 `lastFocused` 대입 위치, projectGrid의 click/keydown 위임
   - `js/data.js`의 index 1, 5, 7에서 `title:` 줄 위치
5. `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`는 읽기 전용이다. 문서 변경은 하네스만 한다.
6. main 직접 변경, merge, deploy는 금지다.

## 허용 파일 (exact)

- `index.html` (section#hero 내부만)
- `css/style.css`
- `js/main.js`
- `js/data.js` (`featured: true,` 3줄 추가만)
- `tests/specs/hero.spec.js`

## 수정 금지

- `css/themes.css`, `assets/`
- 섹션 순서와 nav (step 6에서 다룬다)
- 기존 tests와 fixtures

## 작업 (TDD)

### 1. 테스트 먼저 작성

`tests/specs/hero.spec.js`를 작성하고 실패하는 것을 확인한다. 6개 project에서 실행한다.

- 대표 카드 구성
  - `#heroFeatured [data-featured-card]`가 3개다.
  - `data-project`가 순서대로 1, 5, 7이다.
  - 각 `.featured-title`과 `.featured-blurb`가 PROJECTS[1], [5], [7]의 title, blurb와 같다.
- `#heroTagline`이 `PROFILE.tagline`과 같다.
- 첫 화면 위치 (desktop project, scrollY 0)
  - `#heroName`, `#heroTagline`, `#heroStats`의 boundingBox가 존재하고, y >= 0, y + height <= 800이다.
  - `.featured-title` 3개는 각각 y + height <= 1200이다.
- 모달 연동 (각 대표 카드)
  - click으로 열면 `#modalTitle`이 해당 title이다.
  - button, backdrop, esc 세 경로로 각각 닫을 때마다 포커스가 그 카드로 돌아온다. `tests/helpers/modal.js`의 closeVia와 expectFocused를 쓴다.
  - focus 후 Enter로 열고 esc로 닫아도 포커스가 복귀한다.
- CTA
  - `.hero-cta .btn-primary`는 프로젝트 보기, `.btn-ghost`는 연락하기다.
- 기존 요소
  - `.hero-eyebrow`가 존재한다.
  - `#typed`는 1.5초 안에 텍스트가 생긴다.
- 장식 금지
  - `.featured-card`의 computed background-image가 none이다.

### 2. `js/data.js`

- index 1, 5, 7 객체에서 `title:` 바로 다음 줄에 같은 들여쓰기로 `featured: true,`를 추가한다.
- 다른 변경은 금지한다.

### 3. `index.html` (section#hero)

순서를 다음과 같이 바꾼다.

1. `.hero-eyebrow`
2. `h1#heroName`
3. `p.hero-tagline#heroTagline` (빈 요소)
4. `h2.hero-role`
5. `#heroSummary`
6. `.hero-cta`
7. `ul#heroStats`
8. `div#heroFeatured` (aria-label 대표 프로젝트)

### 4. `js/main.js`

- `setText("heroTagline", PROFILE.tagline)`을 추가한다.
- `renderFeaturedProjects(): void`를 설계 §5 계약대로 구현하고, projectGrid 렌더링 직후에 호출한다.
- `openProjectModal(projectIndex, triggerElement = document.activeElement)`로 시그니처를 바꾸고 `lastFocused = triggerElement`로 대입한다.
- projectGrid 위임 호출부를 `openProjectModal(idx, card)`로 바꾼다.
- `#heroFeatured`에 click 위임을 추가한다. `[data-featured-card]`를 찾아 `openProjectModal(Number(data-project), card)`를 호출한다.
- Esc와 backdrop 처리는 기존 것을 그대로 쓴다.

### 5. `css/style.css`

- eyebrow와 typing 문구의 시각 비중을 줄인다.
- STATS: 4열, 720px 이하에서 2×2.
- `#heroFeatured`: 3열, 1024px 이하 2열, 720px 이하 1열.
- 기존 토큰만 쓴다. 그라데이션, 글로우, 새 accent 사용처는 넣지 않는다.

## 완료 기준 (AC)

`npm --prefix tests test && npm --prefix tests run verify-scope` → 모두 통과한다.

- content, interaction, axe 검사도 회귀 없이 통과해야 한다.
- axe는 known 목록 밖의 위반이 0건이어야 한다.
