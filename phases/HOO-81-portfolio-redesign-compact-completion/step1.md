# Compact Step 1 — featured-cards (r18)

- 목적: featured data와 대표 카드(§C6 `renderFeaturedProjects`)를 구현하고, 공통 닫기 경로에서 trigger로 focus를 돌려준다(§C6 focus 복귀 분담).
- 예상 18분, hard timeout 30분. 선행: step 0. 공통 선행조건: §C0.
- 허용 파일(exact):
  - `js/data.js`: `featured: true,` 3줄만 추가
  - `index.html`: `#heroFeatured` 컨테이너만
  - `js/main.js`: 아래 다섯 가지만
    - `renderFeaturedProjects`
    - `openProjectModal(projectIndex, triggerElement = document.activeElement)` 시그니처, 그리고 `triggerElement`를 모듈 변수 `lastModalTrigger`에 저장
    - container click·keydown 위임
    - 기존 `closeProjectModal` 공통 경로: 저장된 trigger가 `isConnected`이면 그 요소로 focus를 돌리고 변수를 비움
    - button·backdrop·Esc 닫기 중 공통 경로를 거치지 않는 것이 있으면, 공통 경로를 호출하도록 연결만 수정
  - `css/style.css`: `.featured-*` 비색 배치, 그리고 기존 `.project-card` 색 rule의 selector에 `.featured-card` 대응 추가만
  - `tests/specs/featured.spec.js`(신규)
- runtime: §C4
- 금지:
  - 새 색 선언
  - 문구·수치
  - hero 순서·tagline(step 2 몫)
  - 섹션 구조
  - trap stack·lightbox·Tab 처리(step 8 몫)

## 작업
1. `featured.spec.js`를 작성한다. `OWN_SPEC tests/specs/featured.spec.js`를 통과한 뒤 RED를 확인한다. 이 spec이 소유하는 assertion:
   - `featured === true`는 정확히 1·5·7이다. 13개의 순서와 title은 그대로다.
   - `#heroFeatured` 구조가 §C1과 같다.
   - 카드 3개 각각:
     - `button[type=button]`, data-project 1·5·7
     - `span` 2개(block)
     - interactive 자손 0
     - background-image none
   - click·Enter로 열리고 제목이 맞다.
   - button·backdrop·Esc로 닫으면 trigger 카드로 focus가 돌아온다.
   - `.featured-card`의 color·backgroundColor·borderColor가 `#projectGrid .project-card`와 같다.
2. 구현한다.

## AC
- `OWN_SPEC tests/specs/featured.spec.js`
- `T specs/featured.spec.js specs/content-data.spec.js specs/modal-regression.spec.js`
- `DI`
- `T <GS>`
