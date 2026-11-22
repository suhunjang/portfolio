# Step 3 — a11y-print-polish

설계: §5.3(인쇄), §5.5

## 목표

접근성 기준을 충족하고, 인쇄(PDF) 스타일을 새 구조에 맞춘다.

## 변경 허용 파일

`index.html`, `css/style.css`, `css/themes.css`, `js/main.js`, `tests/**`

## 작업 (테스트 먼저)

1. `tests/specs/a11y.spec.js`를 작성한다.
   - axe 검사: 3개 viewport × dark/light에서 serious/critical 위반이 0건이어야 한다. `tests/specs/axe-known.json`을 빈 배열로 만든다.
   - 모달 포커스 트랩:
     - 모달을 연 뒤 Tab과 Shift+Tab을 각각 20회 눌러도 `document.activeElement`가 `#projectModal` 안에 있다.
     - lightbox에서도 같은 검사를 한다.
   - 키보드:
     - Tab만으로 theme toggle, nav 링크, 대표 카드, 프로젝트 카드에 도달할 수 있다.
     - 포커스된 요소의 computed outline이 none이 아니다.
   - heading: h1이 정확히 1개이고, heading level을 건너뛰지 않는다.
2. `tests/specs/print.spec.js`를 작성한다. `page.emulateMedia({ media: 'print' })` 상태에서 확인한다.
   - `#heroFeatured`, `#career`, `#projects`가 보인다.
   - `.theme-toggle`, `.menu-toggle`, `.modal`, `.lightbox`, `.scroll-hint`가 숨겨진다.
   - `page.pdf()`가 에러 없이 생성된다.
3. 구현:
   - 필요하면 모달과 lightbox에 포커스 트랩을 추가한다.
   - 대비가 부족한 토큰을 조정한다. 톤 범위 안에서 명도만 조정한다.
   - `@media print` 규칙을 새 섹션 순서와 대표 카드에 맞게 수정한다.

## 완료 기준

- `npm --prefix tests test`가 전부 통과한다.
- `axe-known.json`이 빈 배열이다.
