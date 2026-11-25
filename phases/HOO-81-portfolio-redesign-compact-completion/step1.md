# Compact Step 1 — featured-cards (r18)

- 목적: featured data와 대표 카드를 구현한다(§C6 `renderFeaturedProjects`).
- 예상 18분, hard timeout 30분. 선행 step 0. 공통 선행조건은 §C0.
- 허용 파일(exact):
  - `js/data.js`: `featured: true,` 3줄만
  - `index.html`: `#heroFeatured` 컨테이너만
  - `js/main.js`: `renderFeaturedProjects`, `openProjectModal` 시그니처, 위임만
  - `css/style.css`: `.featured-*` 비색 배치와, 기존 `.project-card` 색 rule의 selector에 `.featured-card` 대응을 추가하는 것만
  - `tests/specs/featured.spec.js`(신규)
- runtime: §C4
- 금지:
  - 새 색 선언
  - 문구·수치 변경
  - hero 순서·tagline 변경(step 2에서 함)
  - 섹션 구조 변경

## 작업
1. `featured.spec.js`를 작성한다. `OWN_SPEC tests/specs/featured.spec.js`가 통과한 뒤 RED를 확인한다. 이 spec이 소유하는 assertion:
   - `featured === true`인 PROJECTS가 정확히 index 1·5·7이다.
   - 13개 project의 순서와 title이 바뀌지 않았다.
   - `#heroFeatured` 구조가 §C1과 같다.
   - 카드는 3개이고 각각:
     - `button[type=button]`, data-project 1·5·7
     - `span` 2개(block)
     - interactive 자손 0개
     - background-image none
   - click과 Enter로 모달이 열리고 제목이 맞다.
   - button, backdrop, Esc 어느 방법으로 닫아도 trigger 카드로 focus가 돌아온다.
   - `.featured-card`의 color·backgroundColor·borderColor가 `#projectGrid .project-card`와 같다.
2. 구현한다.

## AC
- `OWN_SPEC tests/specs/featured.spec.js`
- `T specs/featured.spec.js specs/content-data.spec.js specs/modal-regression.spec.js`
- `DI`
- `T <GS>`
