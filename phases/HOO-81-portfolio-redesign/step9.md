# Step 9 — scope-snapshot-parity

- 목적: inline C와 `runCheck`·CLI의 통합 parity, 기록 대상 unsafe 시 after.z 보존, CLI의 identity 거부·runtime 링크 거부를 실행 검증한다. 코드 추가 없이 테스트만. 이 step부터 종료 gate는 CLI다.
- 예상 19분 / 선행 0~8 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §11.6, §11.7(규칙, projectRoot 유형, 경로 유형 계약, 실행 순서, C, 비교 도구 step 7·8, 테스트 격리), §12(합성 저장소 예외); `tests/helpers/synthetic-repo.js`
- tracked 허용(exact): `tests/specs/scope-snapshot-parity.spec.js`(신규)
- runtime: R0(합성 저장소, `<pid>-outside/`, 실제 저장소 `tests/.tmp/start-snapshot-parity-{숫자}.json`과 그 after.z)
- 금지: §15.7, `scope-snapshot.mjs`·`start-snapshot.py`·helper 수정, 실제 저장소 비runtime 경로에 symlink·FIFO 생성, 권한 변경

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step9`
2. `scope-snapshot-parity.spec.js` (node 전용, desktop-dark만, 모든 subprocess timeout 10초, 각 사례 전후 대상 디렉터리의 목록·sha256·mtime 비교)
   - 합성 준비(각 사례 새 `makeSyntheticRepo()`; 사례 (i)~(v), after.z 보존 4가지, CLI 합성을 포함한 이 spec의 모든 합성 저장소 공통): 첫 `git add`·commit 전에 Node `fs`로 루트 `.gitignore`를 정확히 `tests/.tmp/` 한 줄(끝 개행 1개)로 작성하고, `.harness/harness.lock.json`(identity 3값 포함), `tracked.txt`, `tests/specs/a.spec.js`와 함께 `add -A`로 초기 commit에 포함한다. `rev-parse --verify BASE^{commit}`만 성공으로 대체하고 나머지는 실제 git으로 전달하는 git 래퍼로 `computeIdentity`·`takeCurrent`를 써서 정상 `tests/.tmp/start-snapshot-parity-1.json`을 만든다(사례 (v)는 아래 별도 준비이며 같은 `.gitignore` 초기 commit을 쓴다)
   - runtime 비노출 assertion: 시작 snapshot 생성 직후, 그리고 C 또는 `runCheck`가 `tests/.tmp/start-snapshot-parity-1-after.z`를 만든 직후마다 `git -C <dir> status --porcelain=v1 -z --untracked-files=all` 출력을 `parseStatusZ`로 파싱해 `tests/.tmp/start-snapshot-parity-1.json`과 `tests/.tmp/start-snapshot-parity-1-after.z`가 path·origPath 어디에도 없음을 assert한다
   - C·`runCheck` parity(같은 합성 상태에서 둘을 각각 실행, C는 cwd `dir` + `designBlock('inline 범위 검사 C')`): (i) 변경 없음 → 둘 다 code 0·`scope-snapshot: OK`; (ii) `tracked.txt` 수정(allow 밖) → 둘 다 code 1·위반 줄 정확히 `outside-tests:tracked.txt`; (iii) 새 `tests/specs/x.spec.js`(allow 밖) → `tests-changed:tests/specs/x.spec.js`; (iv) `--require-absent tracked.txt` → `snapshot-not-first:tracked.txt`; (v) stage만 바뀐 경우 — 준비: 초기 commit 후 `tracked.txt` 내용을 수정하고 stage하지 않은 상태에서 시작 snapshot `tests/.tmp/start-snapshot-parity-1.json`을 만든다 → 파일 내용은 그대로 둔 채 `git -C <dir> add tracked.txt`(helper의 정확한 경로 add)로 stage한다 → assertion 전에 시작 snapshot `xy['tracked.txt']`가 정확히 `' M'`, 현재 `takeCurrent`의 `xy['tracked.txt']`가 정확히 `'M '`, 시작 `files['tracked.txt']`와 현재 `files['tracked.txt']` SHA-256이 같음을 확인 → C와 `runCheck` 모두 code 1·위반 줄 정확히 `status-changed:tracked.txt`. 각 사례에서 두 결과의 exit code와 위반 줄 목록이 같고, 생성된 after.z 내용이 같다
   - 기록 대상 unsafe 시 after.z 보존(4가지 = 기존 after.z 있음/없음 × 기록 대상 FIFO `tests/specs/p.fifo`/symlink `link-x → <outside>/secret.txt`): "있음"이면 `…-after.z`에 고정 bytes를 쓰고 mtime을 기록한 뒤 FIFO 또는 symlink를 추가한다
     - `runCheck({ startFile, allow: [그 경로] }, { git: 래퍼, fs: 기록용 fs, root: dir })` → code 1, stderr에 `non-regular:tests/specs/p.fifo` 또는 `symlink:link-x`, 기록에 after.z 경로 open 없음; "있음"이면 after.z bytes·mtime 불변, "없음"이면 after.z 미생성; snapshot sha256 불변
     - 같은 4가지를 C로 실행 → exit 1, 같은 stderr 항목, after.z bytes·mtime 불변 또는 미생성, 멈추지 않음
   - CLI 합성(cwd `dir`, `node <프로젝트>/tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-parity-1.json --allow ''`): `tests/.tmp → <outside>/tmpdir` 링크 → exit 1, stderr `unsafe path: symlink:tests/.tmp`, 외부 디렉터리에 after.z 미생성·bytes·mtime 불변
   - CLI 실제 저장소(`parity-{숫자}` 사용 후 삭제)
     - `<parity>-after.z`를 FIFO로 미리 만든 경우 → exit 1, `non-regular:…-after.z`, 멈추지 않음, FIFO 유지
     - identity 거부(schema 정상): `projectRoot`=`/tmp/other`, `head`=40자 0, `base`=40자 f, `harness.sourceCommit`, `harness.manifestHash`, `harness.distributionVersion`=`9.9.9`, `harness.lockSha256`=64자 0 중 하나씩만 바꾼 별도 `parity-<n>` → 각각 exit 1, stderr `start snapshot identity mismatch: {field}`, snapshot sha256 불변, `<snapshot>-after.z` 미생성, 실행 전후 `git status --porcelain=v1 -z --untracked-files=all` 출력과 `git ls-files`의 tests 밖 파일 sha256 불변
     - 모든 실행 전후 snapshot sha256 불변

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-parity.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step9 && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step9.json --allow tests/specs/scope-snapshot-parity.spec.js --require-absent tests/specs/scope-snapshot-parity.spec.js` → exit 0 (마지막 명령이 첫 CLI 종료 gate: projectRoot 유형 → 경로 유형 → schema → 현재 identity → 상태 수집(unsafe면 after.z 미접촉 exit 1) → after.z 안전 쓰기 → 판정)
- spec 단독 실행에 다음이 포함되어 통과한다: 모든 합성 저장소 초기 commit에 루트 `.gitignore`(정확히 `tests/.tmp/`) 포함, snapshot·after.z 생성 직후 status에 두 runtime 경로가 없다는 assertion, C·runCheck parity 5사례(사례 (v)는 시작 xy `' M'`·현재 xy `'M '`·시작·현재 SHA-256 동일을 먼저 확인), 기록 대상 FIFO·symlink × 기존 after.z 있음·없음 4가지(`runCheck`와 C 양쪽: exit 1, 기존 after.z bytes·mtime 불변, 신규 after.z 미생성).
