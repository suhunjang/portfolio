# Step 11 — scope-snapshot-parity-artifacts (재검증)

- 목적: unsafe 시 after.z 보존 4조합, CLI `tests/.tmp` 조상 링크 거부, after.z FIFO·identity 변형 거부를 확인한다. §11.6 재검증 모드. 통과 뒤 step 12부터 CLI gate.
- 예상 19분 / 선행 0~10 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.6, §11.7, §12; `tests/helpers/synthetic-repo.js`, `tests/specs/scope-snapshot-parity-core.spec.js`(읽기만)
- tracked 허용(exact): `tests/specs/scope-snapshot-parity-artifacts.spec.js`
- runtime: R0(합성 저장소, 실제 저장소 parity 파일·after.z)
- 금지: §15.7, 도구·helper·다른 spec 수정

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step11`
2. AC 실행 → 통과면 no-op, 실패면 spec만 수정.
3. 계약: step 9 합성 준비; 기존 after.z 있음/없음 × 기록 대상 FIFO `tests/specs/p.fifo`/symlink `link-x → <outside>/secret.txt` 4가지에서 `runCheck({ startFile, allow: [그 경로] })`와 C 모두 exit 1·stderr에 `non-regular:tests/specs/p.fifo` 또는 `symlink:link-x`, after.z open 없음, 있음이면 bytes·mtime 불변, 없음이면 미생성; CLI(cwd dir) `tests/.tmp → <outside>/tmpdir` → `unsafe path: symlink:tests/.tmp`, 외부 불변; 실제 저장소 after.z FIFO → `non-regular:…-after.z`; identity 7개 변형(`projectRoot`=`/tmp/other`, `head`=40자 0, `base`=40자 f, `harness.sourceCommit`, `harness.manifestHash`, `harness.distributionVersion`=`9.9.9`, `harness.lockSha256`=64자 0) 각각 `start snapshot identity mismatch: {field}`, after.z 미생성, status·tests 밖 sha256 불변.

## AC (한 셸에서 순서대로, 모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-parity-artifacts.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step11 && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step11.json --allow tests/specs/scope-snapshot-parity-artifacts.spec.js`
2. 범위 gate: `python3 -I - step11 'tests/specs/scope-snapshot-parity-artifacts.spec.js' '' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
