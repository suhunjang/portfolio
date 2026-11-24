# Step 6 — scope-snapshot-special-files (재검증)

- 목적: FIFO·디렉터리·조상 symlink를 S·C·loader·takeCurrent가 open/write 전 거부, 산출물 불변(테스트만). §8.6.
- 19분 / 선행 0~5 / 공통 §9 / gate CGATE
- 허용(exact): `tests/specs/scope-snapshot-special.spec.js`
- runtime: R0(합성 `<pid>/`·`<pid>-outside/`, 실제 `tests/.tmp/start-snapshot-parity-<m>.json`)
- 추가 금지: 도구·helper 수정

## 작업
1. `SNAP 6` → AC → no-op / spec만 수정.
2. 합성 공통 준비: Node fs로 dir `.harness`, `lib`, `tests`, `tests/specs`; file `.harness/harness.lock.json`(`{"sourceCommit": "e7a03919a460f975149f7c55343ca4b34d3d2352", "manifestHash": "b627e6a5ce4a903c24c400927ca2b49a14d0bd59632c691b2a5c2d74c6c08372", "distributionVersion": "2.0.1"}`), `.gitignore`(`tests/.tmp/`), `tracked.txt`, `lib/x.txt`, `tests/specs/a.spec.js` → `add -A`·commit. BASE commit 없음(유형 검사가 먼저 끝나야 함). S 직전 `lstatSync`로 `.harness` dir·lock file·`tests` dir·미변경 조상 dir 확인(아니면 준비 실패). FIFO `python3 -I -c "import os,sys; os.mkfifo(sys.argv[1])" <path>`, subprocess 10초(timeout은 실패), 전후 목록·sha256·mtime·유형 비교, sentinel `secret.txt`.
3. S 합성(cwd dir, `python3 -I <프로젝트>/tests/scripts/start-snapshot.py parity-1`, exit ≠ 0, stderr 정확히): (a) snapshot FIFO → `unsafe path: non-regular:tests/.tmp/start-snapshot-parity-1.json`(FIFO 유지, 새 파일 없음); (b) snapshot 디렉터리(안 `x`) → 같은 메시지(내용 불변); (c) `tests/.tmp` 없음 + `tests/specs/p.fifo` → `unsafe path: non-regular:tests/specs/p.fifo`(`tests/.tmp` 미생성); (d) `tracked.txt` → 디렉터리 → `unsafe path: non-regular:tracked.txt`; (e) `lib → <outside>` → `unsafe path: symlink:lib`; (f) `tests/.tmp → <outside>/tmpdir`(sentinel·snapshot 사본) → `unsafe path: symlink:tests/.tmp`(외부 불변).
4. S 실제(재사용 분기): `parity-<m>`을 FIFO, 이어 디렉터리로 → `unsafe path: non-regular:tests/.tmp/start-snapshot-parity-<m>.json`, 멈추지 않음, 다른 parity 불변, finally 삭제.
5. C 합성(cwd dir, `python3 -I - parity-1 '' ''` + `designBlock('inline 범위 검사 C')`, 정상 start = 키만 맞춤·stepId `parity-1`·files/xy `{}`; exit 1, stderr 정확히): (g) (f) 링크 → `unsafe path: symlink:tests/.tmp`(외부 after.z 미생성); (h) after.z FIFO → `unsafe path: non-regular:tests/.tmp/start-snapshot-parity-1-after.z`; (i) after.z → `<outside>/after-target` symlink → `unsafe path: symlink:tests/.tmp/start-snapshot-parity-1-after.z`(대상 불변); (j) start FIFO → `unsafe path: non-regular:tests/.tmp/start-snapshot-parity-1.json`.
6. loader 합성: (f) → `Error('unsafe path: symlink:tests/.tmp')`, 기록은 root·`tests`·`tests/.tmp` lstat뿐; snapshot FIFO/디렉터리 → `Error('unsafe path: non-regular:tests/.tmp/start-snapshot-parity-1.json')`, openSync 0.
7. `takeCurrent(null, { git: 실제, fs: 기록용, root: dir })`: (c) `non-regular:tests/specs/p.fifo`, (d) `non-regular:tracked.txt`, (e) `symlink:lib`; files `{}`, 해당 openSync 0.

## AC
1. `T scope-snapshot-special.spec.js && FULL && SNAP 6`
2. `CGATE 6 tests/specs/scope-snapshot-special.spec.js`
