# Step 10 — scope-snapshot-parity-paths

- 목적: 저장소 상대 경로 계약 위반 parity 사례 (vi)(상대 경로 탈출·절대 경로)에서 inline C와 `runCheck`·CLI가 모두 외부 파일 open 없이 exit 1이고 기존 snapshot·after.z가 불변임을 실행 검증한다. 코드 추가 없이 신규 spec 하나만. 종료 gate는 S reused + inline C.
- 예상 17분(snapshot·단독·전체 테스트·범위 gate·디버깅 포함) / 선행 0~9 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.7(저장소 상대 경로 계약, 실행 순서, C, S·C exec harness, 비교 도구 step 3·8·9~11, 테스트 격리), §12(합성 저장소 예외); `tests/helpers/synthetic-repo.js`, `tests/specs/scope-snapshot-parity-core.spec.js`(읽기만, 준비 절차 참고)
- tracked 허용(exact): `tests/specs/scope-snapshot-parity-paths.spec.js`(신규, 정확히 이 파일 하나)
- runtime: R0(합성 저장소 `tests/.tmp/synthetic-repos/<pid>/`, `<pid>-outside/`)
- 금지: §15.7, `scope-snapshot.mjs`·`start-snapshot.py`·helper·다른 spec 수정, 실제 저장소 비runtime 경로에 symlink·FIFO 생성, 합성 저장소에서 init/add/commit 외 Git 변경, 권한 변경

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step10` (재시도도 같은 명령으로 `reused`)
2. `scope-snapshot-parity-paths.spec.js` (node 전용, desktop-dark만, 모든 subprocess timeout 10초, 각 변형 finally에서 `cleanup()`)
   - 합성 준비(spec 내부 로컬 함수, step 9와 같은 절차): 새 `makeSyntheticRepo()`, 첫 add·commit 전 루트 `.gitignore` 정확히 `tests/.tmp/` 한 줄, `.harness/harness.lock.json`(identity 3값)·`tracked.txt`·`tests/specs/a.spec.js`와 함께 `add -A`·초기 commit, BASE verify만 대체한 git 래퍼로 정상 `tests/.tmp/start-snapshot-parity-1.json` 생성, 생성 직후 runtime 비노출 assertion(status에 snapshot·after.z 경로 없음). 외부 `<outside>/secret.txt`에 고유 sentinel 작성
   - (vi) 저장소 상대 경로 계약 위반(정상 identity 유지): 정상 snapshot의 JSON을 읽어 projectRoot·head·base·harness·stepId는 그대로 두고 `files`에 key 하나만 추가해 다시 쓴다 — 변형 A key `../<pid>-outside/secret.txt`(`dir` 기준 외부 sentinel 파일, 값 null), 변형 B key `<outside>/secret.txt`의 절대 경로(Node `path.resolve`, 값 null). 이어 `…-after.z`에 고정 bytes를 쓰고 snapshot·after.z·외부 `secret.txt`의 sha256·mtime을 기록한다. 각 변형에서
     - C: `runHarness(designBlock('inline 범위 검사 C'), { cwd: dir, toplevel: dir, argv: ['parity-1', '', ''] })` → `SystemExit` 메시지가 정확히 `bad start snapshot: paths: tests/.tmp/start-snapshot-parity-1.json`, 기록된 `os.lstat`·`os.open`·`builtins.open`·`os.walk` 대상에 외부 경로(`secret.txt`, `<pid>-outside`)가 없고 `os.open`은 snapshot 1회뿐, `rev-parse --show-toplevel` 외 git 호출 0; 같은 C 본문을 cwd `dir` subprocess(`python3 -I - parity-1 '' ''`)로도 실행 → exit 1, 같은 stderr
     - CLI: `runCheck({ startFile: 'tests/.tmp/start-snapshot-parity-1.json', allow: [] }, { git: 래퍼, fs: 기록용 fs, root: dir })` → code 1, stderr 정확히 `bad start snapshot: paths: tests/.tmp/start-snapshot-parity-1.json`, 기록에 외부 경로 lstat·stat·open·read·readlink·realpath 0, `computeIdentity`·`takeCurrent`·`writeAfterZ` 미호출; CLI subprocess(cwd `dir`, `node <프로젝트>/tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-parity-1.json --allow ''`) → exit 1, 같은 stderr
     - 모든 실행 뒤 snapshot·after.z bytes·mtime 불변, 외부 `secret.txt` bytes·mtime 불변, stdout·stderr에 sentinel 없음, C와 CLI의 exit code·메시지 동일

## AC (한 셸에서 순서대로, 모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-parity-paths.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step10 && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step10.json --allow tests/specs/scope-snapshot-parity-paths.spec.js --require-absent tests/specs/scope-snapshot-parity-paths.spec.js` (S는 `reused`, 마지막 CLI 실행은 동작 확인용)
2. 범위 gate: `python3 -I - step10 'tests/specs/scope-snapshot-parity-paths.spec.js' 'tests/specs/scope-snapshot-parity-paths.spec.js' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
- spec 단독 실행에 사례 (vi)의 `../` 상대·절대 경로 key 두 변형에서 C와 CLI 모두 외부 파일 접근 없이 exit 1·`bad start snapshot: paths:`, 기존 snapshot·after.z·외부 파일 bytes·mtime 불변이 포함되어 통과한다.
