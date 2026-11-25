# Compact Step 7 — final-verification (read-only)

- 목적: 최종 검증을 1회 수행하고, 재현 가능한 evidence를 기록한다. tracked 파일은 쓰지 않는다.
- 예상 18분, hard timeout 30분. 선행: step 6. 공통 선행조건: §C0.
- 허용 파일: 없음. runtime에 쓰는 것은 `tests/.tmp/**`, `tests/screenshots/**`뿐이다.
- 금지:
  - 어떤 tracked 파일 수정
  - review·push·PR 실행. 이것들은 설계 §C9의 phase 밖 운영 절차에서 한다.

## 작업
1. 아래 AC를 순서대로 실행한다.
2. `tests/.tmp/compact/final-evidence.json`을 기록한다. 기록 항목:
   - `baselineHead`(step 0 evidence), `candidateHead`(`git rev-parse HEAD`)
   - 각 명령의 argv와 exit
   - §C7 screenshot 기대 목록, 실제 목록, 각 SHA-256
   - lightbox project ID
3. 결과 판정:
   - 기대 목록과 실제 목록이 다르거나, exit가 0이 아닌 명령이 하나라도 있으면 FAIL이다. 원인 step을 보고하고 중단한다.
   - PASS하면 runner가 §C9의 testCommand → exact range review → `verify-final`로 넘어간다.

## AC
- `SPEC_GATE`
- `FULL`
- `AXE0`
- `VS`
- `T specs/screenshots.spec.js specs/final-contract.spec.js specs/featured.spec.js specs/focus-modal.spec.js specs/design-intake.spec.js`
