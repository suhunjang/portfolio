# Compact Step 11 — final-verification (read-only)

- 목적: 최종 검증을 1회 실행하고, 재현 가능한 evidence를 남긴다. 실패하면 중단한다(§C8).
- 예상 20분, hard timeout 30분. 선행 step 10. 공통 선행조건 §C0.
- 허용 파일: 없음
- runtime: §C4
- 금지:
  - tracked 파일 쓰기
  - 실패 후 수정·재실행
  - review, push, PR(§C9)
  - 고정 SHOT ID

## 작업
1. AC를 순서대로 실행한다. 하나라도 실패하면 그 자리에서 중단하고 §C8에 따라 evidence를 남긴다.
2. `tests/.tmp/compact/shot-id-final.txt`에서 ID를 읽고, `tests/.tmp/compact/screenshots-${id}.json`을 읽는다.
3. `tests/.tmp/compact/final-evidence.json`에 아래 항목을 기록한다.
   - `baselineHead`, `candidateHead`
   - 각 명령의 argv와 exit
   - `shotRunId`
   - 15개 파일의 경로와 SHA
   - lightbox에 사용한 project ID
4. 모두 PASS하면 runner가 §C9의 testCommand → exact range review → `verify-final`로 넘어간다.

## AC
- `SPEC_GATE`
- `T specs/content-data.spec.js specs/content-static.spec.js specs/featured.spec.js specs/final-contract.spec.js specs/focus-modal.spec.js specs/modal-regression.spec.js specs/ui-regression.spec.js specs/first-visit.spec.js specs/smoke.spec.js specs/design-intake.spec.js`
- `DI`
- `FULL`(screenshots suite는 skip)
- `AXE0`
- `VS`
- `SHOT final final`
