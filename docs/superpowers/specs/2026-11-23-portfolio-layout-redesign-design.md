# 포트폴리오 레이아웃·구조 리디자인 설계 (HOO-81)

- 날짜: 2026-11-23
- 브랜치: `feat/HOO-81/portfolio-redesign` (base `main`)
- 선행 문서: `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md` (시각 톤, 적용 완료)
- 합의: Discord 1574196542901059632 (Q1), 1574197289084387379 (Q2), 1574197696334405756 (Q3~Q5 추천안 일괄 확정)

## 1. 의도

2026-07-29 작업에서 색·서체·여백을 "경영자의 절제" 톤으로 정리했다. 그때 레이아웃 구조는 범위 밖이었다. 이번 작업은 그 톤을 유지하면서 구조를 다시 짠다. 목적은 채용·영입 의사결정자(임원 채용 담당자, 헤드헌터, 대표)가 30초 안에 세 가지를 파악하게 하는 것이다.

1. COO·CTO 포지셔닝
2. 핵심 지표
3. 대표 프로젝트라는 근거

## 2. 목표 / 비목표 / 실패 조건

### 목표
- 첫 화면(히어로)에 이름, COO·CTO 포지셔닝, 핵심 지표(STATS 4개), 대표 프로젝트 3개를 담는다.
- 섹션 순서를 근거 우선으로 재배치한다.
- 히어로 구성, 섹션 리듬, 카드·타임라인 배치, 모바일 레이아웃을 재구성한다.
- 기존 기능을 전부 보존하고 자동 테스트로 증명한다.

### 비목표
- 색·서체 체계 재설계. 선행 문서의 토큰을 그대로 쓴다.
- 빌드 도구 도입. 사이트 자체는 순수 HTML/CSS/JS로 유지한다.
- 신규 기능 추가.
- 배포, merge, main 브랜치 직접 변경.

### 실패 조건 (기술적으로 동작해도 실패로 본다)
- 콘텐츠 문구·수치·경력 사실이 바뀌거나 새로 창작된다.
- 비어 있는 email/phone이 채워진다.
- 기존 기능 중 하나라도 회귀한다.
- 접근성 위반이 새로 생긴다.
- 화려한 그라데이션·글로우 등 절제 톤에 어긋나는 장식이 되돌아온다.

## 3. 제약

- GitHub Pages 정적 배포. 루트의 `index.html`을 직접 연다.
- `js/data.js`의 SVG 일러스트가 `font-family=Space Grotesk`를 하드코딩하고 있다. 따라서 `index.html`의 Google Fonts 링크에서 Space Grotesk를 지우지 않는다.
- `.thumb-violet` / `.thumb-blue` / `.thumb-cyan` 클래스명과 `accent` 값을 유지한다. `main.js`와 `data.js`가 이 이름을 참조한다.
- `README.md`, `assets/`, `.nojekyll`은 수정하지 않는다.

## 4. 접근 방식

| 안 | 내용 | 판단 |
|---|---|---|
| A (선택) | 절제 톤 유지 + 레이아웃·구조 재구성 | Q1에서 대표가 선택. 체감되는 변화가 크고, 기존 시각 언어를 보존한다 |
| B | 시각 방향 전면 교체 | 선행 작업을 되돌리게 되어 기각 |
| C | 마감만 다듬기 | 리디자인으로 체감되기 어려워 기각 |

## 5. 확정된 결정

### 5.1 첫 화면 (Q2, Q3)

주 독자는 채용·영입 의사결정자다.

히어로 구성 순서:
1. 이름
2. 포지셔닝 한 줄 (`PROFILE.tagline`)
3. 타이핑 역할 문구 (보조 크기)
4. 요약
5. STATS 4개
6. 대표 프로젝트 3개 카드

인사말(`hero-eyebrow`)과 타이핑 모션은 시각적 비중만 낮춘다. 요소와 기능은 유지한다.

대표 프로젝트는 Motion AD, VigoRight (의료 AI/VR), Lost Energy Intel이다.
- `js/data.js`의 해당 3개 항목에 `featured: true` 필드만 추가한다. 다른 필드와 문구는 수정하지 않는다.
- 대표 카드에 표시할 근거 수치는 이미 data.js(프로젝트 또는 CAREER highlights)에 있는 문자열만 쓴다.
- 대표 카드를 클릭하면 기존 프로젝트 모달이 해당 프로젝트로 열린다. 기존 `openProjectModal(idx)`를 재사용한다.
- 전체 프로젝트 그리드에는 13개 전부를 그대로 둔다(대표 3개 포함).

CTA:
- 주 버튼은 '프로젝트 보기'다.
- '연락하기'는 보조(ghost) 버튼으로 유지한다. 연락처가 비어 있기 때문이다.

데스크톱(1280×800) 기준:
- 이름, 포지셔닝, STATS는 첫 viewport 안에 보여야 한다.
- 대표 프로젝트 3개 제목은 스크롤 1.5 viewport 이내에 보여야 한다.

### 5.2 섹션 순서 (Q4)

- 새 순서: Hero → Career → Projects → Strengths → About·Stack → Contact
- 섹션 id(`hero`, `career`, `projects`, `strengths`, `about`, `contact`)와 네비게이션 앵커를 모두 유지한다. 네비게이션 링크 순서는 섹션 순서에 맞춘다.
- About 본문 문구는 그대로 둔다. 기술 스택(skillsGrid)은 About 섹션과 같은 구역에 배치한다. Contact는 마지막 독립 섹션으로 둔다.
- 섹션 kicker 번호(01 —)는 새 순서에 맞게 다시 매긴다. 라벨 텍스트는 유지한다.

### 5.3 레이아웃 기본값 (작성자 결정, 대표 승인 범위 내)

- 섹션 리듬: 구역마다 같은 head 패턴(kicker, 제목, 선택적 sub)을 쓰고 일관된 세로 여백을 둔다. `section-alt` 배경 교차는 새 순서에 맞게 재배치한다.
- Career:
  - 데스크톱은 기간을 왼쪽 열, 역할·회사·성과를 오른쪽 열에 두는 2열 타임라인이다.
  - 모바일(≤720px)은 1열로 쌓는다.
  - highlights는 항상 펼친다.
- Projects: 반응형 카드 그리드다. 열 수는 1280px에서 3열, 768px에서 2열, 375px에서 1열이다.
- Strengths: 6개 카드를 3열/2열/1열로 배치한다.
- 모바일: 대표 프로젝트 카드는 세로로 쌓고, STATS는 2×2로 배치한다. 가로 스크롤이 없어야 한다.
- 인쇄(PDF):
  - `@media print`를 새 구조에 맞게 고친다.
  - 대표 프로젝트 카드는 인쇄에 포함한다.
  - 인터랙션 요소(토글, 메뉴, 모달, lightbox, scroll-hint)는 숨긴다.

### 5.4 보존할 기존 기능

- 다크/라이트 토글. `localStorage`에 저장하고, 최초 방문 시 시스템 설정을 반영한다.
- 햄버거 메뉴(≤720px). `aria-expanded`를 토글하고, 링크 클릭 시 메뉴를 닫는다.
- 타이핑 애니메이션(`runTyping`)과 스크롤 reveal. `prefers-reduced-motion`이 켜져 있으면 즉시 표시한다.
- data.js 기반 렌더링: STATS, CAREER, PROJECTS, STRENGTHS, SKILLS.
- 프로젝트 모달: backdrop·닫기 버튼·Esc로 닫히고, 닫은 뒤 포커스를 복귀한다.
- 갤러리 lightbox: Esc를 누르면 lightbox부터 닫힌다.
- 스크롤 시 활성 네비게이션 표시(`.nav-link.active`).

### 5.5 접근성 기준

- axe-core 기준 serious/critical 위반 0건. 다크·라이트 두 테마 모두 확인한다.
- WCAG AA 명암 대비.
- 모든 인터랙션을 키보드로 조작할 수 있고 `:focus-visible` 스타일이 유지된다.
- 모달과 lightbox가 열려 있는 동안 Tab 포커스가 그 안에 갇힌다. 지금 없다면 추가한다.
- heading 계층을 유지한다. h1은 이름 하나만 둔다.

### 5.6 검증 (Q5)

- 테스트 도구는 `tests/` 폴더 안에만 둔다.
  - `tests/package.json`(devDependencies: `@playwright/test`, `@axe-core/playwright`)과 lockfile을 둔다.
  - 루트에는 package.json을 두지 않는다.
- 정적 서버는 Playwright `webServer`로 띄운다. 명령은 `python3 -m http.server 4173`이고 cwd는 저장소 루트다.
- 실행 명령: `npm --prefix tests test` (= `playwright test`)
- 매트릭스: viewport 375×812, 768×1024, 1280×800 × 테마 dark, light
- 콘솔 에러 0건. 단 fonts.googleapis.com / fonts.gstatic.com 네트워크 실패는 무시한다.
- 콘텐츠 보존 검사: 렌더링된 STATS, CAREER, PROJECTS 개수와 제목이 data.js 전역 값과 일치해야 한다. 13개 프로젝트, STATS 4개를 확인한다.

## 6. 변경 허용 경로

- 허용:
  - `index.html`
  - `css/themes.css`, `css/style.css`
  - `js/main.js`
  - `js/data.js` (`featured: true` 3곳 추가만 허용)
  - `tests/**`
- 금지: `assets/`, `README.md`, `.nojekyll`, `docs/` (하네스가 관리), 루트 package.json

## 7. 빌더 재량

- 대표 카드의 세부 시각 구성. 썸네일을 쓸지 텍스트만 쓸지 정하되, 절제 톤과 accent 사용처 제한(선행 문서 §1)을 지킨다.
- 클래스명과 CSS 구조 정리 방식. 기존 테스트 가능한 id와 data 속성은 유지한다.
- 테스트 파일 분할 방식.
