# Step 0 — tests-env-bootstrap

- 목적: 시작 snapshot을 먼저 남기고 tests 실행 환경(래퍼, snapshot 스크립트, package, gitignore, 직렬 Playwright 설정, 설치)을 만든다.
- 예상 18분 / 선행 없음 / 공통 절차 설계 §15 (래퍼는 작성 뒤부터) / 종료 gate: S reused + inline C
- read-first: 설계 §3, §11.1~§11.4, §11.6, §11.7(규칙, 저장소 상대 경로 계약, projectRoot 유형, 경로 유형 계약, 실행 순서, schema, 재시도 계약, S, C, 설계 블록 추출 규칙, 테스트 격리)
- tracked 허용(exact): `tests/scripts/with-env.sh`, `tests/scripts/start-snapshot.py`, `tests/package.json`, `tests/package-lock.json`, `tests/.gitignore`, `tests/playwright.config.js`, `tests/specs/bootstrap.spec.js`
- runtime: R0 + `tests/node_modules/**`
- 금지: §15.7, `tests/scripts/scope-snapshot.mjs`(step 1~8), S·C 본문 변경, 실제 저장소의 비runtime 경로에 symlink·FIFO 생성

## 작업 (순서 고정)

1. 시작 snapshot: 어떤 파일보다 먼저 `python3 -I - step0 <<'PY'` + 설계 §11.7 S 코드 블록 본문(그대로) + `PY`. 최초 `created`, 재시도 `reused`여야 한다(`unsafe path` 등이면 중단·보고).
2. 시작 조건(최초 snapshot 기준, 재시도에도 동일): 아래가 `step0 start clean`을 출력해야 한다. 아니면 중단.
   `python3 -I -c "import json,sys; s=json.load(open('tests/.tmp/start-snapshot-step0.json')); bad=sorted(p for p in set(s['files'])|set(s['xy']) if p=='package.json' or (p.startswith('tests/') and not p.startswith('tests/.tmp/'))); sys.exit('preexisting: '+','.join(bad)) if bad else print('step0 start clean')"`
3. `with-env.sh`: 설계 §11.2 그대로.
4. `start-snapshot.py`: 작업 1 heredoc 본문을 바이트 그대로 저장.
5. `.gitignore`: §11.1 7줄 + 끝 개행 1개. `package.json`: `private`, `type: module`, devDependencies 2개, scripts `test`·`browsers:install`.
6. 설치: `sh tests/scripts/with-env.sh npm --prefix tests install`
7. `playwright.config.js`: 설계 §11.4, 반드시 `workers: 1`, `fullyParallel: false`.
8. `bootstrap.spec.js` (node 전용, desktop-dark만, 나머지 `test.skip`; 실제 저장소에는 `tests/.tmp/start-snapshot-parity-{숫자}.json`과 `tests/.tmp/snapshot-probes/__retry_probe.txt`만 쓰고 끝나면 삭제, `step{N}` snapshot은 건드리지 않음; S subprocess는 timeout 10초)
   - config: import한 config의 `workers === 1`, `fullyParallel === false`, 6 project 이름·viewport·colorScheme
   - `.gitignore` 7줄 정확 일치, `with-env.sh` 첫 두 줄 `#!/bin/sh`·`set -eu`와 `PLAYWRIGHT_BROWSERS_PATH` export
   - `tests/scripts/start-snapshot.py` bytes = 설계 문서의 S 블록(설계 블록 추출 규칙, 문서는 읽기만)
   - 최초: `python3 -I tests/scripts/start-snapshot.py parity-<A>` → exit 0, `created`, 키 집합이 schema와 같고 `stepId` 일치, 기존 비runtime 파일 `tests/playwright.config.js`의 `files` 값이 그 파일 sha256과 같음, 모든 `files` 값이 64hex 또는 null이고 null인 경로는 실제로 없음(`lstat` ENOENT), SKIP 경로 없음
   - 중간 실패 뒤 재사용: 생성 후 probe `tests/.tmp/snapshot-probes/__retry_probe.txt`를 쓰고 재실행 → exit 0, `reused`, snapshot sha256·mtime 불변. probe는 finally에서 삭제
   - identity 거부: 최초 snapshot을 복사해 한 필드씩 바꾼 별도 `parity-<n>` 파일(`stepId` 파일명과 다름, `head` 40자 0, `base`, `projectRoot` `/tmp/other`, `harness.manifestHash`, `harness.lockSha256`) → 각각 exit ≠ 0, stderr `identity mismatch: {field}` 또는 `bad start snapshot`, sha256 불변
   - schemaVersion 거부(원문 텍스트 변형, 각각 exit ≠ 0, sha256 불변): 값 토큰 `2`·`true`·`1.0`·`1e0` → `bad start snapshot: schemaVersion`; 최상위 중복 키 — 끝 `}` 앞에 `, "schemaVersion": 1.0` 추가, 같은 방식 `1e0`, 여는 `{` 뒤에 `"schemaVersion": 1.0, ` 추가 → 모두 `bad start snapshot: invalid json`; 최상위 값 `1.0`이고 `harness` 객체 안에 `"schemaVersion": 1` 추가 → `schemaVersion`; `files` 값 하나를 `NaN`으로 → `invalid json`
   - 잘못된 id(`step`, `../x`, `Step1`) → exit ≠ 0, 파일 생성 없음
   - projectRoot 유형은 step 1, 저장소 상대 경로 계약 단위 판정은 step 2, 나머지 schema 범주와 경로 계약 거부는 step 3, symlink는 step 5, 특수 파일·조상 symlink는 step 6이 검증한다

## AC (한 셸에서 순서대로, 모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- bootstrap.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step0` (전체는 config의 `workers: 1`로 직렬 실행, 마지막은 `reused` = projectRoot·경로 유형 + strict schema + 현재 identity 대조 통과)
2. 범위 gate: `python3 -I - step0 'tests/scripts/with-env.sh,tests/scripts/start-snapshot.py,tests/package.json,tests/package-lock.json,tests/.gitignore,tests/playwright.config.js,tests/specs/bootstrap.spec.js' 'tests/scripts/with-env.sh,tests/scripts/start-snapshot.py,tests/package.json,tests/package-lock.json,tests/.gitignore,tests/playwright.config.js,tests/specs/bootstrap.spec.js' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
