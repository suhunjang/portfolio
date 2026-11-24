# Step 3 — scope-snapshot-loader (재검증)

- 목적: strict schema loader(저장소 상대 경로 계약 포함)가 모든 schema 범주에서 S 재사용 분기와 같은 판정임을 확인한다. 설계 §11.6 재검증 모드.
- 예상 19분 / 선행 0~2 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.4, §11.6, §11.7(저장소 상대 경로 계약, schema·검사 순서, projectRoot 유형, 경로 유형 계약, S, 비교 도구 step 3, 테스트 격리)
- tracked 허용(exact): `tests/scripts/scope-snapshot.mjs`(step 3 API), `tests/specs/scope-snapshot-loader.spec.js`
- runtime: R0
- 금지: §15.7, step 1·2 함수 동작, 비runtime 경로 symlink·FIFO

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step3`
2. AC 실행 → 통과면 no-op, 실패면 아래 계약 안에서 수정.
3. 계약: `loadStartSnapshot`(설계 순서, 쓰기·snapshot 외 접근 없음). spec(node 전용, desktop-dark, timeout 10초): projectRoot symlink·file 거부; 파일 없음 `unsafe path: missing:`; S·loader 동일 범주(실제 저장소 `parity-<n>` 변형: invalid json(깨진 JSON, `NaN`, 최상위·중첩 중복), keys, schemaVersion(`2`·`true`·`1.0`·`1e0`·`"1"`, 중첩 schemaVersion), statusZHex(`zz`·홀수·대문자), status parse(`3f3f`), xy, files, files/status); 경로 계약 거부(정상 identity 유지, `files`에 `../outside.txt`·절대 경로 sentinel·`a//b`·`./x`·`x/..`, statusZHex에 ` M ../outside.txt`) → S·loader 모두 `bad start snapshot: paths:`, 대상 경로 접근 0, sentinel 불변; 정상 사본 반환과 S `reused`; parity 파일·sentinel 삭제.

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-loader.spec.js scope-snapshot-parse.spec.js scope-snapshot-paths.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step3` (마지막은 `reused`)
2. 범위 gate: `python3 -I - step3 'tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-loader.spec.js' '' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
