# Compact Step 1 — featured-cards (r18)

- 목적: featured data와 대표 카드(§C6 `renderFeaturedProjects`)를 만들고, 공통 닫기 경로에서 trigger로 focus를 돌려준다.
- 예상 18분, hard timeout 30분. 선행: step 0. 공통 선행조건: §C0.
- 허용 파일(exact):
  - `js/data.js`: `featured: true,` 3줄만
  - `index.html`: `#heroFeatured` 컨테이너만
  - `js/main.js`: 아래 범위만
    - `renderFeaturedProjects`
    - `openProjectModal(projectIndex, triggerElement = document.activeElement)` 시그니처, 그리고 `lastModalTrigger`에 저장하는 부분
    - container 위임
    - 기존 `closeProjectModal` 공통 경로: trigger가 `isConnected`이면 focus를 돌려주고 변수를 비운다
    - button·backdrop·Esc 중 공통 경로를 거치지 않는 경로를 공통 경로로 잇는 연결
  - `css/style.css`: `.featured-*` 비색 배치, 그리고 기존 `.project-card` 색 rule의 selector에 `.featured-card`를 대응으로 추가하는 것만
  - `tests/specs/featured.spec.js`(신규)
- runtime: §C4
- 금지: 새 색 선언, 문구·수치 변경, hero 순서·tagline, 섹션 구조, trap stack·lightbox·Tab 처리(step 8)

## 작업
1. `featured.spec.js`를 작성하고 `OWN_SPEC tests/specs/featured.spec.js`를 통과시킨 뒤 RED를 확인한다. 이 spec이 소유하는 assertion:
   - `featured === true`인 것은 정확히 index 1·5·7이고, 13개의 순서와 title이 그대로다.
   - `#heroFeatured` 구조가 §C1과 같다.
   - 카드 3개는 모두 `button[type=button]`이고 data-project가 1·5·7이다. 각각 `span` 2개(block), interactive 자손 0, background-image none이다.
   - click이나 Enter로 열리고 제목이 맞다.
   - button·backdrop·Esc 어느 방법으로 닫아도 trigger 카드로 focus가 돌아온다.
   - `.featured-card`의 color·backgroundColor·borderColor가 `#projectGrid .project-card`와 같다.
2. 구현한다.

## AC
- `OWN_SPEC tests/specs/featured.spec.js`
- `T specs/featured.spec.js specs/content-data.spec.js specs/modal-regression.spec.js`
- `DI`
- `T <GS>`
