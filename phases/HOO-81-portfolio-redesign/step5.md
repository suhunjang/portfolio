# Step 5 — hero-featured

- 예상 시간: 20분
- 실행 횟수: 테스트 2회(실패 확인 1회, 통과 1회), verify-scope 1회
- 선행 step: 0~4 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침 `CLAUDE.md`(하네스 계약 포함)와 `README.md`를 읽는다. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서 두 개를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`: 토큰, accent 제한, 그라데이션·글로우 금지
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md`: §5, §7, §9
3. index.json에서 step 0~4가 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드를 확인한다.
   - section#hero 마크업 순서
   - `setText` 호출부
   - projectGrid 렌더링
   - `openProjectModal(idx)`와 `lastFocused`
   - 위임 리스너
   - data.js의 index 1, 5, 7 `title:` 줄
5. 다음 경로는 읽기만 한다.
   - `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`
   - 하네스 managed 파일: `scripts/**`, `.claude/**`, `.codex/**`, `templates/**`, `harness-manifest.json`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. git add·commit·push는 하네스만 한다. main 직접 변경, merge, deploy는 금지다.

## tracked source 허용 파일 (exact)

- `index.html`: section#hero 내부만
- `css/style.css`
- `js/main.js`
- `js/data.js`: `featured: true,` 3줄 추가만
- `tests/specs/hero.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`
- `tests/test-results/**`
- `tests/playwright-report/**`

## 수정 금지

- `css/themes.css`
- 섹션 순서와 nav
- 기존 tests와 fixtures(axe-baseline 포함)

## 작업 (TDD)

### 1. `tests/specs/hero.spec.js`를 먼저 작성하고 실패를 확인한다

6개 project에서 실행한다.

- 대표 카드
  - `[data-featured-card]`가 3개다.
  - `data-project` 값이 1, 5, 7이다.
  - title과 blurb가 해당 프로젝트와 일치한다.
- `#heroTagline`이 `PROFILE.tagline`과 같다.
- 첫 화면 배치 (desktop, scrollY 0)
  - `#heroName`, `#heroTagline`, `#heroStats`가 y >= 0이고 y + height <= 800이다.
  - `.featured-title` 3개의 bottom이 모두 1200 이하다.
- 모달과 포커스
  - 각 대표 카드를 click으로 연 뒤 button, backdrop, esc 각 경로로 닫으면 포커스가 그 카드로 돌아온다.
  - Enter로 열고 esc로 닫아도 포커스가 복귀한다.
  - `#modalTitle`이 해당 title이다.
- CTA: `.btn-primary`는 프로젝트 보기, `.btn-ghost`는 연락하기다.
- `.hero-eyebrow`와 `#typed`가 유지된다.
- `.featured-card`의 background-image가 none이다.

### 2. `js/data.js`

index 1, 5, 7 객체에서 `title:` 바로 다음 줄에 `featured: true,`를 추가한다.

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
- `renderFeaturedProjects(): void`를 계약대로 구현하고, 그리드 렌더링 직후 호출한다.
- `openProjectModal(projectIndex, triggerElement = document.activeElement)`로 시그니처를 바꾼다.
- projectGrid에서 `openProjectModal(idx, card)`로 호출하게 바꾼다.
- `#heroFeatured`에 click 위임을 추가한다.

### 5. `css/style.css`

- eyebrow와 typing의 시각 비중을 낮춘다.
- STATS: 4열, 720px 이하에서 2×2
- `#heroFeatured`: 3열, 1024px 이하 2열, 720px 이하 1열
- 색과 간격은 기존 토큰만 쓴다.

## 완료 기준 (AC)

- `npm --prefix tests test && npm --prefix tests run verify-scope`가 모두 통과한다.
- content, interaction, axe 테스트에 회귀가 없다.
- axe에서 baseline에 없는 새 key가 0건이다.
