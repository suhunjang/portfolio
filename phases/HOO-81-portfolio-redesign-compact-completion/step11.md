# Compact Step 11 — final-verification (read-only)

- 목적: 최종 검증을 1회 실행하고, 재현 가능한 evidence를 기록한다. 실패하면 중단하고(§C8) 아무것도 수정하지 않는다.
- 예상 20분, hard timeout 30분. 선행: step 10. 공통 선행조건: §C0.
- 허용 파일: 없음(tracked 쓰기 0)
- runtime: §C4
- 금지:
  - tracked 파일 수정
  - 실패 후 수정하거나 재실행하는 것
  - review·push·PR(§C9, phase 밖에서 함)
  - 고정 SHOT ID 사용

## 작업
1. 아래 AC를 순서대로 실행한다. 하나라도 실패하면 즉시 중단하고 §C8에 따라 evidence를 남긴다.
2. 이번 SHOT 실행의 ID를 `tests/.tmp/compact/shot-id-final.txt`에서 읽는다. 그 ID의 manifest `tests/.tmp/compact/screenshots-${id}.json`을 읽는다.
3. `tests/.tmp/compact/final-evidence.json`에 다음을 기록한다.
   - `baselineHead`
   - `candidateHead`(`git rev-parse HEAD`)
   - 각 명령의 argv와 exit 코드
   - 사용한 `shotRunId`
   - 15개 경로와 SHA-256
   - lightbox project ID
4. 모두 PASS하면 runner가 §C9 절차로 넘어간다: testCommand → exact range review → `verify-final`.

## AC
- `SPEC_GATE`
- `T specs/content-data.spec.js specs/content-static.spec.js specs/featured.spec.js specs/final-contract.spec.js specs/focus-modal.spec.js specs/modal-regression.spec.js specs/ui-regression.spec.js specs/first-visit.spec.js specs/smoke.spec.js specs/design-intake.spec.js`
- `DI`
- `FULL`(`COMPACT_RUN_ID` 없이 실행하므로 screenshots suite는 skip)
- `AXE0`
- `VS`
- `SHOT final final`: 새 ID `final-<UTC>`를 쓰고, desktop-dark 단일 project로 실행한다.
