# Step 6 — scope-snapshot-special-files (재검증)

- 목적: FIFO·디렉터리·조상 symlink(`tests/.tmp` 외부 링크 포함)를 S·C·loader가 open/write 전에 거부하고 산출물이 불변임을 확인한다(테스트만). §11.6 재검증 모드.
- 예상 19분 / 선행 0~5 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.6, §11.7, §12; `tests/helpers/synthetic-repo.js`
- tracked 허용(exact): `tests/specs/scope-snapshot-special.spec.js`
- runtime: R0(합성 저장소, 실제 저장소 parity 위치 FIFO·디렉터리)
- 금지: §15.7, 도구·helper 수정, 비runtime symlink·FIFO

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step6`
2. AC 실행 → 통과면 no-op, 실패면 spec만 수정.
3. 계약(timeout 10초, 전후 목록·sha256·mtime·유형 비교): S 합성 (a)~(f), S 실제 저장소 재사용 분기 FIFO·디렉터리, C 합성 (g)~(j), JS loader, `takeCurrent` (c)(d)(e). 모두 멈추지 않고 거부, 산출물 불변.

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-special.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step6`
2. 범위 gate: `python3 -I - step6 'tests/specs/scope-snapshot-special.spec.js' '' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
