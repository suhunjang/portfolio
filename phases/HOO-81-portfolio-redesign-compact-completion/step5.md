# Compact Step 5 — focused-fix

- 목적: 대응표의 focused 묶음과 `AXE0`를 실행하고, 실제로 실패한 것만 고친다.
- 예상 15분, hard timeout 30분. 선행: step 4. 공통 선행조건: §C0.
- 허용 파일(exact): `index.html`, `css/style.css`, `js/main.js`, `js/data.js`, `tests/specs/featured.spec.js`, `tests/specs/focus-modal.spec.js`
- 금지:
  - 신규 파일
  - 다른 spec 수정
  - §C1 계약 위반

## 작업
1. AC를 실행한다.
2. 실패하면 원인 파일만 허용 범위 안에서 고치고, AC 전체를 다시 실행한다.
3. 원인이 허용 범위 밖이거나 승인된 spec을 바꿔야 하는 경우 중단하고 보고한다.

## AC
- `OWN_SPEC tests/specs/featured.spec.js`
- `OWN_SPEC tests/specs/focus-modal.spec.js`
- `T specs/content-data.spec.js specs/content-static.spec.js specs/featured.spec.js specs/modal-regression.spec.js specs/focus-modal.spec.js specs/ui-regression.spec.js specs/first-visit.spec.js specs/smoke.spec.js specs/design-intake.spec.js`
- `DI`
- `T <GS>`
- `AXE0`
- `VS`
