# Step 8 — scope-snapshot-cli (재검증)

- 목적: after.z 안전 쓰기, `runCheck` 실행 순서, CLI 연결을 확인한다. §11.6 재검증 모드. CLI 종료 gate는 step 12부터.
- 예상 18분 / 선행 0~7 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.6, §11.7(실행 순서, 비교 도구 step 8의 `runCheck(opts, deps)`·`deps.impl`)
- tracked 허용(exact): `tests/scripts/scope-snapshot.mjs`(step 8 API), `tests/specs/scope-snapshot-cli.spec.js`
- runtime: R0
- 금지: §15.7, step 1~4·7 함수 동작, dirfd/openat·경쟁 주입 테스트

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step8`
2. AC 실행 → 통과면 no-op. 실패하거나 `runCheck`에 `deps.impl` 주입점이 없으면 허용 파일 안에서 설계 계약대로 수정.
3. `writeAfterZ` spec(가짜 fs): 정상 → openSync flags에 `O_NOFOLLOW`·`O_NONBLOCK`·`O_TRUNC`, fstat 확인 후 write; leaf symlink·FIFO·디렉터리, 조상 `tests/.tmp` symlink(호출 전 준비) → `UnsafePathError`, openSync 0.
4. `runCheck` spy spec — `runCheck({ startFile: 'tests/.tmp/start-snapshot-parity-1.json', allow: [], requireAbsent: [] }, { git, fs, root: '/r', impl })`, impl의 7개 함수를 호출 기록 spy로 대체하고 단계마다 하나만 실패시킨다. 기본 spy: `checkRoot` 통과, `loadStartSnapshot` → 정상 start, `computeIdentity` → start identity와 같은 값, `checkIdentity` 실제 함수, `takeCurrent` → `{ entries: [], xy: {}, files: {}, unsafe: [] }`, `writeAfterZ` 통과, `evaluateGate` → `[]`.
   - (0) `checkRoot`가 `UnsafePathError('symlink:/r')` → code 1, stderr 정확히 `unsafe path: symlink:/r`, 이후 6개 함수 호출 0
   - (1) `loadStartSnapshot`이 `Error('bad start snapshot: paths: tests/.tmp/start-snapshot-parity-1.json')` → code 1, stderr 그 메시지, `computeIdentity`·`takeCurrent`·`writeAfterZ`·`evaluateGate` 호출 0
   - (2) `computeIdentity`가 head만 다른 identity 반환 → code 1, stderr `start snapshot identity mismatch: head`, `takeCurrent`·`writeAfterZ`·`evaluateGate` 호출 0
   - (3) `takeCurrent`가 `unsafe: ['non-regular:tests/specs/p.fifo']` 반환 → code 1, stderr 정확히 `non-regular:tests/specs/p.fifo`, `writeAfterZ`·`evaluateGate` 호출 0; 같은 조건에 `requireAbsent: ['x']`이고 start files에 `x`가 있으면 stderr 첫 줄 `snapshot-not-first:x`
   - (4) `writeAfterZ`가 `UnsafePathError('symlink:tests/.tmp/start-snapshot-parity-1-after.z')` → code 1, stderr `unsafe path: symlink:tests/.tmp/start-snapshot-parity-1-after.z`, `evaluateGate` 호출 0
   - (5a) `evaluateGate` → `['outside-tests:README.md']` → `writeAfterZ` 1회 호출 뒤 code 1, stderr 정확히 `outside-tests:README.md`; (5b) `[]` → code 0, stdout `scope-snapshot: OK`
   - 모든 경우 실제 fs 쓰기 호출 0
5. CLI subprocess(실제 저장소, `parity-{숫자}` 생성 후 삭제): 정상 snapshot + `--allow ''` → exit 0·`scope-snapshot: OK`·after.z regular; 없는 snapshot → exit 1·`unsafe path: missing:`; schemaVersion `1.0` 사본 → exit 1·`bad start snapshot: schemaVersion`; 인자 누락 → exit 2·usage; snapshot sha256 불변.

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-cli.spec.js scope-snapshot-identity.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step8 && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step8.json --allow tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-cli.spec.js`
2. 범위 gate: `python3 -I - step8 'tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-cli.spec.js' '' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
