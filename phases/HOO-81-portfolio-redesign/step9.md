# Step 9 — scope-snapshot-parity-core

- 목적: 합성 저장소 준비, runtime 비노출 assertion, inline C와 `runCheck`의 정상·변경 parity 사례 (i)~(v)를 실행 검증한다. 코드 추가 없이 신규 spec 하나만. 종료 gate는 아직 S reused + inline C이다(CLI 종료 gate 전환은 step 12).
- 예상 19분(snapshot·단독·전체 테스트·범위 gate·디버깅 포함) / 선행 0~8 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.6, §11.7(규칙, 저장소 상대 경로 계약, projectRoot 유형, 경로 유형 계약, 실행 전제, 실행 순서, C, 비교 도구 step 7·8·9~11, 테스트 격리), §12(합성 저장소 예외); `tests/helpers/synthetic-repo.js`
- tracked 허용(exact): `tests/specs/scope-snapshot-parity-core.spec.js`(신규, 정확히 이 파일 하나)
- runtime: R0(합성 저장소 `tests/.tmp/synthetic-repos/<pid>/`, `<pid>-outside/`)
- 금지: §15.7, `scope-snapshot.mjs`·`start-snapshot.py`·helper·다른 spec 수정, 실제 저장소 비runtime 경로에 symlink·FIFO 생성, 합성 저장소에서 init/add/commit 외 Git 변경, 권한 변경

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step9` (재시도도 같은 명령으로 최초 baseline `reused`)
2. `scope-snapshot-parity-core.spec.js` (node 전용, desktop-dark만, 모든 subprocess timeout 10초, 각 사례 전후 대상 디렉터리의 목록·sha256·mtime 비교, 각 사례 finally에서 `cleanup()`으로 `<pid>`·`<pid>-outside` 삭제)
   - 합성 준비(spec 내부 로컬 함수로 구현, helper의 `makeSyntheticRepo`·`designBlock`만 사용; 각 사례 새 `makeSyntheticRepo()`): 첫 `git add`·commit 전에 Node `fs`로 루트 `.gitignore`를 정확히 `tests/.tmp/` 한 줄(끝 개행 1개)로 작성하고, `.harness/harness.lock.json`(identity 3값 포함), `tracked.txt`, `tests/specs/a.spec.js`와 함께 `add -A`로 초기 commit에 포함한다. `rev-parse --verify BASE^{commit}`만 성공으로 대체하고 나머지는 실제 git으로 전달하는 git 래퍼로 `computeIdentity`·`takeCurrent`를 써서 정상 `tests/.tmp/start-snapshot-parity-1.json`을 만든다(사례 (v)는 아래 별도 준비이며 같은 `.gitignore` 초기 commit을 쓴다)
   - runtime 비노출 assertion: 시작 snapshot 생성 직후, 그리고 C 또는 `runCheck`가 `tests/.tmp/start-snapshot-parity-1-after.z`를 만든 직후마다 `git -C <dir> status --porcelain=v1 -z --untracked-files=all` 출력을 `parseStatusZ`로 파싱해 `tests/.tmp/start-snapshot-parity-1.json`과 `tests/.tmp/start-snapshot-parity-1-after.z`가 path·origPath 어디에도 없음을 assert한다
   - C·`runCheck` parity(같은 합성 상태에서 둘을 각각 실행, C는 cwd `dir` + `designBlock('inline 범위 검사 C')`): (i) 변경 없음 → 둘 다 code 0·`scope-snapshot: OK`; (ii) `tracked.txt` 수정(allow 밖) → 둘 다 code 1·위반 줄 정확히 `outside-tests:tracked.txt`; (iii) 새 `tests/specs/x.spec.js`(allow 밖) → `tests-changed:tests/specs/x.spec.js`; (iv) `--require-absent tracked.txt` → `snapshot-not-first:tracked.txt`; (v) stage만 바뀐 경우 — 준비: 초기 commit 후 `tracked.txt` 내용을 수정하고 stage하지 않은 상태에서 시작 snapshot `tests/.tmp/start-snapshot-parity-1.json`을 만든다 → 파일 내용은 그대로 둔 채 `git -C <dir> add tracked.txt`(helper의 정확한 경로 add)로 stage한다 → assertion 전에 시작 snapshot `xy['tracked.txt']`가 정확히 `' M'`, 현재 `takeCurrent`의 `xy['tracked.txt']`가 정확히 `'M '`, 시작 `files['tracked.txt']`와 현재 `files['tracked.txt']` SHA-256이 같음을 확인 → C와 `runCheck` 모두 code 1·위반 줄 정확히 `status-changed:tracked.txt`. 각 사례에서 두 결과의 exit code와 위반 줄 목록이 같고, 생성된 after.z 내용이 같다

## AC (한 셸에서 순서대로, 모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-parity-core.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step9 && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step9.json --allow tests/specs/scope-snapshot-parity-core.spec.js --require-absent tests/specs/scope-snapshot-parity-core.spec.js` (S는 `reused`, 마지막 CLI 실행은 동작 확인용)
2. 범위 gate: `python3 -I - step9 'tests/specs/scope-snapshot-parity-core.spec.js' 'tests/specs/scope-snapshot-parity-core.spec.js' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
- spec 단독 실행에 모든 합성 저장소 초기 commit의 루트 `.gitignore`(정확히 `tests/.tmp/`), snapshot·after.z 생성 직후 runtime 비노출 assertion, C·`runCheck` parity 사례 (i)~(v)(사례 (v)는 시작 xy `' M'`·현재 xy `'M '`·시작·현재 SHA-256 동일을 먼저 확인)가 포함되어 통과한다.
