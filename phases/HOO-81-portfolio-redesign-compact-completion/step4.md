# Compact Step 4 — focused-fix

- 목적: 대응표의 focused 묶음과 `AXE0`를 실행하고, 실제로 실패한 항목만 수정한다.
- 예상 15분, hard timeout 30분. 선행: step 3.
- 허용 파일(exact): `index.html`, `css/style.css`, `js/main.js`, `js/data.js`, `tests/specs/featured.spec.js`, `tests/specs/focus-modal.spec.js`
- 금지: 신규 파일 생성, 다른 spec 수정, 색 계약 위반, `js/data.js`의 featured 3줄 외 변경

## 작업
1. 아래 AC를 실행한다.
2. 실패하면 그 원인 파일만 허용 범위 안에서 수정하고, AC 전체를 다시 실행한다.
3. 원인이 허용 범위 밖이거나, 승인된 spec을 바꿔야 하면 중단하고 보고한다.

## AC
- `T specs/content-data.spec.js specs/content-static.spec.js specs/featured.spec.js specs/modal-regression.spec.js specs/focus-modal.spec.js specs/ui-regression.spec.js specs/first-visit.spec.js specs/smoke.spec.js specs/design-intake.spec.js specs/axe-helper.spec.js`
- `DI`
- `T <GS>`
- `AXE0`
- `VS`
