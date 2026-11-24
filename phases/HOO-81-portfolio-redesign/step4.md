# Step 4 — scope-snapshot-state (재검증)

- 목적: projectRoot·경로 유형 검사를 포함한 현재 status+hash 수집과 합성 저장소 helper, 합성 수집·rename, 실제 저장소 S parity를 확인한다. 설계 §11.6 재검증 모드.
- 예상 19분 / 선행 0~3 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.1, §11.4, §11.6, §11.7(규칙, 경로 계약, 경로 유형, 실행 전제, S, 비교 도구 step 4, 블록 추출, exec harness, 테스트 격리), §12
- tracked 허용(exact): `tests/scripts/scope-snapshot.mjs`(step 4 API), `tests/helpers/synthetic-repo.js`, `tests/specs/scope-snapshot-state.spec.js`
- runtime: R0(합성 저장소, `<pid>-outside/`)
- 금지: §15.7, step 1~3 함수 동작, 합성 저장소 init/add/commit 외 Git 변경, 권한 변경

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step4`
2. AC 실행 → 통과면 no-op, 실패면 계약 안에서 수정.
3. 계약: `scanProject`, `hashPath`, `takeCurrent`(설계 step 4). `synthetic-repo.js`: `makeSyntheticRepo()` → `{ dir, outside, git(args), cleanup() }`(init/add/commit만), `designBlock(marker)`, `runPython`, `runNode`(timeout 10초), `runHarness(body, { cwd, toplevel, argv })`. spec: `hashPath` 가짜 fs(file·missing·dir·symlink, 링크 follow 접근 없음); `scanProject`(root symlink, SKIP 미진입·엔트리 symlink 보고, 정렬); `takeCurrent` start key `../outside.txt` → `bad start snapshot: paths`, fs 0; 합성 수집(ignore·runtime 포함)과 rename(`fs.renameSync` + `add -A`, `R ` 두 경로); runtime 내부 링크 비보고; 실제 저장소 `parity-<pid>` S 결과와 `takeCurrent(null)` 일치; cleanup.

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-state.spec.js scope-snapshot-loader.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step4` (마지막은 `reused`)
2. 범위 gate: `python3 -I - step4 'tests/scripts/scope-snapshot.mjs,tests/helpers/synthetic-repo.js,tests/specs/scope-snapshot-state.spec.js' '' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
