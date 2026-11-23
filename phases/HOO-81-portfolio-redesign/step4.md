# Step 4 — scope-snapshot-special-files

- 목적: 고정 S·C와 JS loader가 snapshot·기록 대상·after.z의 특수 파일(FIFO·디렉터리)과 조상 symlink(`tests/.tmp` 외부 디렉터리 링크 포함)를 open/read/write 전에 거부하고, 실패 시 기존 bytes와 산출물이 바뀌지 않음을 실행 검증한다. 코드 추가 없이 테스트만.
- 예상 19분 / 선행 0~3 / 공통 절차 설계 §15
- read-first: 설계 §11.7(경로 유형 계약, 실행 순서, S, C, 비교 도구 step 1·2, 설계 블록 추출 규칙, 테스트 격리), §12(합성 저장소 예외); `tests/helpers/synthetic-repo.js`
- tracked 허용(exact): `tests/specs/scope-snapshot-special.spec.js`(신규)
- runtime: R0(합성 저장소, `<pid>-outside/`, 실제 저장소 `tests/.tmp/start-snapshot-parity-{숫자}.json` 위치의 FIFO·디렉터리)
- 금지: §15.7, `scope-snapshot.mjs`·`start-snapshot.py`·helper 수정, 실제 저장소 비runtime 경로에 symlink·FIFO 생성, 권한 변경

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step4`
2. `scope-snapshot-special.spec.js` (node 전용, desktop-dark만, 모든 S·C subprocess timeout 10초 — timeout은 실패로 판정, 각 사례 전후로 대상 디렉터리의 파일 목록·각 regular 파일 sha256·mtime·FIFO/디렉터리 유형을 기록해 비교). FIFO는 `os.mkfifo`(python3 -I -c) 또는 `mkfifo`로 만든다.
   - S 합성(cwd `dir`, BASE 없음 → 유형 검사 실패가 BASE 오류보다 먼저 나와야 함)
     - (a) snapshot FIFO: `tests/.tmp/start-snapshot-parity-1.json`이 FIFO → exit ≠ 0, stderr `unsafe path:`에 `non-regular:tests/.tmp/start-snapshot-parity-1.json`, 멈추지 않음, FIFO 유지, 새 파일 없음
     - (b) snapshot 디렉터리: 같은 경로가 디렉터리(안에 파일 1개) → `non-regular:…`, 디렉터리 내용 불변
     - (c) 기록 대상 FIFO: `tests/.tmp`가 없는 상태에서 `tests/specs/p.fifo` FIFO → `non-regular:tests/specs/p.fifo`, `tests/.tmp` 미생성, 다른 파일 sha256 불변
     - (d) 기록 대상 디렉터리: commit된 `tracked.txt`를 지우고 같은 이름 디렉터리(안에 `x`) 생성 → `non-regular:tracked.txt`, `tests/.tmp` 미생성
     - (e) 조상 symlink: commit된 `lib/x.txt`가 있는 `lib`를 `<outside>`(안에 sentinel `x.txt`) 링크로 교체 → `symlink:lib`, sentinel 미출력
     - (f) `tests/.tmp` 외부 디렉터리 symlink: `tests/.tmp → <outside>/tmpdir`(안에 sentinel 파일과 정상 형식 snapshot 사본) → `symlink:tests/.tmp`, 외부 디렉터리 목록·bytes·mtime 불변
   - S 실제 저장소(재사용 분기, 실제 BASE): `tests/.tmp/start-snapshot-parity-<m>.json`이 FIFO, 디렉터리인 경우 각각 exit ≠ 0·`non-regular:`·멈추지 않음, 다른 parity 파일 sha256 불변. 끝나면 삭제
   - C 합성(cwd `dir`, `designBlock('inline 범위 검사 C')`): (g) (f)와 같은 `tests/.tmp` 외부 링크 → exit 1, stderr `unsafe path: symlink:tests/.tmp`, `<outside>/tmpdir`에 `-after.z` 미생성, 외부 bytes·mtime 불변; (h) 정상 start 파일 + `…-after.z`가 FIFO → exit 1, `non-regular:…-after.z`, FIFO 유지, 멈추지 않음; (i) after.z가 외부 파일 symlink → `symlink:…-after.z`, 외부 파일 bytes 불변; (j) snapshot 자체가 FIFO → `non-regular:`, 멈추지 않음
   - JS loader 합성: (f) 상태에서 `loadStartSnapshot('tests/.tmp/start-snapshot-parity-1.json', { root: dir, fs: 기록용 fs })` → `unsafe path: symlink:tests/.tmp` throw, 기록은 root·`tests`·`tests/.tmp`에 대한 `lstatSync`뿐(외부 대상에 대한 open·read·stat·readlink·realpath 없음); snapshot FIFO·디렉터리 → `non-regular:` throw, open 없음
   - JS `takeCurrent` 합성: (c)·(d)·(e) 각각 `unsafe`에 같은 항목, `files` `{}`, 해당 경로 open 없음
   - 기록 대상 unsafe 시 after.z 보존은 step 5가 C·CLI 양쪽에서 검증한다

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-special.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step4` (마지막은 `reused`)
2. 범위 gate: `python3 -I - step4 'tests/specs/scope-snapshot-special.spec.js' 'tests/specs/scope-snapshot-special.spec.js' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
