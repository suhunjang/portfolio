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
3. 계약: JS·S(생성·재사용)·C 세 경로에서 (a) ignored symlink, (b) 수정된 tracked symlink target 변경(실행 사이 교체), (c) symlink 디렉터리 미진입, (d) 대조, (e) snapshot 자체 symlink(`parity-<A>` 원본·`parity-<k>` 사본·`parity-<m>` 링크, 사본 불변, finally 삭제). sentinel 미출력, 링크는 실행 전 준비.

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-symlink.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step5`
2. 범위 gate: `python3 -I - step5 'tests/specs/scope-snapshot-symlink.spec.js' '' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
