# Step 3 — scope-snapshot-loader

- 목적: strict schema loader를 만들고 모든 schema 범주에서 Python S 재사용 분기와 같은 판정임을 실제 저장소에서 실행으로 증명한다.
- 예상 18분 / 선행 0~2 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.4(직렬화), §11.7(schema, projectRoot 유형, 경로 유형 계약, S, 비교 도구 step 3, 테스트 격리)
- tracked 허용(exact): `tests/scripts/scope-snapshot.mjs`(추가만), `tests/specs/scope-snapshot-loader.spec.js`(신규)
- runtime: R0
- 금지: §15.7, step 1·2 함수 동작, 상태 수집(step 4), 실제 저장소의 비runtime 경로에 symlink·FIFO 생성

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step3`
2. `scope-snapshot.mjs`에 step 3 API(`loadStartSnapshot`) 추가. 설계 §11.7 순서 그대로, 쓰기 없음.
3. `scope-snapshot-loader.spec.js` (node 전용, desktop-dark만, subprocess timeout 10초)
   - projectRoot(가짜 fs): root symlink·regular file → `unsafe path: symlink:{root}` / `non-regular:{root}`, 기록에 root 외 호출 없음
   - loader: 파일 없음 → `unsafe path: missing:`, stepId≠파일명·형식 오류 throw
   - S·loader 동일 판정(실제 저장소, `workers: 1` 직렬): S로 정상 `parity-<A>`를 만들고 원문 텍스트 변형으로 `parity-<n>` 파일들을 만든다(`stepId`는 새 이름으로 맞춤). 각 파일에 대해 `python3 -I tests/scripts/start-snapshot.py parity-<n>`(재사용 분기)와 `loadStartSnapshot`을 실행해 둘 다 거부하고 `bad start snapshot:` 뒤 범주가 같으며 파일 sha256 불변. 변형: 깨진 JSON, `files` 값 `NaN`(`invalid json`); 최상위 중복 schemaVersion(마지막 `1.0`, 마지막 `1e0`, 처음 `1.0`·마지막 `1`)과 `harness` 안 중복 key(`invalid json`); 키 누락·여분(`keys`); schemaVersion `2`·`true`·`1.0`·`1e0`·`"1"`, 최상위 `1.0` + `harness`·`files` 안 `"schemaVersion": 1`(`schemaVersion`); statusZHex `zz`·홀수 `0`·대문자(`statusZHex`); 잘린 레코드 `3f3f`(`status parse`); xy 경로 추가·값 변경(`xy`); files 값 `abc`·대문자 64hex·숫자(`files`); status 비SKIP 경로를 files에서 제거(`files/status`)
   - 정상 사본: loader가 `{ stepId, identity, entries, xy, files }`를 반환하고 S는 `reused`
   - 끝나면 parity 파일 모두 삭제. snapshot 파일 자체 symlink는 step 5가 검증한다

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-loader.spec.js scope-snapshot-parse.spec.js scope-snapshot-paths.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step3` (마지막은 `reused`)
2. 범위 gate: `python3 -I - step3 'tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-loader.spec.js' 'tests/specs/scope-snapshot-loader.spec.js' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
