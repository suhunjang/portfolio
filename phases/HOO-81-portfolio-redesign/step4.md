# Step 4 — scope-snapshot-gate

- 목적: 현재 identity 대조, 변경 판정, exact allowedPaths/runtime 정책 분류, unsafe 우선 판정, CLI gate를 완성한다. 이 step부터 모든 종료 검사는 identity 대조와 경로 안전을 경유하는 완성 CLI.
- 예상 20분 / 선행 0~3 / 공통 절차 설계 §15
- read-first: 설계 §11.1, §11.5(런타임 면제), §11.6(identity 경유), §11.7(규칙, 경로 안전 계약, schema, C, 비교 도구 step 4)
- tracked 허용(exact): `tests/scripts/scope-snapshot.mjs`(추가만), `tests/specs/scope-snapshot-gate.spec.js`(신규)
- runtime: R0(합성 저장소 포함)
- 금지: §15.7, step 1·2 함수 동작, 기존 spec·helper(import만)

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step4`
2. `scope-snapshot.mjs`에 step 4 API(`computeIdentity`, `checkIdentity`, `diffAgainstStart`, `classifyChanges`, `checkRuntimeVisible`, `checkSnapshotFirst`, `evaluateGate`, CLI `--check`) 추가. CLI 순서는 설계 §11.7(schema → identity → 상태 수집 → 판정)이며 identity 실패 시 어떤 파일도 쓰지 않는다. 판정 문자열·순서는 C와 같다.
3. `scope-snapshot-gate.spec.js` (node 전용, desktop-dark만)
   - `checkIdentity`(순수): 같음 → `[]`; projectRoot·head·base·harness.sourceCommit·harness.manifestHash·harness.distributionVersion·harness.lockSha256 각각 다름 → 해당 `identity-mismatch:{field}`; 여러 필드 → 지정 순서
   - `computeIdentity`(실제 저장소 읽기 전용): `parity-<pid>` snapshot identity와 같음, 다른 root(`tests/.tmp`) → throw
   - 변경 판정(가짜 current, h0·h1·h2 서로 다름)
     - `CLAUDE.md` 시작 ` M`/h1: 그대로 → 0; 원복(status 없음, h0) → `{content-changed, ' M', null}`·`outside-tests:CLAUDE.md`; 삭제(` D`, null) → `deleted`·`outside-tests:`; 같은 ` M`에서 h2 → `outside-tests:`
     - `tests/playwright.config.js` 시작 ` M`/h1(allow 밖): 그대로 → 0; h2 → `tests-changed:`; 삭제·원복 → `tests-changed:`; allow에 있으면 → 0
     - 깨끗한 `tests/helpers/theme.js` → ` M`/h' → `tests-changed:`; `?? tests/specs/wip.spec.js` 사라짐 → `tests-changed:`; walk 전용 `tests/fixtures/local.json` h1→h2 → `tests-changed:`
     - `README.md` hash 같고 xy 없음→`M ` → `status-changed:README.md`; 새 `?? docs/x.md` → `outside-tests:`
     - `?? .harness/runtime/a.json`, `phases/HOO-81-portfolio-redesign/step5.md` 변경 → 0; `.harness/policy.json`·`.harness/harness.lock.json` 변경 → `outside-tests:`
     - `?? tests/node_modules/x/index.js` → `runtime-visible:`; 새 `tests/specs/other.spec.js` → `tests-changed:`; `R  tests/x.js`←`README.md` → `outside-tests:README.md`와 `tests-changed:tests/x.js`
     - unsafe 우선: current.unsafe `['symlink:b','symlink:a']` + 다른 변경 + require-absent 위반 → 정확히 `snapshot-not-first:…`, `symlink:a`, `symlink:b`(변경 판정 없음), allow에 `a`가 있어도 같음
     - `checkSnapshotFirst`, `evaluateGate` 순서, 입력 불변
   - 합성 종료 gate: step 3 사례 (a) ignored symlink와 (b) 수정된 tracked symlink의 target 재변경을 `makeSyntheticRepo()`로 재현해 `evaluateGate(start, takeCurrent(start, { root: dir }), { allow: [링크 경로] })` → 각각 `symlink:{p}` 포함, 위반 ≥ 1
   - CLI subprocess(실제 저장소, `parity-{숫자}` 사용 후 삭제)
     - 없는 파일·schemaVersion `1.0` → exit 1
     - 방금 만든 parity snapshot + `--allow ''` → exit 0·`scope-snapshot: OK`
     - identity 거부(schema 정상): `projectRoot`=`/tmp/other`, `head`=40자 0, `base`=40자 f, `harness.sourceCommit`, `harness.manifestHash`, `harness.distributionVersion`=`9.9.9`, `harness.lockSha256`=64자 0 중 하나씩만 바꾼 별도 `parity-<n>` → 각각 exit 1, stderr `start snapshot identity mismatch: {field}`, snapshot sha256 불변, `<snapshot>-after.z` 미생성, 실행 전후 `git status --porcelain=v1 -z --untracked-files=all` 출력과 `git ls-files`의 tests 밖 파일 sha256 불변
     - 모든 실행 전후 snapshot sha256 불변

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-gate.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step4 && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step4.json --allow tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-gate.spec.js --require-absent tests/specs/scope-snapshot-gate.spec.js` → exit 0 (마지막 명령은 schema → 현재 identity → 경로 안전 → 판정을 거친다)
