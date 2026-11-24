# Step 9 — scope-snapshot-parity-core (재검증)

- 목적: 합성 저장소 준비, runtime 비노출 assertion, inline C와 `runCheck`의 정상·변경 parity 사례 (i)~(v)를 확인한다(spec 하나). 설계 §11.6 재검증 모드.
- 예상 19분 / 선행 0~8 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.6, §11.7(규칙, 경로 계약, projectRoot, 경로 유형, 실행 전제, 실행 순서, C, 비교 도구 step 7·8·9~11, 테스트 격리), §12; `tests/helpers/synthetic-repo.js`
- tracked 허용(exact): `tests/specs/scope-snapshot-parity-core.spec.js`
- runtime: R0(합성 저장소, `<pid>-outside/`)
- 금지: §15.7, 도구·helper·다른 spec 수정, 비runtime symlink·FIFO, 합성 저장소 init/add/commit 외 Git 변경

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step9`
2. AC 실행 → 통과면 no-op, 실패면 spec만 계약대로 수정.
3. 계약: 합성 준비(첫 commit 전 루트 `.gitignore` 정확히 `tests/.tmp/`, `.harness/harness.lock.json`(identity 3값), `tracked.txt`, `tests/specs/a.spec.js` 포함 초기 commit, BASE verify만 대체한 git 래퍼로 정상 `parity-1`); snapshot·after.z 생성 직후마다 status에 두 runtime 경로가 없음을 assert; parity (i) 변경 없음 OK, (ii) `outside-tests:tracked.txt`, (iii) `tests-changed:tests/specs/x.spec.js`, (iv) `snapshot-not-first:tracked.txt`, (v) ` M` 상태 snapshot 후 같은 내용 stage → 시작 xy `' M'`·현재 `'M '`·SHA-256 동일 확인 후 `status-changed:tracked.txt`; 두 결과의 code·위반 줄·after.z 동일.

## AC (한 셸에서 순서대로, 모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-parity-core.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step9 && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step9.json --allow tests/specs/scope-snapshot-parity-core.spec.js`
2. 범위 gate: `python3 -I - step9 'tests/specs/scope-snapshot-parity-core.spec.js' '' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
