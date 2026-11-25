# Compact Step 3 — focus-overlays

- 목적: 설계 §C6 `trapFocus`로 modal·lightbox focus trap과 trigger 복귀를 구현한다. `:focus-visible` outline도 추가한다.
- 예상 18분, hard timeout 30분. 선행: step 2. 공통 선행조건: §C0.
- 허용 파일(exact): `js/main.js`, `css/style.css`(`:focus-visible`의 outline·outline-offset만, 기존 token만), `tests/specs/focus-modal.spec.js`(신규)
- 금지:
  - 새 색, named color, `currentColor`
  - 색 규칙 순서 변경
  - `renderFeaturedProjects`의 렌더 구조 변경

## 작업
1. `tests/specs/focus-modal.spec.js`를 작성하고, `OWN_SPEC tests/specs/focus-modal.spec.js`를 통과한 뒤 RED를 확인한다.
   - 이 spec이 소유하는 assertion:
     - modal: Tab·Shift+Tab이 안에서 순환한다. 닫기 버튼·backdrop·Esc로 닫으면 trigger로 복귀한다(`#heroFeatured`, `#projectGrid` 둘 다). 2회 열고 닫아도 Tab이 한 칸씩 이동한다.
     - lightbox: modal 안 `.shot-zoom`으로 연다. 안에서 순환한다. Esc 1회면 lightbox만 닫히고 `.shot-zoom`으로 돌아가며 modal 순환이 재개된다. Esc 2회째에 modal이 닫히고 trigger로 돌아간다.
     - release를 두 번 호출해도 안전하다. document keydown handler가 1개다.
     - 키보드로 도달한 `.featured-card`·`.project-card`·modal 닫기·`.shot-zoom`의 outline-style이 none이 아니다.
2. 구현한다: trap stack과 단일 handler, modal·lightbox 연결, 기존 lightbox Tab listener 제거.

## AC
- `OWN_SPEC tests/specs/focus-modal.spec.js`
- `T specs/focus-modal.spec.js specs/featured.spec.js specs/modal-regression.spec.js specs/ui-regression.spec.js`
- `T <GS>`
