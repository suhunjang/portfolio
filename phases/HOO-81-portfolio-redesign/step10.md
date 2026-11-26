# Step 10 — scope-snapshot-parity-paths (재검증)

- 목적: 경로 계약 위반 (vi)에서 C·runCheck·CLI 모두 외부 접근 없이 exit 1·산출물 불변. §8.6.
- 17분 / 선행 0~9 / 공통 §9 / gate CGATE
- 허용(exact): `tests/specs/scope-snapshot-parity-paths.spec.js`
- runtime: R0(합성)
- 추가 금지: 도구·helper·다른 spec 수정

## 작업
1. `SNAP 10` → AC → no-op / spec만 수정.
2. step 9 준비 + `<outside>/secret.txt`; 정상 snapshot `files`에 key 하나 추가 — A `../<pid>-outside/secret.txt`(null), B `<outside>/secret.txt` 절대(null); after.z 고정 bytes; C(`runHarness`·subprocess `python3 -I - parity-1 '' ''`)·`runCheck`(기록 fs)·CLI(`node <프로젝트>/tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-parity-1.json --allow ''`) 모두 1, 정확히 `bad start snapshot: paths: tests/.tmp/start-snapshot-parity-1.json`, 외부 lstat·open·read 0, C `os.open` snapshot 1회·git은 toplevel만, runCheck의 computeIdentity·takeCurrent·writeAfterZ 미호출; snapshot·after.z·외부 bytes·mtime 불변, sentinel 미출력.

## AC
1. `T scope-snapshot-parity-paths.spec.js && FULL && SNAP 10 && W node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step10.json --allow tests/specs/scope-snapshot-parity-paths.spec.js`
2. `CGATE 10 tests/specs/scope-snapshot-parity-paths.spec.js`
