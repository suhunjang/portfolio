# Step 2 — scope-snapshot-gate

- 목적: 변경 판정, exact allowedPaths/runtime 정책 분류, CLI gate와 나머지 합성 사례를 완성한다. 이 step부터 종료 검사는 완성 CLI.
- 예상 19분 / 선행 0~1 / 공통 절차 설계 §15
- read-first: 설계 §11.1, §11.5(런타임 면제), §11.7(규칙, C, 비교 도구 step 2)
- tracked 허용(exact): `tests/scripts/scope-snapshot.mjs`(추가만), `tests/specs/scope-snapshot-gate.spec.js`(신규)
- runtime: R0
- 금지: §15.7, step 1 함수 동작, `scope-snapshot-state.spec.js`

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step2`
2. `scope-snapshot.mjs`에 step 2 API(`diffAgainstStart`, `classifyChanges`, `checkRuntimeVisible`, `checkSnapshotFirst`, `evaluateGate`, CLI `--check`) 추가. 문자열·순서는 C와 같다.
3. `scope-snapshot-gate.spec.js` (node 전용, desktop-dark만, 가짜 git·fs, h0·h1·h2 서로 다름)
   - `CLAUDE.md` 시작 ` M`/h1: 그대로 → 0; 원복(status 없음, h0) → `{content-changed, xyBefore ' M', xyAfter null}`·`outside-tests:CLAUDE.md`; 삭제(` D`, null) → `deleted`·`outside-tests:`; 같은 ` M`에서 h2 → `{content-changed, ' M', ' M'}`·`outside-tests:`
   - 기존 `tests/playwright.config.js` 시작 ` M`/h1(allow 밖): 그대로 → 0; 시작·종료 ` M`이고 h2 → `tests-changed:tests/playwright.config.js`; 삭제 → `tests-changed:`(deleted); 원복 → `tests-changed:`(xyAfter null); allow에 있으면 → 0
   - 깨끗한 추적 `tests/helpers/theme.js` → ` M`/h' → `tests-changed:`; 미추적 `?? tests/specs/wip.spec.js` 사라짐 → `tests-changed:`; walk 전용 `tests/fixtures/local.json` h1→h2 → `tests-changed:`
   - `README.md` hash 같고 xy 없음→`M ` → `status-changed:README.md`; 깨끗한 README → ` M`/h' → `outside-tests:`; 새 `?? docs/x.md` → `outside-tests:`
   - `?? .harness/runtime/a.json`, `phases/HOO-81-portfolio-redesign/step3.md` 변경 → 0; `.harness/policy.json`·`.harness/harness.lock.json` 변경 → 각각 `outside-tests:`
   - `?? tests/node_modules/x/index.js` → `runtime-visible:`; 새 allow spec → 0; 새 `tests/specs/other.spec.js` → `tests-changed:`; `R  tests/x.js`←`README.md`(README null) → `outside-tests:README.md`와 `tests-changed:tests/x.js`
   - `checkSnapshotFirst`, `evaluateGate` 순서, 입력 불변
   - CLI subprocess(`parity-{숫자}` snapshot 사용 후 삭제): 없는 파일·깨진 JSON·stepId≠파일명·statusZHex 손상 → exit 1; 방금 만든 parity snapshot + `--allow ''` → exit 0·`scope-snapshot: OK`; 모든 실행 전후 snapshot sha256 불변

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-gate.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step2 && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step2.json --allow tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-gate.spec.js --require-absent tests/specs/scope-snapshot-gate.spec.js` → exit 0
