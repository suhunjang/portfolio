# Step 1 — scope-snapshot-paths (재검증)

- 목적: projectRoot·경로 유형·안전 읽기 판정이 JS·S·C에서 같음을 확인. §8.6.
- 17분 / 선행 0 / 공통 §9 / gate CGATE
- 허용(exact): `tests/scripts/scope-snapshot.mjs`(step 1 API), `tests/specs/scope-snapshot-paths.spec.js`
- runtime: R0(합성 `<pid>`, `<pid>-link`, `<pid>-file`)
- 추가 금지: 이후 step API, `HARNESS_IDENTITY` 값

## 작업
1. `SNAP 1` → AC → 통과 no-op / 실패 시 계약 안에서 수정.
2. spec(node, desktop-dark, 10초): `checkRoot` 가짜 fs(symlink → `symlink:{root}`, file → `non-regular:{root}`, 없음 → `missing:{root}`, dir 통과, lstat 1회); `checkPath`(root 오류 전파·하위 접근 0, 조상 symlink `symlink:{조상}`, 조상 file `non-regular:{조상}`, 조상 missing+허용 missing → null, 필수 file missing → `missing:`, leaf dir·FIFO·socket `non-regular:`, leaf symlink `symlink:`, `lstatSync`만); `readRegular`(flags `O_NOFOLLOW`·`O_NONBLOCK`, fstat FIFO → `UnsafePathError('non-regular:…')`, read 없음); 합성 root(`init -q`, 정상 `tests/.tmp/start-snapshot-parity-1.json`, `<pid>-link → <pid>`, file `<pid>-file`): JS `checkPath('tests/.tmp/start-snapshot-parity-1.json', ['file'], { root: <link> })` → `symlink:<link>`, root `<file>` → `non-regular:<file>`; S·C exec harness → `unsafe path: symlink:<link>`/`non-regular:<file>`, root lstat 1회 외 walk·open·makedirs·open·git 0, 산출물 없음; 입력 불변; 정리.

## AC
1. `T scope-snapshot-paths.spec.js && FULL && SNAP 1`
2. `CGATE 1 tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-paths.spec.js`
