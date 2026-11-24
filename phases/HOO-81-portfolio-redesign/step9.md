# Step 9 — scope-snapshot-parity-core (재검증)

- 목적: C·`runCheck` parity (i)~(v). §8.6.
- 19분 / 선행 0~8 / 공통 §9 / gate CGATE
- 허용(exact): `tests/specs/scope-snapshot-parity-core.spec.js`
- runtime: R0(합성)
- 추가 금지: 도구·helper·다른 spec 수정

## 작업
1. `SNAP 9` → AC → no-op / spec만 수정.
2. 첫 commit: 루트 `.gitignore` 정확히 `tests/.tmp/`·`.harness/harness.lock.json`(§ID 3값)·`tracked.txt`·`tests/specs/a.spec.js`. `rev-parse --verify BASE^{commit}`만 성공으로 대체한 git 래퍼로 `computeIdentity`·`takeCurrent` → `tests/.tmp/start-snapshot-parity-1.json`. 생성 직후 status를 `parseStatusZ`로 파싱해 두 runtime 경로 없음. C(cwd dir)와 `runCheck` 각각: (i) 변경 없음 0·`scope-snapshot: OK`; (ii) `tracked.txt` 수정 → 정확히 `outside-tests:tracked.txt`; (iii) 새 `tests/specs/x.spec.js` → `tests-changed:tests/specs/x.spec.js`; (iv) `--require-absent tracked.txt` → `snapshot-not-first:tracked.txt`; (v) 수정·미stage에서 snapshot → 같은 내용 `git -C <dir> add tracked.txt` → 시작 `' M'`·현재 `'M '`·SHA 동일 확인 후 `status-changed:tracked.txt`; 두 결과 code·줄·after.z 동일.

## AC
1. `T scope-snapshot-parity-core.spec.js && FULL && SNAP 9 && W node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step9.json --allow tests/specs/scope-snapshot-parity-core.spec.js`
2. `CGATE 9 tests/specs/scope-snapshot-parity-core.spec.js`
