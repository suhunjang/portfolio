# Step 9 — scope-snapshot-parity-core (재검증)

- 목적: 합성 저장소 준비, runtime 비노출 assertion, C·`runCheck` parity (i)~(v)를 확인한다. §11.6 재검증 모드.
- 예상 19분 / 선행 0~8 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.6, §11.7, §12; `tests/helpers/synthetic-repo.js`
- tracked 허용(exact): `tests/specs/scope-snapshot-parity-core.spec.js`
- runtime: R0(합성 저장소)
- 금지: §15.7, 도구·helper·다른 spec 수정, 합성 저장소 init/add/commit 외 Git 변경

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step9`
2. AC 실행 → 통과면 no-op, 실패면 spec만 수정.
3. 계약: 첫 commit에 루트 `.gitignore` 정확히 `tests/.tmp/`·lock(identity 3값)·`tracked.txt`·`tests/specs/a.spec.js`; BASE verify만 대체한 git 래퍼로 `parity-1`; snapshot·after.z 생성 직후 runtime 경로 status 비노출; (i) OK, (ii) `outside-tests:tracked.txt`, (iii) `tests-changed:tests/specs/x.spec.js`, (iv) `snapshot-not-first:tracked.txt`, (v) ` M` snapshot 후 같은 내용 stage → `' M'`·`'M '`·SHA 동일 확인 후 `status-changed:tracked.txt`; 결과·after.z 동일.

## AC (한 셸에서 순서대로, 모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-parity-core.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step9 && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step9.json --allow tests/specs/scope-snapshot-parity-core.spec.js`
2. 범위 gate: `python3 -I - step9 'tests/specs/scope-snapshot-parity-core.spec.js' '' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
