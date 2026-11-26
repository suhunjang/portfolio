# Compact Step 8 — focus-overlays (r28·r29)

- 목적: §C6의 `trapFocus`로 modal과 lightbox의 focus trap을 만든다. step 1의 공통 닫기 경로를 재사용하고, 거기에 release를 연결한다. `:focus-visible`도 구현한다.
- 예상 18분, hard timeout 30분. 선행: step 7. 공통 선행조건: §C0.
- 허용 파일(exact):
  - `js/main.js`
  - `css/style.css`: `:focus-visible`의 outline만, 기존 token만 사용
  - `tests/specs/focus-modal.spec.js`(신규)
- runtime: §C4
- 금지: 새 색·named color·`currentColor`, 색 순서 변경, `renderFeaturedProjects`의 렌더 구조 변경

## 작업
1. `focus-modal.spec.js`를 작성하고 `OWN_SPEC`이 통과하는지 확인한 뒤 RED를 확인한다. 이 spec이 소유하는 assertion:
   - modal
     - Tab이 modal 안에서 순환한다.
     - 세 가지 닫기 경로 모두 trigger로 focus가 돌아온다(featured·grid trigger 둘 다).
     - 두 번 열고 닫아도 Tab이 한 칸씩 이동한다.
   - lightbox
     - lightbox 안에서 순환한다.
     - Esc 1회에 lightbox만 닫히고 focus가 `.shot-zoom`으로 돌아오며, modal 순환이 재개된다.
     - Esc 2회째에 modal이 닫히고 trigger로 돌아온다.
   - release를 두 번 불러도 안전하고, handler는 1개다.
   - outline-style이 none이 아니다.
2. 구현한다.

## AC
- `OWN_SPEC tests/specs/focus-modal.spec.js`
- `T specs/focus-modal.spec.js specs/featured.spec.js specs/modal-regression.spec.js specs/ui-regression.spec.js`
- `T <GS>`
