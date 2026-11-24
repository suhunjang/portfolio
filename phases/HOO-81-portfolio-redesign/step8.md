# Step 8 — scope-snapshot-cli (재검증)

- 목적: after.z 안전 쓰기, `runCheck` 실행 순서(unsafe면 after.z 쓰기 전 실패), CLI 연결을 확인한다. 설계 §11.6 재검증 모드. CLI 종료 gate는 step 12부터다.
- 예상 17분 / 선행 0~7 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.6, §11.7(경로 계약, 경로 유형, 실행 전제, 실행 순서, 비교 도구 step 8)
- tracked 허용(exact): `tests/scripts/scope-snapshot.mjs`(step 8 API), `tests/specs/scope-snapshot-cli.spec.js`
- runtime: R0
- 금지: §15.7, step 1~4·7 함수 동작, dirfd/openat·경쟁 주입 테스트

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step8`
2. AC 실행 → 통과면 no-op, 실패면 계약 안에서 수정.
3. 계약: `writeAfterZ`, `runCheck`, CLI `--check`(설계 step 8). spec: `writeAfterZ` 가짜 fs(flags `O_NOFOLLOW`·`O_NONBLOCK`·`O_TRUNC`, leaf symlink·FIFO·디렉터리·조상 symlink → open 없음); `runCheck` 단계별 spy((0)~(2) 실패 시 쓰기 0, (3) unsafe → `writeAfterZ` 0, (4) 실패 → `evaluateGate` 0, (5) 위반/OK); CLI subprocess(정상 OK·after.z regular, 없는 snapshot `missing:`, schemaVersion `1.0`, 인자 누락 exit 2, snapshot sha256 불변).

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-cli.spec.js scope-snapshot-identity.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step8 && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step8.json --allow tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-cli.spec.js` (마지막 CLI는 동작 확인용)
2. 범위 gate: `python3 -I - step8 'tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-cli.spec.js' '' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
