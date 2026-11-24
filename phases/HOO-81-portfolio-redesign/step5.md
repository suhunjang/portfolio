# Step 5 — scope-snapshot-symlink (재검증)

- 목적: 비runtime symlink·snapshot symlink 거부(S·takeCurrent·C·loader, 테스트만). §8.6.
- 18분 / 선행 0~4 / 공통 §9 / gate CGATE
- 허용(exact): `tests/specs/scope-snapshot-symlink.spec.js`
- runtime: R0(합성, 실제 parity 위치)
- 추가 금지: 도구·helper 수정

## 작업
1. `SNAP 5` → AC → no-op / spec만 수정.
2. 각 사례 새 `makeSyntheticRepo()`, `outside/secret.txt` sentinel, 링크는 실행 전 준비. JS `takeCurrent`(unsafe 기대, files `{}`, follow 없음), S `python3 -I <프로젝트>/tests/scripts/start-snapshot.py parity-1`(exit ≠ 0, stderr `unsafe path:` 시작·기대 항목, 미생성; 기존 정상 snapshot도 거부·bytes 불변), C(`python3 -I - parity-1 '<allow>' ''`, exit 1, `symlink:` 항목, 변경 줄 없음, after.z 미생성, allow에 링크 넣어도 동일).
3. 사례: (a) ignore된 `link-ignored → <outside>/secret.txt` → `symlink:link-ignored`; (b) commit된 `tracked-link → a.txt`를 `b.txt`→`c.txt`로 교체 → 매번 `symlink:tracked-link`; (c) `docs-link → <outside>` → `symlink:docs-link`·내부 항목 없음; (d) 대조 → JS `[]`·C symlink 없음; (e) 실제 `parity-<A>`·사본 `parity-<k>`·`parity-<m>` → 사본 symlink → S `unsafe path: symlink:tests/.tmp/start-snapshot-parity-<m>.json`, loader `unsafe path: symlink:` throw, 사본 불변, finally 삭제. sentinel 미출력.

## AC
1. `T scope-snapshot-symlink.spec.js && FULL && SNAP 5`
2. `CGATE 5 tests/specs/scope-snapshot-symlink.spec.js`
