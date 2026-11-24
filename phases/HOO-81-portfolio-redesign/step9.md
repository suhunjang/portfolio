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
3. 계약: 첫 commit에 루트 `.gitignore` 정확히 `tests/.tmp/`·`.harness/harness.lock.json`(identity 3값)·`tracked.txt`·`tests/specs/a.spec.js`; `rev-parse --verify BASE^{commit}`만 성공으로 대체한 git 래퍼로 `computeIdentity`·`takeCurrent`를 써서 `tests/.tmp/start-snapshot-parity-1.json` 생성; snapshot·after.z 생성 직후 `git -C <dir> status --porcelain=v1 -z --untracked-files=all`을 `parseStatusZ`로 파싱해 두 runtime 경로 없음 assert; C(cwd dir + C 블록)와 `runCheck` 각각: (i) 변경 없음 code 0·`scope-snapshot: OK`, (ii) `tracked.txt` 수정 → 정확히 `outside-tests:tracked.txt`, (iii) 새 `tests/specs/x.spec.js` → `tests-changed:tests/specs/x.spec.js`, (iv) `--require-absent tracked.txt` → `snapshot-not-first:tracked.txt`, (v) `tracked.txt` 수정·미stage 상태에서 snapshot 생성 → 같은 내용으로 `git -C <dir> add tracked.txt` → 시작 xy `' M'`·현재 `'M '`·SHA 동일 확인 후 `status-changed:tracked.txt`; 두 결과의 code·위반 줄·after.z 내용 동일.

## AC (한 셸에서 순서대로, 모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-parity-core.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step9 && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step9.json --allow tests/specs/scope-snapshot-parity-core.spec.js`
2. 범위 gate: `python3 -I - step9 'tests/specs/scope-snapshot-parity-core.spec.js' '' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
