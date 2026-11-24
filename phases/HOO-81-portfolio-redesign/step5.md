# Step 5 — scope-snapshot-symlink (재검증)

- 목적: 비runtime symlink와 snapshot 자체 symlink 거부를 S·`takeCurrent`·C·loader에서 확인한다(테스트만). §11.6 재검증 모드.
- 예상 18분 / 선행 0~4 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.6, §11.7, §12; `tests/helpers/synthetic-repo.js`
- tracked 허용(exact): `tests/specs/scope-snapshot-symlink.spec.js`
- runtime: R0(합성 저장소, 실제 저장소 parity 위치 symlink·사본)
- 금지: §15.7, 도구·helper 수정, 비runtime symlink

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step5`
2. AC 실행 → 통과면 no-op, 실패면 spec만 수정.
3. 계약(각 사례 새 `makeSyntheticRepo()`, 외부 `outside/secret.txt` sentinel, 링크는 실행 전 준비): 실행 경로 — JS `takeCurrent(start, { root: dir, fs: 기록용 })`(기대 unsafe, `files` `{}`, 링크·대상 follow 접근 없음), S `python3 -I <프로젝트>/tests/scripts/start-snapshot.py parity-1`(cwd dir, exit ≠ 0, `unsafe path:` + 기대 항목, snapshot 미생성; 미리 둔 정상 snapshot이 있을 때도 거부·bytes 불변), C(키만 맞춘 start, `python3 -I - parity-1 '<allow>' ''`, exit 1, 기대 `symlink:` 항목, 변경 판정 줄 없음, after.z 미생성, allow에 링크를 넣어도 같음). 사례 (a) `.gitignore`의 `link-ignored` → `<outside>/secret.txt` → `symlink:link-ignored`; (b) commit된 `tracked-link → a.txt`를 `b.txt`, 이어 `c.txt`로 교체(실행 사이) → 매번 `symlink:tracked-link`; (c) `docs-link → <outside>` → `symlink:docs-link`, 내부 항목 없음; (d) 링크 없는 대조 → JS `[]`, C symlink 항목 없음; (e) 실제 저장소 `parity-<A>` 원본·`parity-<k>` 사본·`parity-<m>` → 사본 symlink → S `unsafe path: symlink:tests/.tmp/start-snapshot-parity-<m>.json`, loader `unsafe path: symlink:` throw, 사본 불변, finally 삭제. 출력·산출물에 sentinel 없음.

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-symlink.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step5`
2. 범위 gate: `python3 -I - step5 'tests/specs/scope-snapshot-symlink.spec.js' '' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
