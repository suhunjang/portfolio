# Step 6 — scope-snapshot-special-files (재검증)

- 목적: FIFO·디렉터리·조상 symlink(`tests/.tmp` 외부 링크 포함)를 S·C·loader·`takeCurrent`가 open/write 전에 거부하고 산출물이 불변임을 확인한다(테스트만). §11.6 재검증 모드.
- 예상 19분 / 선행 0~5 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.6, §11.7(S 실행 순서·경로 유형 검사 대상: 기록 대상·lock·`tests/.tmp`·snapshot), §12; `tests/helpers/synthetic-repo.js`
- tracked 허용(exact): `tests/specs/scope-snapshot-special.spec.js`
- runtime: R0(합성 저장소 `tests/.tmp/synthetic-repos/<pid>/`·`<pid>-outside/`, 실제 저장소 `tests/.tmp/start-snapshot-parity-<m>.json` 위치)
- 금지: §15.7, 도구·helper 수정, 비runtime symlink·FIFO

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step6`
2. AC 실행 → 통과면 no-op, 실패면 spec만 아래 계약대로 수정.
3. 합성 저장소 공통 준비(각 사례 새 `makeSyntheticRepo()`):
   - Node `fs`로 regular 디렉터리 `.harness`, `lib`, `tests`, `tests/specs`를 만들고 regular file `.harness/harness.lock.json`(내용: `{"sourceCommit": "e7a03919a460f975149f7c55343ca4b34d3d2352", "manifestHash": "b627e6a5ce4a903c24c400927ca2b49a14d0bd59632c691b2a5c2d74c6c08372", "distributionVersion": "2.0.1"}`), `.gitignore`(`tests/.tmp/` 한 줄), `tracked.txt`, `lib/x.txt`, `tests/specs/a.spec.js`를 쓴 뒤 `add -A`·초기 commit
   - 합성 저장소에는 BASE commit이 없다(유형 검사가 BASE 확인보다 먼저라 각 사례가 의도한 유형 검사 한 줄에서 끝나야 함)
   - 사례별 거부 상태를 만든 뒤 S 호출 직전에 Node `lstatSync`로 확인: `.harness`가 dir, `.harness/harness.lock.json`이 file, `tests`가 dir, 사례가 바꾸지 않는 조상(`lib`, `tests/specs`)이 dir. 아니면 테스트 준비 실패로 중단
   - FIFO는 `python3 -I -c "import os,sys; os.mkfifo(sys.argv[1])" <path>`, 모든 subprocess timeout 10초(timeout은 실패), 실행 전후 대상 디렉터리의 목록·regular sha256·mtime·유형 비교, `<outside>`에는 sentinel `secret.txt`, 거부 상태는 실행 중 바꾸지 않음
4. S 합성 — cwd `dir`, 명령 `python3 -I <프로젝트>/tests/scripts/start-snapshot.py parity-1`. 각 사례 exit ≠ 0, stderr가 정확히 아래 한 줄:
   - (a) `tests/.tmp/start-snapshot-parity-1.json`이 FIFO → `unsafe path: non-regular:tests/.tmp/start-snapshot-parity-1.json`; FIFO 유지, `tests/.tmp`에 새 파일 없음
   - (b) 같은 경로가 디렉터리(안에 파일 `x`) → `unsafe path: non-regular:tests/.tmp/start-snapshot-parity-1.json`; 디렉터리 내용 불변
   - (c) `tests/.tmp` 없음 + untracked `tests/specs/p.fifo` FIFO → `unsafe path: non-regular:tests/specs/p.fifo`; `tests/.tmp` 미생성, 다른 파일 sha256 불변
   - (d) commit된 `tracked.txt`를 지우고 같은 이름 디렉터리(안에 `x`) 생성 → `unsafe path: non-regular:tracked.txt`; `tests/.tmp` 미생성
   - (e) commit된 `lib` 디렉터리를 지우고 `lib → <outside>` symlink로 교체 → `unsafe path: symlink:lib`; sentinel 미출력
   - (f) `tests/.tmp → <outside>/tmpdir` symlink(`tmpdir`에 sentinel과 정상 형식 snapshot 사본) → `unsafe path: symlink:tests/.tmp`; `<outside>/tmpdir` 목록·bytes·mtime 불변
5. S 실제 저장소(재사용 분기, 실제 BASE·lock) — `tests/.tmp/start-snapshot-parity-<m>.json`을 FIFO로, 이어 디렉터리로 만들고 각각 `python3 -I tests/scripts/start-snapshot.py parity-<m>` → exit ≠ 0, stderr `unsafe path: non-regular:tests/.tmp/start-snapshot-parity-<m>.json`, 멈추지 않음, 다른 parity 파일 sha256 불변; finally 삭제.
6. C 합성 — cwd `dir`, 명령 `python3 -I - parity-1 '' ''` + `designBlock('inline 범위 검사 C')`. 정상 start = 키 집합만 맞춘 `tests/.tmp/start-snapshot-parity-1.json`(stepId `parity-1`, files `{}`, xy `{}`). 각 사례 exit 1, stderr 정확히:
   - (g) (f)와 같은 `tests/.tmp` 외부 링크 → `unsafe path: symlink:tests/.tmp`; `<outside>/tmpdir`에 `-after.z` 미생성, 외부 bytes·mtime 불변
   - (h) 정상 start + `tests/.tmp/start-snapshot-parity-1-after.z` FIFO → `unsafe path: non-regular:tests/.tmp/start-snapshot-parity-1-after.z`; FIFO 유지
   - (i) 정상 start + after.z가 `<outside>/after-target`(sentinel) symlink → `unsafe path: symlink:tests/.tmp/start-snapshot-parity-1-after.z`; 대상 bytes 불변
   - (j) start 파일 자체가 FIFO → `unsafe path: non-regular:tests/.tmp/start-snapshot-parity-1.json`; 멈추지 않음
7. JS loader 합성 — `loadStartSnapshot('tests/.tmp/start-snapshot-parity-1.json', { root: dir, fs: 기록용 fs })`: (f) 상태 → `Error('unsafe path: symlink:tests/.tmp')`, 기록은 root·`tests`·`tests/.tmp`의 `lstatSync`뿐(외부 대상 open·read·stat·readlink·realpath 0); snapshot FIFO 또는 디렉터리 → `Error('unsafe path: non-regular:tests/.tmp/start-snapshot-parity-1.json')`, `openSync` 0.
8. JS `takeCurrent` 합성 — `takeCurrent(null, { git: 실제 git 래퍼, fs: 기록용 fs, root: dir })`: (c) 상태 → `unsafe`에 `non-regular:tests/specs/p.fifo`; (d) → `non-regular:tracked.txt`; (e) → `symlink:lib`; 세 경우 모두 `files` `{}`, 해당 경로 `openSync` 0.

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-special.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step6`
2. 범위 gate: `python3 -I - step6 'tests/specs/scope-snapshot-special.spec.js' '' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
