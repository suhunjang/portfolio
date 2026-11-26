# Step 8 — scope-snapshot-cli (재검증)

- 목적: after.z 안전 쓰기, `runCheck` 순서, CLI. §8.6.
- 18분 / 선행 0~7 / 공통 §9 / gate CGATE
- 허용(exact): `tests/scripts/scope-snapshot.mjs`(step 8 API), `tests/specs/scope-snapshot-cli.spec.js`
- runtime: R0
- 추가 금지: step 1~4·7 동작

## 작업
1. `SNAP 8` → AC → no-op / `deps.impl` 없거나 실패 시 수정.
2. `writeAfterZ`(가짜 fs): flags `O_NOFOLLOW`·`O_NONBLOCK`·`O_TRUNC`, fstat 후 write; leaf symlink·FIFO·dir·조상 `tests/.tmp` symlink → `UnsafePathError`, openSync 0.
3. `runCheck({ startFile: 'tests/.tmp/start-snapshot-parity-1.json', allow: [], requireAbsent: [] }, { git, fs, root: '/r', impl })`, 7개 spy(기본: checkRoot 통과, load 정상, computeIdentity 같은 값, checkIdentity 실제, takeCurrent `{ entries: [], xy: {}, files: {}, unsafe: [] }`, writeAfterZ 통과, evaluateGate `[]`):
   - (0) checkRoot `UnsafePathError('symlink:/r')` → code 1, stderr 정확히 `unsafe path: symlink:/r`, 이후 6개 0회
   - (1) load `Error('bad start snapshot: paths: tests/.tmp/start-snapshot-parity-1.json')` → code 1·그 메시지, computeIdentity·takeCurrent·writeAfterZ·evaluateGate 0회
   - (2) head만 다른 identity → `start snapshot identity mismatch: head`, takeCurrent·writeAfterZ·evaluateGate 0회
   - (3) unsafe `['non-regular:tests/specs/p.fifo']` → stderr 정확히 그 줄, writeAfterZ·evaluateGate 0회; `requireAbsent: ['x']`+start files `x`면 첫 줄 `snapshot-not-first:x`
   - (4) writeAfterZ `UnsafePathError('symlink:tests/.tmp/start-snapshot-parity-1-after.z')` → `unsafe path: symlink:tests/.tmp/start-snapshot-parity-1-after.z`, evaluateGate 0회
   - (5a) gate `['outside-tests:README.md']` → writeAfterZ 1회 뒤 code 1·정확히 그 줄; (5b) `[]` → code 0·`scope-snapshot: OK`; 실제 fs 쓰기 0
4. CLI(실제, parity 생성 후 삭제): 정상 + `--allow ''` → 0·OK·after.z regular; 없음 → 1·`unsafe path: missing:`; schemaVersion `1.0` → 1·`bad start snapshot: schemaVersion`; 인자 누락 → 2·usage; sha256 불변.

## AC
1. `T scope-snapshot-cli.spec.js scope-snapshot-identity.spec.js && FULL && SNAP 8 && W node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step8.json --allow tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-cli.spec.js`
2. `CGATE 8 tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-cli.spec.js`
