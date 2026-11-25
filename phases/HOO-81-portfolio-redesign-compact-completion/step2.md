# Compact Step 2 — layout-interaction

- 목적: 원 §4(FINAL 섹션·nav·scrollspy), §6.1(focus trap), §7(섹션 레이아웃·print)과 resume 21~30 계약 가운데 현재 HEAD에 남은 실제 diff만 구현한다.
  - 범위: section 구조와 레이아웃, hit target, 비색 hover/active, modal/lightbox focus trap과 trigger 복귀, `:focus-visible`(기존 token만), print
- 예상 20분, hard timeout 30분. 선행: step 1.
- 남은 diff가 20분을 넘으면 구현 전에 plan batch로 2a(구조·레이아웃·hit)와 2b(focus·lightbox·print)로 나눈다.
- 허용 파일(exact): `index.html`, `js/main.js`, `css/style.css`, `tests/specs/focus-modal.spec.js`(신규)
- 금지: 색 값 변경(step 3 소관), 문구·수치·이미지 변경, 새 섹션 추가, `js/data.js` 수정

## 작업
1. `tests/specs/focus-modal.spec.js`를 먼저 작성하고, 실패하는 것을 확인한다(RED). 이 파일이 아래 assertion을 소유한다.
   - 모달: Tab과 Shift+Tab이 모달 안에서 순환한다. 닫기 버튼·backdrop·Esc로 닫으면 trigger로 focus가 돌아온다. trigger는 `#heroFeatured`와 `#projectGrid` 양쪽에서 확인한다. 두 번 열고 닫아도 Tab이 한 칸씩 움직인다.
   - lightbox: 모달 안의 `.shot-zoom`으로 연다. lightbox 안에서 focus가 순환한다. Esc 1회면 lightbox가 닫히고 focus가 `.shot-zoom`으로 돌아간다. Esc 2회면 모달까지 닫히고 trigger로 돌아간다.
   - 키보드로 도달한 `.featured-card`, `.project-card`, 모달 닫기 버튼, `.shot-zoom`의 `outline-style`이 `none`이 아니다.
   - FINAL 섹션 순서가 hero→Career→Projects→Strengths→About→Contact이고, nav 순서와 scrollspy가 이와 같다.
   - 375·768·1280에서 가로 스크롤이 없다.
2. 구현한다.
   - `index.html`: 섹션 subtree를 통째로 이동하고 nav 순서를 맞춘다.
   - `js/main.js`: trapFocus, lightbox trap, 기존 Tab 리스너 제거
   - `css/style.css`: 비색 레이아웃·hit target·hover/active transform·opacity, `@media print`(clamp 해제 포함), `:focus-visible` outline(기존 token)

## AC
- `T specs/focus-modal.spec.js specs/featured.spec.js specs/modal-regression.spec.js specs/ui-regression.spec.js specs/first-visit.spec.js specs/smoke.spec.js specs/content-static.spec.js`
- `DI`
- `T <GS>`
