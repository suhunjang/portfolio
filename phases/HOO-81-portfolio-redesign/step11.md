# Step 11 — scope-snapshot-parity-artifacts

- 목적: 기록 대상 unsafe 시 after.z 보존 4조합(C·`runCheck`), CLI의 `tests/.tmp` runtime 조상 링크 거부, 실제 저장소 after.z FIFO·identity 변형 거부를 실행 검증한다. 코드 추가 없이 신규 spec 하나만. 이 step까지 종료 gate는 S reused + inline C이며, 통과 뒤 step 12부터 CLI가 종료 gate가 된다.
- 예상 19분(snapshot·단독·전체 테스트·범위 gate·디버깅 포함) / 선행 0~10 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.6, §11.7(규칙, projectRoot 유형, 경로 유형 계약, 실행 순서, C, 비교 도구 step 7·8·9~11, 테스트 격리), §12(합성 저장소 예외); `tests/helpers/synthetic-repo.js`, `tests/specs/scope-snapshot-parity-core.spec.js`(읽기만, 준비 절차 참고)
- tracked 허용(exact): `tests/specs/scope-snapshot-parity-artifacts.spec.js`(신규, 정확히 이 파일 하나)
- runtime: R0(합성 저장소, `<pid>-outside/`, 실제 저장소 `tests/.tmp/start-snapshot-parity-{숫자}.json`과 그 after.z)
- 금지: §15.7, `scope-snapshot.mjs`·`start-snapshot.py`·helper·다른 spec 수정, 실제 저장소 비runtime 경로에 symlink·FIFO 생성, 합성 저장소에서 init/add/commit 외 Git 변경, 권한 변경

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step11` (재시도도 같은 명령으로 `reused`)
2. `scope-snapshot-parity-artifacts.spec.js` (node 전용, desktop-dark만, 모든 subprocess timeout 10초, 각 사례 전후 대상 디렉터리의 목록·sha256·mtime 비교, 합성 사례 finally `cleanup()`, 실제 저장소 parity 파일은 finally 삭제)
   - 합성 준비(spec 내부 로컬 함수, step 9와 같은 절차): 새 `makeSyntheticRepo()`, 첫 add·commit 전 루트 `.gitignore` 정확히 `tests/.tmp/` 한 줄, `.harness/harness.lock.json`(identity 3값)·`tracked.txt`·`tests/specs/a.spec.js`와 함께 `add -A`·초기 commit, BASE verify만 대체한 git 래퍼로 정상 `tests/.tmp/start-snapshot-parity-1.json` 생성, 생성 직후 runtime 비노출 assertion. 외부 `<outside>/secret.txt`에 고유 sentinel
   - 기록 대상 unsafe 시 after.z 보존(4가지 = 기존 after.z 있음/없음 × 기록 대상 FIFO `tests/specs/p.fifo`/symlink `link-x → <outside>/secret.txt`): "있음"이면 `…-after.z`에 고정 bytes를 쓰고 mtime을 기록한 뒤 FIFO 또는 symlink를 추가한다
     - `runCheck({ startFile, allow: [그 경로] }, { git: 래퍼, fs: 기록용 fs, root: dir })` → code 1, stderr에 `non-regular:tests/specs/p.fifo` 또는 `symlink:link-x`, 기록에 after.z 경로 open 없음; "있음"이면 after.z bytes·mtime 불변, "없음"이면 after.z 미생성; snapshot sha256 불변
     - 같은 4가지를 C로 실행 → exit 1, 같은 stderr 항목, after.z bytes·mtime 불변 또는 미생성, 멈추지 않음
   - CLI runtime 조상 링크(cwd `dir`, `node <프로젝트>/tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-parity-1.json --allow ''`): `tests/.tmp`를 `<outside>/tmpdir`(정상 snapshot 사본과 sentinel 포함) 링크로 교체 → exit 1, stderr `unsafe path: symlink:tests/.tmp`, 외부 디렉터리에 after.z 미생성·bytes·mtime 불변, sentinel 미출력
   - CLI 실제 저장소(`parity-{숫자}` 사용 후 삭제)
     - `<parity>-after.z`를 FIFO로 미리 만든 경우 → exit 1, `non-regular:…-after.z`, 멈추지 않음, FIFO 유지
     - identity 거부(schema 정상): `projectRoot`=`/tmp/other`, `head`=40자 0, `base`=40자 f, `harness.sourceCommit`, `harness.manifestHash`, `harness.distributionVersion`=`9.9.9`, `harness.lockSha256`=64자 0 중 하나씩만 바꾼 별도 `parity-<n>` → 각각 exit 1, stderr `start snapshot identity mismatch: {field}`, snapshot sha256 불변, `<snapshot>-after.z` 미생성, 실행 전후 `git status --porcelain=v1 -z --untracked-files=all` 출력과 `git ls-files`의 tests 밖 파일 sha256 불변
     - 모든 실행 전후 snapshot sha256 불변

## AC (한 셸에서 순서대로, 모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-parity-artifacts.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step11 && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step11.json --allow tests/specs/scope-snapshot-parity-artifacts.spec.js --require-absent tests/specs/scope-snapshot-parity-artifacts.spec.js` (S는 `reused`, 마지막 CLI 실행은 동작 확인용)
2. 범위 gate: `python3 -I - step11 'tests/specs/scope-snapshot-parity-artifacts.spec.js' 'tests/specs/scope-snapshot-parity-artifacts.spec.js' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
- spec 단독 실행에 기록 대상 FIFO·symlink × 기존 after.z 있음·없음 4가지(`runCheck`와 C 양쪽: exit 1, 기존 after.z bytes·mtime 불변, 신규 after.z 미생성), CLI `tests/.tmp` 외부 링크 거부, 실제 저장소 after.z FIFO 거부와 identity 7개 변형 거부가 포함되어 통과한다.
