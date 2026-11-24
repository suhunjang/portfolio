# Step 10 — scope-snapshot-parity-paths (재검증)

- 목적: 저장소 상대 경로 계약 위반 사례 (vi)(상대 경로 탈출·절대 경로)에서 inline C·`runCheck`·CLI가 모두 외부 파일 접근 없이 exit 1이고 산출물이 불변임을 확인한다(spec 하나). 설계 §11.6 재검증 모드.
- 예상 17분 / 선행 0~9 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.6, §11.7(경로 계약, 실행 전제, 실행 순서, C, exec harness, 비교 도구 step 3·8·9~11, 테스트 격리), §12; `tests/helpers/synthetic-repo.js`, `tests/specs/scope-snapshot-parity-core.spec.js`(읽기만)
- tracked 허용(exact): `tests/specs/scope-snapshot-parity-paths.spec.js`
- runtime: R0(합성 저장소, `<pid>-outside/`)
- 금지: §15.7, 도구·helper·다른 spec 수정, 비runtime symlink·FIFO, 합성 저장소 init/add/commit 외 Git 변경

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step10`
2. AC 실행 → 통과면 no-op, 실패면 spec만 계약대로 수정.
3. 계약: step 9와 같은 합성 준비와 외부 sentinel; 정상 identity를 유지한 채 `files`에 변형 A `../<pid>-outside/secret.txt`, 변형 B 외부 절대 경로 key 추가, after.z 고정 bytes; C(exec harness와 subprocess)·`runCheck`(기록용 fs)·CLI subprocess 모두 정확히 `bad start snapshot: paths: tests/.tmp/start-snapshot-parity-1.json`, 외부 경로 접근 0, `computeIdentity`·`takeCurrent`·`writeAfterZ` 미호출, snapshot·after.z·외부 파일 bytes·mtime 불변, sentinel 미출력.

## AC (한 셸에서 순서대로, 모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-parity-paths.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step10 && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step10.json --allow tests/specs/scope-snapshot-parity-paths.spec.js`
2. 범위 gate: `python3 -I - step10 'tests/specs/scope-snapshot-parity-paths.spec.js' '' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
