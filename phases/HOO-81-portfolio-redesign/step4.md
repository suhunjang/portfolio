# Step 4 — scope-snapshot-state (재검증)

- 목적: 현재 status+hash 수집과 합성 저장소 helper, rename, 실제 저장소 S parity를 확인한다. §11.6 재검증 모드.
- 예상 19분 / 선행 0~3 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.1, §11.4, §11.6, §11.7, §12
- tracked 허용(exact): `tests/scripts/scope-snapshot.mjs`(step 4 API), `tests/helpers/synthetic-repo.js`, `tests/specs/scope-snapshot-state.spec.js`
- runtime: R0(합성 저장소, `<pid>-outside/`)
- 금지: §15.7, step 1~3 함수 동작, 합성 저장소 init/add/commit 외 Git 변경

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step4`
2. AC 실행 → 통과면 no-op, 실패면 계약 안에서 수정.
3. 계약: `scanProject`, `hashPath`, `takeCurrent`; `synthetic-repo.js`(`makeSyntheticRepo`, `designBlock`, `runPython`, `runNode`, `runHarness`). spec: `hashPath` 4유형·링크 follow 없음; `scanProject` root symlink·SKIP·정렬; `takeCurrent` start key 경로 위반 → fs 0; 합성 수집·rename(`R ` 두 경로); runtime 내부 링크 비보고; 실제 저장소 parity 일치; cleanup.

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-state.spec.js scope-snapshot-loader.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step4`
2. 범위 gate: `python3 -I - step4 'tests/scripts/scope-snapshot.mjs,tests/helpers/synthetic-repo.js,tests/specs/scope-snapshot-state.spec.js' '' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
