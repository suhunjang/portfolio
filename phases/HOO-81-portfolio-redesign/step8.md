# Step 8 — scope-snapshot-cli (재검증)

- 목적: after.z 안전 쓰기, `runCheck` 순서, CLI 연결을 확인한다. §11.6 재검증 모드. CLI 종료 gate는 step 12부터.
- 예상 17분 / 선행 0~7 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.6, §11.7
- tracked 허용(exact): `tests/scripts/scope-snapshot.mjs`(step 8 API), `tests/specs/scope-snapshot-cli.spec.js`
- runtime: R0
- 금지: §15.7, step 1~4·7 함수 동작, dirfd/openat·경쟁 주입 테스트

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step8`
2. AC 실행 → 통과면 no-op, 실패면 계약 안에서 수정.
3. 계약: `writeAfterZ`, `runCheck`, CLI `--check`. spec: `writeAfterZ` flags·거부 시 open 없음; `runCheck` 단계별 spy((0)~(2) 쓰기 0, (3) unsafe → `writeAfterZ` 0, (4) → `evaluateGate` 0, (5)); CLI subprocess(OK, `missing:`, `schemaVersion`, exit 2, snapshot 불변).

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-cli.spec.js scope-snapshot-identity.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step8 && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step8.json --allow tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-cli.spec.js`
2. 범위 gate: `python3 -I - step8 'tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-cli.spec.js' '' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
