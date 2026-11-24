# Step 3 — scope-snapshot-loader (재검증)

- 목적: strict loader가 모든 schema 범주에서 S 재사용 분기와 같은 판정임을 확인한다. §11.6 재검증 모드.
- 예상 19분 / 선행 0~2 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.4, §11.6, §11.7(경로 계약, schema·검사 순서, projectRoot, 경로 유형, S, 비교 도구 step 3, 테스트 격리)
- tracked 허용(exact): `tests/scripts/scope-snapshot.mjs`(step 3 API), `tests/specs/scope-snapshot-loader.spec.js`
- runtime: R0
- 금지: §15.7, step 1·2 함수 동작

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step3`
2. AC 실행 → 통과면 no-op, 실패면 계약 안에서 수정.
3. 계약: `loadStartSnapshot`(설계 순서, 쓰기·snapshot 외 접근 없음). spec: projectRoot 거부; 파일 없음 `unsafe path: missing:`; 실제 저장소 `parity-<n>` 변형으로 S·loader 범주 일치(invalid json·keys·schemaVersion·statusZHex·status parse·xy·files·files/status); 경로 계약 거부(정상 identity 유지, `../outside.txt`·절대 경로 sentinel·`a//b`·`./x`·`x/..` key, statusZHex 안 ` M ../outside.txt`) → 모두 `bad start snapshot: paths:`, 대상 접근 0; 정상 사본 반환·S `reused`; 정리.

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-loader.spec.js scope-snapshot-parse.spec.js scope-snapshot-paths.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step3`
2. 범위 gate: `python3 -I - step3 'tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-loader.spec.js' '' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
