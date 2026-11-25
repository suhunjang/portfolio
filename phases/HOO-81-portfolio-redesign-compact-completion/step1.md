# Compact Step 1 — featured-hero

- 목적: 아래 세 영역에서 현재 HEAD 기준으로 남은 실제 diff만 구현한다.
  - featured data
  - 대표 카드
  - hero 첫 화면(원 §3)
- 예상 20분, hard timeout 30분. 선행: step 0.
- 허용 파일(exact): `js/data.js`, `index.html`, `js/main.js`, `css/style.css`, `tests/specs/featured.spec.js`(신규)
- 금지:
  - 색 선언 변경(step 3 소관)
  - 문구·수치 변경
  - `css/themes.css` 수정
  - 섹션 순서 변경(step 2 소관)

## 작업
1. `tests/specs/featured.spec.js`를 먼저 작성하고, 실패하는 것을 확인한다(RED). 이 파일이 아래 assertion을 소유한다.
   - `js/data.js` PROJECTS 중 `featured === true`인 것이 정확히 index 1·5·7이고, 13개 project의 순서·title이 그대로다.
   - `#heroFeatured`가 1개이고, div, role `region`, aria-label `대표 프로젝트`이며, `#heroStats`의 바로 다음 형제다.
   - 카드 3개: 각각 `button[type=button]`, data-project 1·5·7, `span` 정확히 2개(block), 안에 interactive 자손 0개, background-image none.
   - click 또는 Enter로 모달이 열린다. 제목이 맞는다. 닫기 버튼·backdrop·Esc 각각으로 닫으면 해당 카드 버튼으로 focus가 돌아온다.
   - hero 직계 자식 순서가 원 §3과 같다. `#heroTagline`은 `PROFILE.tagline`이다.
   - 375·768·1280에서 가로 스크롤이 없다. featured 열 수는 1/2/3이다.
   - desktop-dark/light 1280×800에서 원 §3 첫 화면 AC를 모두 만족한다.
2. 구현한다.
   - `js/data.js`: `featured: true,` 3줄만 추가한다.
   - `index.html`: `#heroFeatured`를 추가하고 hero 순서·tagline 자리를 원 §3대로 맞춘다.
   - `js/main.js`: `renderFeaturedProjects`, 모달 연결, `setText('heroTagline', PROFILE.tagline);`
   - `css/style.css`: featured·hero의 비색 레이아웃만 추가한다. featured 카드의 색은 기존 `.project-card` 색 규칙의 selector에 `.featured-card`를 추가하는 방식으로만 준다.

## AC
- `T specs/featured.spec.js specs/content-data.spec.js specs/content-static.spec.js`
- `DI`
- `T <GS>`
