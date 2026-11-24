# Step 0 — tests-env-bootstrap (재검증)

- 목적: 시작 snapshot을 먼저 남기고 tests 실행 환경(래퍼, snapshot 스크립트, package, gitignore, 직렬 Playwright 설정, 설치)을 갖춘다. HEAD에 기존 구현이 있으므로 설계 §11.6 재검증 모드로 실행한다.
- 예상 18분 / 선행 없음 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §3, §11.1~§11.4, §11.6(재검증 모드), §11.7(전체), §17(preflight 완료 여부)
- tracked 허용(exact): `tests/scripts/with-env.sh`, `tests/scripts/start-snapshot.py`, `tests/package.json`, `tests/package-lock.json`, `tests/.gitignore`, `tests/playwright.config.js`, `tests/specs/bootstrap.spec.js`
- runtime: R0 + `tests/node_modules/**`
- 금지: §15.7, S·C 본문 변경, 실제 저장소 비runtime 경로에 symlink·FIFO 생성

## 작업

1. 시작 snapshot: 어떤 파일보다 먼저 `python3 -I - step0 <<'PY'` + 설계 §11.7 S 코드 블록 본문(그대로) + `PY`. `created` 또는 `reused`가 아니면 중단·보고.
2. 재검증 모드 판정: 위 7개 파일이 모두 `git ls-files`에 있으면 재검증 모드(최초 구축의 `step0 start clean` 조건은 생략). 없으면 최초 구축: 아래가 `step0 start clean`을 출력해야 한다. `python3 -I -c "import json,sys; s=json.load(open('tests/.tmp/start-snapshot-step0.json')); bad=sorted(p for p in set(s['files'])|set(s['xy']) if p=='package.json' or (p.startswith('tests/') and not p.startswith('tests/.tmp/'))); sys.exit('preexisting: '+','.join(bad)) if bad else print('step0 start clean')"`
3. 알려진 불일치: 커밋된 `tests/scripts/start-snapshot.py`의 `HARNESS`는 2.0.0이다. 이 파일을 설계 §11.7 S 블록과 바이트 그대로 같게 고친다(설계 블록 추출 규칙). 그 밖 파일은 AC가 실패할 때만 아래 계약대로 고친다.
4. 계약(최초 구축·수정 기준): `with-env.sh` = 설계 §11.2; `.gitignore` = §11.1 7줄 + 끝 개행 1개; `package.json` = `private`, `type: module`, devDependencies 2개, scripts `test`·`browsers:install`(이후 step이 추가한 script는 유지); 설치 `sh tests/scripts/with-env.sh npm --prefix tests install`; `playwright.config.js` = §11.4(`workers: 1`, `fullyParallel: false`).
5. `bootstrap.spec.js` 계약(node 전용, desktop-dark만; 실제 저장소에는 `tests/.tmp/start-snapshot-parity-{숫자}.json`과 `tests/.tmp/snapshot-probes/__retry_probe.txt`만 쓰고 삭제; S subprocess timeout 10초)
   - config `workers === 1`, `fullyParallel === false`, 6 project 이름·viewport·colorScheme
   - `.gitignore` 7줄, `with-env.sh` 첫 두 줄 `#!/bin/sh`·`set -eu`와 `PLAYWRIGHT_BROWSERS_PATH` export
   - `tests/scripts/start-snapshot.py` bytes = 설계 S 블록
   - 최초 `parity-<A>` → `created`, 키 집합·`stepId`, `tests/playwright.config.js` sha256, 값 64hex|null(null은 실제 없음), SKIP 경로 없음
   - probe를 쓴 뒤 재실행 → `reused`, sha256·mtime 불변
   - identity 거부(`stepId`·`head`·`base`·`projectRoot`·`harness.manifestHash`·`harness.lockSha256` 각각 변형) → exit ≠ 0, sha256 불변
   - schemaVersion 거부(`2`·`true`·`1.0`·`1e0` → `schemaVersion`; 최상위 중복 키 3종 → `invalid json`; 최상위 `1.0` + `harness` 안 `"schemaVersion": 1` → `schemaVersion`; `NaN` → `invalid json`)
   - 잘못된 id(`step`, `../x`, `Step1`) → exit ≠ 0, 파일 없음
6. 결과 기록: runner 로그에 `reverify step0: fixed tests/scripts/start-snapshot.py` 또는 추가 수정 파일 목록.

## AC (한 셸에서 순서대로, 모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests install && sh tests/scripts/with-env.sh npm --prefix tests test -- bootstrap.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step0` (마지막은 `reused`)
2. 범위 gate: `python3 -I - step0 'tests/scripts/with-env.sh,tests/scripts/start-snapshot.py,tests/package.json,tests/package-lock.json,tests/.gitignore,tests/playwright.config.js,tests/specs/bootstrap.spec.js' '' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY` (최초 구축 모드면 세 번째 인자는 두 번째와 같은 목록)
