# Compact Step 8 — focus-overlays (r28·r29)

- 목적: §C6 `trapFocus`로 modal과 lightbox의 focus trap을 구현한다.
  - step 1의 공통 닫기 경로는 그대로 재사용하고, trap release만 그 경로에 연결한다.
  - `:focus-visible` outline도 이 step에서 구현한다.
- 예상 18분, hard timeout 30분. 선행: step 7. 공통 선행조건: §C0.
- 허용 파일(exact):
  - `js/main.js`
  - `css/style.css`: `:focus-visible`의 outline·outline-offset만. 기존 token만 쓴다.
  - `tests/specs/focus-modal.spec.js`(신규)
- runtime: §C4
- 금지:
  - 새 색·named color·`currentColor` 사용
  - 색 규칙 순서 변경
  - `renderFeaturedProjects` 렌더 구조 변경

## 작업
1. `focus-modal.spec.js`를 만들고 `OWN_SPEC`이 통과하는지 확인한 뒤 RED를 확인한다. 이 spec이 소유하는 assertion:
   - modal
     - Tab과 Shift+Tab이 modal 안에서만 순환한다.
     - button, backdrop, Esc 어느 쪽으로 닫아도 trigger로 focus가 돌아간다. trigger는 `#heroFeatured`와 `#projectGrid` 두 가지 모두 확인한다.
     - 두 번 열고 닫은 뒤에도 Tab 한 번에 한 칸씩 이동한다.
   - lightbox
     - `.shot-zoom`으로 연 뒤 lightbox 안에서 순환한다.
     - Esc를 한 번 누르면 lightbox만 닫히고 focus가 `.shot-zoom`으로 돌아간다. 이후 modal 안 순환이 다시 동작한다.
     - Esc를 다시 누르면 modal이 닫히고 trigger로 돌아간다.
   - release를 두 번 호출해도 안전하다. document keydown handler는 1개만 있다.
   - 키보드로 도달한 `.featured-card`, `.project-card`, modal 닫기 버튼, `.shot-zoom`의 outline-style이 none이 아니다.
2. 구현한다.
   - trap stack과 단일 handler를 둔다.
   - 공통 닫기 경로에 release를 연결한다.
   - 기존 lightbox Tab listener를 제거한다.

## AC
- `OWN_SPEC tests/specs/focus-modal.spec.js`
- `T specs/focus-modal.spec.js specs/featured.spec.js specs/modal-regression.spec.js specs/ui-regression.spec.js`
- `T <GS>`
