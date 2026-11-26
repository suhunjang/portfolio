# Step 11 — scope-snapshot-parity-artifacts (재검증)

- 목적: unsafe 시 after.z 보존, CLI 조상 링크·after.z FIFO·identity 변형 거부. §8.6. 이후 CLI gate.
- 19분 / 선행 0~10 / 공통 §9 / gate CGATE
- 허용(exact): `tests/specs/scope-snapshot-parity-artifacts.spec.js`
- runtime: R0(합성, 실제 parity·after.z)
- 추가 금지: 도구·helper·다른 spec 수정

## 작업
1. `SNAP 11` → AC → no-op / spec만 수정.
2. step 9 준비; after.z 있음/없음 × FIFO `tests/specs/p.fifo`/symlink `link-x → <outside>/secret.txt` 4조합에서 `runCheck({ startFile, allow: [그 경로] })`와 C 모두 1·stderr `non-regular:tests/specs/p.fifo` 또는 `symlink:link-x`, after.z open 없음, 있음이면 bytes·mtime 불변, 없음이면 미생성; CLI(cwd dir) `tests/.tmp → <outside>/tmpdir` → `unsafe path: symlink:tests/.tmp`·외부 불변; 실제 after.z FIFO → `non-regular:…-after.z`; identity 7변형(`projectRoot`=`/tmp/other`, `head`=40자 0, `base`=40자 f, `harness.sourceCommit`, `harness.manifestHash`, `harness.distributionVersion`=`9.9.9`, `harness.lockSha256`=64자 0) 각각 `start snapshot identity mismatch: {field}`·after.z 미생성·status·tests 밖 불변.

## AC
1. `T scope-snapshot-parity-artifacts.spec.js && FULL && SNAP 11 && W node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step11.json --allow tests/specs/scope-snapshot-parity-artifacts.spec.js`
2. `CGATE 11 tests/specs/scope-snapshot-parity-artifacts.spec.js`
