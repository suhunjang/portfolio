# Step 6 — scope-snapshot-special-files (재검증)

- 목적: S·C·loader가 snapshot·기록 대상·after.z의 FIFO·디렉터리와 조상 symlink(`tests/.tmp` 외부 링크 포함)를 open/read/write 전에 거부하고 산출물이 불변임을 확인한다(테스트만). 설계 §11.6 재검증 모드.
- 예상 19분 / 선행 0~5 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.6, §11.7(경로 유형, 실행 전제, 실행 순서, S, C, 비교 도구 step 1~4, 블록 추출, 테스트 격리), §12; `tests/helpers/synthetic-repo.js`
- tracked 허용(exact): `tests/specs/scope-snapshot-special.spec.js`
- runtime: R0(합성 저장소, `<pid>-outside/`, 실제 저장소 parity 위치 FIFO·디렉터리)
- 금지: §15.7, 도구·helper 수정, 비runtime symlink·FIFO, 권한 변경

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step6`
2. AC 실행 → 통과면 no-op, 실패면 spec만 계약대로 수정.
3. 계약(timeout 10초, 전후 목록·sha256·mtime·유형 비교, FIFO는 mkfifo): S 합성 (a) snapshot FIFO, (b) snapshot 디렉터리, (c) 기록 대상 FIFO(`tests/.tmp` 미생성), (d) 기록 대상 디렉터리, (e) 조상 `lib` symlink, (f) `tests/.tmp` 외부 링크; S 실제 저장소 재사용 분기 FIFO·디렉터리; C 합성 (g) `tests/.tmp` 외부 링크, (h) after.z FIFO, (i) after.z 외부 symlink, (j) snapshot FIFO; JS loader (f)·FIFO·디렉터리; `takeCurrent` (c)(d)(e). 모두 멈추지 않고 거부, 산출물 불변.

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-special.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step6` (마지막은 `reused`)
2. 범위 gate: `python3 -I - step6 'tests/specs/scope-snapshot-special.spec.js' '' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
