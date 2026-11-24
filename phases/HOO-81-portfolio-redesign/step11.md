# Step 11 — scope-snapshot-parity-artifacts (재검증)

- 목적: 기록 대상 unsafe 시 after.z 보존 4조합(C·`runCheck`), CLI `tests/.tmp` 조상 링크 거부, 실제 저장소 after.z FIFO·identity 변형 거부를 확인한다(spec 하나). 설계 §11.6 재검증 모드. 통과 뒤 step 12부터 CLI가 종료 gate다.
- 예상 19분 / 선행 0~10 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.6, §11.7(규칙, projectRoot, 경로 유형, 실행 전제, 실행 순서, C, 비교 도구 step 7·8·9~11, 테스트 격리), §12; `tests/helpers/synthetic-repo.js`, `tests/specs/scope-snapshot-parity-core.spec.js`(읽기만)
- tracked 허용(exact): `tests/specs/scope-snapshot-parity-artifacts.spec.js`
- runtime: R0(합성 저장소, `<pid>-outside/`, 실제 저장소 parity 파일과 after.z)
- 금지: §15.7, 도구·helper·다른 spec 수정, 비runtime symlink·FIFO, 합성 저장소 init/add/commit 외 Git 변경

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step11`
2. AC 실행 → 통과면 no-op, 실패면 spec만 계약대로 수정.
3. 계약: 기존 after.z 있음/없음 × 기록 대상 FIFO `tests/specs/p.fifo`/symlink `link-x` 4가지에서 `runCheck`와 C 모두 exit 1·해당 stderr·after.z bytes·mtime 불변 또는 미생성; CLI `tests/.tmp` 외부 링크 → `unsafe path: symlink:tests/.tmp`, 외부 불변; 실제 저장소 after.z FIFO → `non-regular:…-after.z`; identity 7개 변형(`projectRoot`, `head`, `base`, `harness.sourceCommit`, `harness.manifestHash`, `harness.distributionVersion`=`9.9.9`, `harness.lockSha256`) 각각 `start snapshot identity mismatch: {field}`, after.z 미생성, status·tests 밖 sha256 불변.

## AC (한 셸에서 순서대로, 모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-parity-artifacts.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step11 && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step11.json --allow tests/specs/scope-snapshot-parity-artifacts.spec.js`
2. 범위 gate: `python3 -I - step11 'tests/specs/scope-snapshot-parity-artifacts.spec.js' '' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
