# Step 4 — scope-snapshot-state (재검증)

- 목적: 현재 status+hash 수집, 합성 저장소 helper, rename, 실제 저장소 S parity. §8.6.
- 19분 / 선행 0~3 / 공통 §9 / gate CGATE
- 허용(exact): `tests/scripts/scope-snapshot.mjs`(step 4 API), `tests/helpers/synthetic-repo.js`, `tests/specs/scope-snapshot-state.spec.js`
- runtime: R0(합성, `<pid>-outside/`)
- 추가 금지: step 1~3 동작, 합성 init/add/commit 외 Git 변경

## 작업
1. `SNAP 4` → AC → no-op / 수정.
2. API `scanProject`, `hashPath`, `takeCurrent(start | null, { git, fs, root })`; `synthetic-repo.js`: `makeSyntheticRepo() → { dir, outside, git(args), cleanup() }`, `designBlock(marker)`, `runPython(args, { cwd, input })`, `runNode(args, { cwd })`(10초), `runHarness(body, { cwd, toplevel, argv, status? })`.
3. spec: `hashPath` sha256·null·dir `non-regular:`·symlink `symlink:`·follow 없음; `scanProject` root symlink → readdir 없음, SKIP 미진입, 엔트리 symlink 보고·정렬; `takeCurrent` start files `../outside.txt` → `bad start snapshot: paths`·fs 0; 합성(`.gitignore`·`tracked.txt`·`tests/specs/a.spec.js` commit 후 수정·ignore·runtime) unsafe `[]`·files 정확; rename(`fs.renameSync`+`add -A`, 두 경로 `R `, a null); `tests/node_modules/.bin/x` 링크 비보고; 실제 `parity-<pid>`와 `takeCurrent(null)` 일치; cleanup.

## AC
1. `T scope-snapshot-state.spec.js scope-snapshot-loader.spec.js && FULL && SNAP 4`
2. `CGATE 4 tests/scripts/scope-snapshot.mjs,tests/helpers/synthetic-repo.js,tests/specs/scope-snapshot-state.spec.js`
