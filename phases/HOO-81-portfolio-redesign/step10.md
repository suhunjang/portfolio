# Step 10 — scope-snapshot-parity-paths (재검증)

- 목적: 경로 계약 위반 (vi)에서 C·`runCheck`·CLI 모두 외부 접근 없이 exit 1·산출물 불변임을 확인한다. §11.6 재검증 모드.
- 예상 17분 / 선행 0~9 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.6, §11.7, §12; `tests/helpers/synthetic-repo.js`, `tests/specs/scope-snapshot-parity-core.spec.js`(읽기만)
- tracked 허용(exact): `tests/specs/scope-snapshot-parity-paths.spec.js`
- runtime: R0(합성 저장소)
- 금지: §15.7, 도구·helper·다른 spec 수정

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step10`
2. AC 실행 → 통과면 no-op, 실패면 spec만 수정.
3. 계약: step 9 준비 + 외부 sentinel; 정상 identity 유지한 채 `files`에 `../<pid>-outside/secret.txt` 또는 외부 절대 경로 key; C(harness·subprocess)·`runCheck`·CLI 모두 정확히 `bad start snapshot: paths: tests/.tmp/start-snapshot-parity-1.json`, 외부 접근 0, identity·수집·after.z 미호출, 파일 bytes·mtime 불변.

## AC (한 셸에서 순서대로, 모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-parity-paths.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step10 && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step10.json --allow tests/specs/scope-snapshot-parity-paths.spec.js`
2. 범위 gate: `python3 -I - step10 'tests/specs/scope-snapshot-parity-paths.spec.js' '' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
