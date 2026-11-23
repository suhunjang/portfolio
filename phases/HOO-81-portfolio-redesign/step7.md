# Step 7 — scope-snapshot-identity

- 목적: 현재 identity 계산·대조와 순수 변경·정책 판정(unsafe 우선 포함)을 만든다. 파일 쓰기·CLI는 없다.
- 예상 18분 / 선행 0~6 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.1, §11.5(런타임 면제), §11.7(규칙, projectRoot 유형, 경로 유형 계약, schema, C의 판정 문자열·순서, 비교 도구 step 7)
- tracked 허용(exact): `tests/scripts/scope-snapshot.mjs`(추가만), `tests/specs/scope-snapshot-identity.spec.js`(신규)
- runtime: R0
- 금지: §15.7, step 1~4 함수 동작, `writeAfterZ`·`runCheck`·CLI(step 8), 파일 쓰기

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step7`
2. `scope-snapshot.mjs`에 step 7 API(`computeIdentity`, `checkIdentity`, `diffAgainstStart`, `classifyChanges`, `checkRuntimeVisible`, `checkSnapshotFirst`, `evaluateGate`) 추가. 판정 문자열·순서는 C와 같다.
3. `scope-snapshot-identity.spec.js` (node 전용, desktop-dark만, subprocess timeout 10초)
   - `checkIdentity`(순수): 같음 → `[]`; projectRoot·head·base·harness.sourceCommit·harness.manifestHash·harness.distributionVersion·harness.lockSha256 각각 다름 → 해당 `identity-mismatch:{field}`; 여러 필드 → 지정 순서
   - `computeIdentity`: 실제 저장소에서 `parity-<pid>` snapshot identity와 같음(끝나면 parity 삭제), 다른 root(`tests/.tmp`) → throw; 가짜 fs·git에서 root symlink, `.harness` 조상 symlink, lock FIFO → `UnsafePathError`이고 git `rev-parse --verify` 호출·lock open 없음
   - 변경 판정(가짜 current, h0·h1·h2 서로 다름)
     - `CLAUDE.md` 시작 ` M`/h1: 그대로 → 0; 원복(status 없음, h0) → `{content-changed, ' M', null}`·`outside-tests:CLAUDE.md`; 삭제(` D`, null) → `deleted`·`outside-tests:`; 같은 ` M`에서 h2 → `outside-tests:`
     - `tests/playwright.config.js` 시작 ` M`/h1(allow 밖): 그대로 → 0; h2 → `tests-changed:`; 삭제·원복 → `tests-changed:`; allow에 있으면 → 0
     - 깨끗한 `tests/helpers/theme.js` → ` M`/h' → `tests-changed:`; `?? tests/specs/wip.spec.js` 사라짐 → `tests-changed:`; walk 전용 `tests/fixtures/local.json` h1→h2 → `tests-changed:`
     - `README.md` hash 같고 xy 없음→`M ` → `status-changed:README.md`; 새 `?? docs/x.md` → `outside-tests:`
     - `?? .harness/runtime/a.json`, `phases/HOO-81-portfolio-redesign/step10.md` 변경 → 0; `.harness/policy.json`·`.harness/harness.lock.json` 변경 → `outside-tests:`
     - `?? tests/node_modules/x/index.js` → `runtime-visible:`; 새 `tests/specs/other.spec.js` → `tests-changed:`; `R  tests/x.js`←`README.md` → `outside-tests:README.md`와 `tests-changed:tests/x.js`
     - unsafe 우선: current.unsafe `['symlink:b','non-regular:a']` + 다른 변경 + require-absent 위반 → 정확히 `snapshot-not-first:…`, `non-regular:a`, `symlink:b`(변경 판정 없음), allow에 `a`가 있어도 같음
     - `checkSnapshotFirst`, `evaluateGate` 전체 순서(snapshot-not-first → 변경 경로 오름차순 → runtime-visible), 입력 불변

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-identity.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step7` (마지막은 `reused`)
2. 범위 gate: `python3 -I - step7 'tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-identity.spec.js' 'tests/specs/scope-snapshot-identity.spec.js' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
