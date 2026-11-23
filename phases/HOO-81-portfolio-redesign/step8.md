# Step 8 — scope-snapshot-cli

- 목적: after.z 안전 쓰기, `runCheck` 실행 순서(unsafe면 after.z 쓰기 전 즉시 실패), CLI 연결을 만든다. CLI는 이 step에서 완성되므로 종료 gate는 아직 S reused + inline C이고, AC에서 새 CLI를 같은 snapshot에 대해 실행해 동작만 확인한다.
- 예상 17분 / 선행 0~7 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.6, §11.7(경로 유형 계약, 실행 순서, 비교 도구 step 8)
- tracked 허용(exact): `tests/scripts/scope-snapshot.mjs`(추가만), `tests/specs/scope-snapshot-cli.spec.js`(신규)
- runtime: R0
- 금지: §15.7, step 1~4·7 함수 동작, 실제 저장소의 비runtime 경로에 symlink·FIFO 생성

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step8`
2. `scope-snapshot.mjs`에 step 8 API(`writeAfterZ`, `runCheck`, CLI `--check`) 추가. 순서는 설계 §11.7 비교 도구 step 8 그대로.
3. `scope-snapshot-cli.spec.js` (node 전용, desktop-dark만, subprocess timeout 10초)
   - `writeAfterZ`(가짜 fs): 정상 → open flags에 `O_NOFOLLOW`·`O_NONBLOCK`·`O_TRUNC`, fstat 확인 후 쓰기; leaf symlink·FIFO·디렉터리, 조상 `tests/.tmp` symlink → `UnsafePathError`이고 open 없음
   - `runCheck`(가짜 deps, 각 단계 호출을 spy로 기록): (0) root symlink·(1) loader 오류·(2) identity 불일치 각각 → code 1, 해당 stderr, `writeAfterZ`·fs 쓰기 호출 0; (3) `takeCurrent`가 `unsafe` `['non-regular:tests/specs/p.fifo']`를 반환 → code 1, stderr가 정확히 snapshot-not-first(있으면)와 `non-regular:tests/specs/p.fifo`, `writeAfterZ` 호출 0; (4) `writeAfterZ` 실패 → code 1, `evaluateGate` 호출 0; (5) 위반 있음 → after.z 쓴 뒤 code 1, 위반 없음 → code 0·stdout `scope-snapshot: OK`
   - CLI subprocess(실제 저장소, `parity-{숫자}` 사용 후 삭제): 방금 만든 parity snapshot + `--allow ''` → exit 0·`scope-snapshot: OK`, `<parity>-after.z`가 regular file; 없는 snapshot → exit 1·`unsafe path: missing:`; schemaVersion `1.0` 사본 → exit 1·`bad start snapshot: schemaVersion`; 인자 누락 → exit 2·usage; 모든 실행 전후 snapshot sha256 불변

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-cli.spec.js scope-snapshot-identity.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step8 && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step8.json --allow tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-cli.spec.js --require-absent tests/specs/scope-snapshot-cli.spec.js` (마지막 CLI 실행은 동작 확인용, `reused` 뒤)
2. 범위 gate: `python3 -I - step8 'tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-cli.spec.js' 'tests/specs/scope-snapshot-cli.spec.js' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
