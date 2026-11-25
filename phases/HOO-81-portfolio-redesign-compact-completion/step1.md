# Compact Step 1 — featured-hero

- 목적: 현재 HEAD 대비 아직 남은 실제 diff만 구현한다. 대상은 featured data, 대표 카드(설계 §C6 `renderFeaturedProjects`), hero 첫 화면(원 §3)이다.
- 예상 20분, hard timeout 30분. 선행: step 0. 공통 선행조건: §C0.
- 허용 파일(exact): `js/data.js`, `index.html`, `js/main.js`, `css/style.css`, `tests/specs/featured.spec.js`(신규)
- 금지:
  - 색 값 변경(step 4 몫)
  - 문구·수치 변경
  - `css/themes.css` 수정
  - 섹션 순서·hero 밖 구조 변경(step 2 몫)
  - focus trap 구현(step 3 몫)

## 작업
1. `tests/specs/featured.spec.js`를 작성하고, `OWN_SPEC tests/specs/featured.spec.js`를 통과한 뒤 RED를 확인한다.
   - 이 spec이 소유하는 assertion:
     - PROJECTS 중 `featured === true`인 것이 정확히 index 1·5·7이다. 13개 순서와 title은 그대로다.
     - `#heroFeatured` 구조가 §C1과 같다.
     - 카드 3개: `button[type=button]`, data-project 1·5·7, `span` 정확히 2개(block), interactive 자손 0개, background-image none.
     - click·Enter로 열고 제목이 맞는다. 닫기 버튼·backdrop·Esc로 닫으면 trigger 카드로 focus가 돌아온다.
     - hero 직계 자식 순서가 원 §3과 같고, `#heroTagline` = `PROFILE.tagline`이다.
     - 375·768·1280에서 가로 스크롤 0, featured 열은 1/2/3이다.
     - desktop-dark/light 1280×800에서 원 §3 첫 화면 AC를 모두 만족한다.
2. 구현한다.
   - `js/data.js`: `featured: true,` 3줄을 index 1·5·7의 title 다음 줄에 넣는다.
   - `index.html`: `#heroFeatured`, hero 순서, tagline.
   - `js/main.js`:
     - `renderFeaturedProjects()`를 추가하고 grid render 직후 1회 호출한다.
     - `openProjectModal(projectIndex, triggerElement = document.activeElement)` 시그니처로 바꾼다.
     - 위임 처리와 `setText('heroTagline', PROFILE.tagline);`를 넣는다.
   - `css/style.css`: featured·hero의 비색 레이아웃만 넣는다. featured 색은 기존 `.project-card` 색 규칙의 selector에 `.featured-card`를 추가하는 방식으로만 준다.

## AC
- `OWN_SPEC tests/specs/featured.spec.js`
- `T specs/featured.spec.js specs/content-data.spec.js specs/content-static.spec.js specs/modal-regression.spec.js`
- `DI`
- `T <GS>`
