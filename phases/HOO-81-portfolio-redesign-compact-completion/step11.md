# Compact Step 11 — final-verification (read-only)

- 목적: 최종 검증을 1회 수행하고, 재현 가능한 evidence를 남긴다. 실패하면 중단한다(§C8). 수정하지 않는다.
- 예상 20분, hard timeout 30분. 선행: step 10. 공통 선행조건 §C0.
- 허용 파일: 없음. tracked 파일은 쓰지 않는다.
- runtime: §C4
- 금지: tracked 파일 수정, 실패 후 수정·재실행, review·push·PR(§C9 phase 밖 절차)

## 작업
1. 아래 AC를 순서대로 실행한다. 하나라도 실패하면 즉시 중단하고 §C8에 따라 증거를 남긴다.
2. `tests/.tmp/compact/final-evidence.json`을 기록한다.
   - `baselineHead`, `candidateHead`(`git rev-parse HEAD`)
   - 각 명령의 argv와 exit
   - `screenshots-final.json`의 15개 경로와 SHA, lightbox project ID
3. 결과가 PASS이면 runner가 §C9 절차(testCommand → exact range review → `verify-final`)로 넘어간다.

## AC
- `SPEC_GATE`
- `T specs/content-data.spec.js specs/content-static.spec.js specs/featured.spec.js specs/final-contract.spec.js specs/focus-modal.spec.js specs/modal-regression.spec.js specs/ui-regression.spec.js specs/first-visit.spec.js specs/smoke.spec.js specs/design-intake.spec.js`
- `DI`
- `FULL`
- `AXE0`
- `VS`
- `SHOT final`
