# Step 1 — scope-snapshot-paths (재검증)

- 목적: projectRoot·경로 유형 검사와 안전 읽기, projectRoot symlink·non-directory 거부가 JS·S·C에서 같은 판정임을 확인한다. §11.6 재검증 모드.
- 예상 17분 / 선행 0 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.6, §11.7(projectRoot, 경로 유형, 실행 전제, S, C, 블록 추출, exec harness, 비교 도구 step 1, 테스트 격리), §12
- tracked 허용(exact): `tests/scripts/scope-snapshot.mjs`(step 1 API), `tests/specs/scope-snapshot-paths.spec.js`
- runtime: R0(합성 저장소, `<pid>-link`, `<pid>-file`)
- 금지: §15.7, 이후 step API 변경, S·C 본문 변경, dirfd/openat·경쟁 주입 테스트

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step1`
2. AC 실행 → 통과면 no-op, 실패면 계약 안에서 수정.
3. 계약: step 1 API(fs 주입, 쓰기·CLI 없음). spec: `checkRoot`(4유형, lstat 1회); `checkPath`(root 오류 전파, 조상 symlink·file, missing 허용, leaf 유형, `lstatSync`만); `readRegular`(flags `O_NOFOLLOW`·`O_NONBLOCK`, FIFO → `non-regular:`, read 없음); 합성 projectRoot에서 JS·S·C exec harness가 `symlink:<link>`/`non-regular:<file>`, root lstat 1회 외 접근 0, 산출물 없음; 입력 불변.

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-paths.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step1`
2. 범위 gate: `python3 -I - step1 'tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-paths.spec.js' '' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
