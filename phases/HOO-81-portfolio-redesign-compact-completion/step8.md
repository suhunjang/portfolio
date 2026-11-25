# Compact Step 8 — focus-overlays (r28·r29)

- 목적: §C6 `trapFocus`로 modal·lightbox focus trap과 trigger 복귀를 구현한다. `:focus-visible`(기존 token)도 포함한다.
- 예상 18분, hard timeout 30분. 선행: step 7. 공통 선행조건 §C0.
- 허용 파일(exact):
  - `js/main.js`
  - `css/style.css`: `:focus-visible`의 outline·outline-offset만, 기존 token만
  - `tests/specs/focus-modal.spec.js`: 신규
- runtime: §C4
- 금지: 새 색·named color·`currentColor`, 색 규칙 순서, `renderFeaturedProjects` 렌더 구조 변경

## 작업
1. `focus-modal.spec.js`를 만들고 `OWN_SPEC`을 통과한 뒤 RED를 확인한다. 소유 assertion:
   - **modal**
     - Tab과 Shift+Tab이 modal 안에서 순환한다.
     - 닫기 버튼, backdrop, Esc로 닫으면 trigger로 focus가 돌아온다. trigger는 `#heroFeatured`와 `#projectGrid` 두 경우를 모두 확인한다.
     - 두 번 열고 닫은 뒤에도 Tab 한 번에 한 칸씩 이동한다.
   - **lightbox**
     - `.shot-zoom`으로 열면 lightbox 안에서 순환한다.
     - Esc 1회: lightbox만 닫히고 `.shot-zoom`으로 focus가 돌아가며 modal 순환이 재개된다.
     - Esc 2회째: modal이 닫히고 trigger로 돌아간다.
   - release를 두 번 불러도 안전하고, document keydown handler는 1개다.
   - 키보드로 도달한 `.featured-card`, `.project-card`, modal 닫기, `.shot-zoom`의 outline-style이 none이 아니다.
2. 구현한다. trap stack과 단일 handler를 두고, 기존 lightbox Tab listener를 제거한다.

## AC
- `OWN_SPEC tests/specs/focus-modal.spec.js`
- `T specs/focus-modal.spec.js specs/featured.spec.js specs/modal-regression.spec.js specs/ui-regression.spec.js`
- `T <GS>`
