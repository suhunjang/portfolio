# Step 5 — scope-snapshot-gate

- 목적: 현재 identity 대조, 변경 판정, exact allowedPaths/runtime 정책 분류, unsafe 우선 판정(after.z 쓰기 전 즉시 실패), after.z 안전 쓰기, `runCheck`·CLI gate를 완성한다. 이 step부터 모든 종료 검사는 projectRoot·경로 유형 검사와 identity 대조를 경유하는 완성 CLI.
- 예상 20분 / 선행 0~4 / 공통 절차 설계 §15
- read-first: 설계 §11.1, §11.5(런타임 면제), §11.6(identity 경유), §11.7(규칙, projectRoot 유형, 경로 유형 계약, 실행 순서, schema, C, 비교 도구 step 5)
- tracked 허용(exact): `tests/scripts/scope-snapshot.mjs`(추가만), `tests/specs/scope-snapshot-gate.spec.js`(신규)
- runtime: R0(합성 저장소 포함)
- 금지: §15.7, step 1·2 함수 동작, 기존 spec·helper(import만)

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step5`
2. `scope-snapshot.mjs`에 step 5 API(`computeIdentity`, `checkIdentity`, `diffAgainstStart`, `classifyChanges`, `checkRuntimeVisible`, `checkSnapshotFirst`, `evaluateGate`, `writeAfterZ`, `runCheck`, CLI `--check`) 추가. `runCheck` 순서는 설계 §11.7 비교 도구 step 5이며 `takeCurrent`가 unsafe를 내면 `writeAfterZ`를 호출하지 않고 code 1. 판정 문자열·순서는 C와 같다.
3. `scope-snapshot-gate.spec.js` (node 전용, desktop-dark만, subprocess timeout 10초)
   - `checkIdentity`(순수): 같음 → `[]`; projectRoot·head·base·harness.sourceCommit·harness.manifestHash·harness.distributionVersion·harness.lockSha256 각각 다름 → 해당 `identity-mismatch:{field}`; 여러 필드 → 지정 순서
   - `computeIdentity`: 실제 저장소에서 `parity-<pid>` snapshot identity와 같음, 다른 root(`tests/.tmp`) → throw; 가짜 fs에서 root symlink, `.harness` 조상 symlink, lock FIFO → `UnsafePathError`이고 git `rev-parse --verify` 호출·lock open 없음
   - `writeAfterZ`(가짜 fs): 정상 → flags에 `O_NOFOLLOW`·`O_NONBLOCK`; leaf symlink·FIFO·디렉터리, 조상 `tests/.tmp` symlink → `UnsafePathError`이고 open 없음
   - 변경 판정(가짜 current, h0·h1·h2 서로 다름)
     - `CLAUDE.md` 시작 ` M`/h1: 그대로 → 0; 원복(status 없음, h0) → `{content-changed, ' M', null}`·`outside-tests:CLAUDE.md`; 삭제(` D`, null) → `deleted`·`outside-tests:`; 같은 ` M`에서 h2 → `outside-tests:`
     - `tests/playwright.config.js` 시작 ` M`/h1(allow 밖): 그대로 → 0; h2 → `tests-changed:`; 삭제·원복 → `tests-changed:`; allow에 있으면 → 0
     - 깨끗한 `tests/helpers/theme.js` → ` M`/h' → `tests-changed:`; `?? tests/specs/wip.spec.js` 사라짐 → `tests-changed:`; walk 전용 `tests/fixtures/local.json` h1→h2 → `tests-changed:`
     - `README.md` hash 같고 xy 없음→`M ` → `status-changed:README.md`; 새 `?? docs/x.md` → `outside-tests:`
     - `?? .harness/runtime/a.json`, `phases/HOO-81-portfolio-redesign/step6.md` 변경 → 0; `.harness/policy.json`·`.harness/harness.lock.json` 변경 → `outside-tests:`
     - `?? tests/node_modules/x/index.js` → `runtime-visible:`; 새 `tests/specs/other.spec.js` → `tests-changed:`; `R  tests/x.js`←`README.md` → `outside-tests:README.md`와 `tests-changed:tests/x.js`
     - unsafe 우선: current.unsafe `['symlink:b','non-regular:a']` + 다른 변경 + require-absent 위반 → 정확히 `snapshot-not-first:…`, `non-regular:a`, `symlink:b`(변경 판정 없음), allow에 `a`가 있어도 같음
     - `checkSnapshotFirst`, `evaluateGate` 순서, 입력 불변
   - 기록 대상 unsafe 시 after.z 보존(합성 저장소, 4가지 = 기존 after.z 있음/없음 × 기록 대상 FIFO `tests/specs/p.fifo`/symlink `link-x → <outside>/secret.txt`): 합성 저장소에 `.harness/harness.lock.json`(identity 3값 포함)과 commit을 만들고, `rev-parse --verify BASE^{commit}`만 성공으로 대체하고 나머지는 실제 git으로 전달하는 git 래퍼로 `computeIdentity`·`takeCurrent`를 써서 정상 `tests/.tmp/start-snapshot-parity-1.json`을 만든다. "있음"이면 `…-after.z`에 고정 bytes를 쓰고 mtime을 기록한다. 그다음 FIFO 또는 symlink를 추가한다.
     - `runCheck({ startFile, allow: [그 경로] }, { git: 래퍼, fs, root: dir })` → code 1, stderr에 `non-regular:tests/specs/p.fifo` 또는 `symlink:link-x`, 기록용 fs에 after.z 경로 open 없음; "있음"이면 after.z bytes·mtime 불변, "없음"이면 after.z 미생성; snapshot sha256 불변
     - 같은 4가지를 C(cwd `dir`, `designBlock('inline 범위 검사 C')`)로 실행 → exit 1, 같은 stderr 항목, after.z bytes·mtime 불변 또는 미생성, 멈추지 않음
   - CLI 합성(cwd `dir`, `node <프로젝트>/tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-parity-1.json --allow ''`): `tests/.tmp → <outside>/tmpdir` 링크 → exit 1, stderr `unsafe path: symlink:tests/.tmp`, 외부 디렉터리에 after.z 미생성·bytes·mtime 불변
   - CLI 실제 저장소(`parity-{숫자}` 사용 후 삭제)
     - 방금 만든 parity snapshot + `--allow ''` → exit 0·`scope-snapshot: OK`, after.z는 regular file
     - `<parity>-after.z`를 FIFO로 미리 만든 경우 → exit 1, `non-regular:…-after.z`, 멈추지 않음, FIFO 유지
     - identity 거부(schema 정상): `projectRoot`=`/tmp/other`, `head`=40자 0, `base`=40자 f, `harness.sourceCommit`, `harness.manifestHash`, `harness.distributionVersion`=`9.9.9`, `harness.lockSha256`=64자 0 중 하나씩만 바꾼 별도 `parity-<n>` → 각각 exit 1, stderr `start snapshot identity mismatch: {field}`, snapshot sha256 불변, `<snapshot>-after.z` 미생성, 실행 전후 `git status --porcelain=v1 -z --untracked-files=all` 출력과 `git ls-files`의 tests 밖 파일 sha256 불변
     - 모든 실행 전후 snapshot sha256 불변

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-gate.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step5 && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step5.json --allow tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-gate.spec.js --require-absent tests/specs/scope-snapshot-gate.spec.js` → exit 0 (마지막 명령은 projectRoot 유형 → 경로 유형 → schema → 현재 identity → 상태 수집(unsafe면 after.z 미접촉 exit 1) → after.z 안전 쓰기 → 판정을 거친다)
- spec 단독 실행에 기록 대상 FIFO·symlink × 기존 after.z 있음·없음 4가지가 `runCheck`와 C 양쪽에서 exit 1, 기존 after.z bytes·mtime 불변, 신규 after.z 미생성으로 통과한다.
