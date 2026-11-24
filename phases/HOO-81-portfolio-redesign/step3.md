# Step 3 — scope-snapshot-loader (재검증)

- 목적: strict loader와 S 재사용 분기의 범주 동일. §8.6.
- 19분 / 선행 0~2 / 공통 §9 / gate CGATE
- 허용(exact): `tests/scripts/scope-snapshot.mjs`(step 3 API), `tests/specs/scope-snapshot-loader.spec.js`
- runtime: R0
- 추가 금지: step 1·2 함수 동작

## 작업
1. `SNAP 3` → AC → no-op / 수정.
2. `loadStartSnapshot`(§8.7 순서, 쓰기·snapshot 외 접근 없음). spec(node, desktop-dark, 10초): projectRoot symlink·file 거부; 없음 `unsafe path: missing:`; S로 `parity-<A>` 생성 후 텍스트 변형 `parity-<n>`(stepId 새 이름)마다 S 재사용·loader가 같은 범주로 거부·sha256 불변 — 깨진 JSON·`NaN`·최상위 중복 schemaVersion 3종·`harness` 안 중복(`invalid json`), 키 누락·여분(`keys`), `2`·`true`·`1.0`·`1e0`·`"1"`·최상위 `1.0`+중첩(`schemaVersion`), statusZHex `zz`·`0`·대문자(`statusZHex`), `3f3f`·` ?? `+0xFF(`status parse`), xy 추가·변경(`xy`), files `abc`·대문자 64hex·숫자(`files`), status 비SKIP 경로 제거(`files/status`); 경로(identity 유지) `../outside.txt`, 절대 sentinel(`tests/.tmp/abs-sentinel-<pid>.txt`), `a//b`, `./x`, `x/..`, statusZHex 끝 ` M ../outside.txt`(xy·files 맞춤) → `bad start snapshot: paths:`, loader 기록은 root·`tests`·`tests/.tmp`·snapshot만, sentinel 불변; 정상 사본 반환·S reused; 정리.

## AC
1. `T scope-snapshot-loader.spec.js scope-snapshot-parse.spec.js scope-snapshot-paths.spec.js && FULL && SNAP 3`
2. `CGATE 3 tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-loader.spec.js`
