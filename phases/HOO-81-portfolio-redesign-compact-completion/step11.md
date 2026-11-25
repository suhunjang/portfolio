# Compact Step 11 — final-verification (read-only)

- 목적: 최종 검증을 1회 수행하고, 재현 가능한 evidence를 남긴다. 실패하면 중단하고 §C8을 따른다.
- 예상 20분, hard timeout 30분. 선행: step 10. 공통 선행조건: §C0.
- 허용 파일: 없음.
- runtime: §C4.
- 금지: tracked 파일 쓰기, 실패 후 수정·재실행, review·push·PR(§C9 소관), 고정된 SHOT ID 사용.

## 작업
1. 아래 AC를 순서대로 실행한다. 실패하면 즉시 중단하고 §C8 절차대로 evidence를 남긴다.
2. `shot-id-final.txt`에서 이번 실행의 ID를 읽고, 그 ID의 manifest를 읽는다.
3. `tests/.tmp/compact/final-evidence.json`에 다음을 기록한다.
   - `baselineHead`, `candidateHead`
   - 실행한 각 명령의 argv와 exit
   - `shotRunId`
   - 경로 15개와 각 SHA
   - lightbox에서 쓴 project ID
4. PASS하면 runner가 §C9의 testCommand → review → `verify-final`로 진행한다.

## AC
- `SPEC_GATE`
- `T specs/content-data.spec.js specs/content-static.spec.js specs/featured.spec.js specs/final-contract.spec.js specs/focus-modal.spec.js specs/modal-regression.spec.js specs/ui-regression.spec.js specs/first-visit.spec.js specs/smoke.spec.js specs/design-intake.spec.js`
- `DI`
- `FULL`(screenshots는 skip)
- `AXE0`
- `VS`
- `SHOT final final`
