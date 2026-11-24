# Step 1 — scope-snapshot-paths

- 목적: 비교 도구의 projectRoot·경로 유형 검사와 안전 읽기를 만들고, projectRoot symlink·non-directory 거부가 JS·Python S·C에서 하위 접근 없이 같은 판정임을 실행으로 증명한다.
- 예상 17분 / 선행 0 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.7(projectRoot 유형, 경로 유형 계약, 실행 전제, S, C, 설계 블록 추출 규칙, S·C exec harness, 비교 도구 step 1, 테스트 격리), §12(합성 저장소 예외)
- tracked 허용(exact): `tests/scripts/scope-snapshot.mjs`(신규, step 1 API만), `tests/specs/scope-snapshot-paths.spec.js`(신규)
- runtime: R0(합성 저장소 `tests/.tmp/synthetic-repos/<pid>/`, `<pid>-link`, `<pid>-file` 포함)
- 금지: §15.7, 파서(step 2)·loader(step 3)·상태 수집(step 4)·identity·판정·CLI(step 7·8), S·C 본문 변경, 실제 저장소의 비runtime 경로에 symlink·FIFO 생성, dirfd/openat 기반 구현·검사와 open 사이 경쟁 주입 테스트(설계 §11.7 실행 전제에 따라 동시 경로 교체는 지원 범위 밖)

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step1`
2. `scope-snapshot.mjs`: 설계 §11.7 비교 도구 step 1 API(상수, `UnsafePathError`, `checkRoot`, `pathKind`, `checkPath`, `readRegular`). fs 주입 가능, 파일 쓰기 기능 없음, CLI 없음. 보장 범위는 실행 시점 lstat 조상·leaf 검사, leaf `O_NOFOLLOW`, fd `fstat` regular 확인, unsafe fail-closed까지다.
3. `scope-snapshot-paths.spec.js` (node 전용, desktop-dark만, subprocess timeout 10초)
   - `checkRoot`(가짜 fs): root lstat이 symlink → `symlink:{root}`, regular file → `non-regular:{root}`, 없음 → `missing:{root}`, dir → 통과; 호출 기록이 root에 대한 `lstatSync` 1회뿐
   - `checkPath`(가짜 fs): root 오류는 그대로 전파되고 하위 lstat·open·readdir 없음; 조상 symlink → `symlink:{조상}`, 조상 regular file → `non-regular:{조상}`, 조상 missing + leaf 허용 missing → null, 필수 file이 missing → `missing:`, leaf dir·FIFO·socket·symlink → `non-regular:`/`symlink:`; 호출 기록이 `lstatSync`뿐
   - `readRegular`(가짜 fs): `openSync` flags에 `O_NOFOLLOW`·`O_NONBLOCK` 포함, fstat이 FIFO면 `UnsafePathError('non-regular:…')`이고 read 없음
   - 합성 projectRoot: `tests/.tmp/synthetic-repos/<pid>/`에서 `git -C <dir> init -q`만 실행하고 그 안에 정상 형식 `tests/.tmp/start-snapshot-parity-1.json`을 둔다. 옆에 `<pid>-link → <pid>` symlink와 regular file `<pid>-file`을 만든다(모두 실행 전에 준비, 실행 중 변경 없음)
     - JS: `checkPath('tests/.tmp/start-snapshot-parity-1.json', ['file'], { root: <link>, fs: 기록용 fs })` → `symlink:<link>`, root `<file>` → `non-regular:<file>`, 기록에 root 외 호출 없음
     - S·C: 설계 S·C exec harness로(cwd `<dir>`, `rev-parse --show-toplevel` 결과만 `<link>` 또는 `<file>`로 대체, S 본문은 `tests/scripts/start-snapshot.py`, C 본문은 설계 블록 추출) 실행 → 각각 `unsafe path: symlink:<link>` / `non-regular:<file>`, 기록상 `os.lstat`은 root 경로 1회뿐이고 `os.walk`·`os.open`·`os.makedirs`·`open` 호출과 그 밖 git 호출 0, 합성 디렉터리 목록·bytes·mtime 불변, snapshot·after.z 미생성
     - 끝나면 `<pid>`, `<pid>-link`, `<pid>-file` 삭제
   - 모든 함수가 입력을 바꾸지 않는다

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-paths.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step1` (전체는 `workers: 1` 직렬, 마지막은 `reused`)
2. 범위 gate: `python3 -I - step1 'tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-paths.spec.js' 'tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-paths.spec.js' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
