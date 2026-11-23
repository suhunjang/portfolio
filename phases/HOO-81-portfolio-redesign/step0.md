# Step 0 — tests-env-bootstrap

- 목적: 시작 snapshot을 먼저 남기고 tests 실행 환경(래퍼, snapshot 스크립트, package, gitignore, Playwright 설정, 설치)을 만든다.
- 예상 19분 / 선행 없음 / 공통 절차 설계 §15 (래퍼는 작성 뒤부터)
- read-first: 설계 §3, §11.1~§11.4, §11.6, §11.7(schema, 재시도 계약, S, C)
- tracked 허용(exact): `tests/scripts/with-env.sh`, `tests/scripts/start-snapshot.py`, `tests/package.json`, `tests/package-lock.json`, `tests/.gitignore`, `tests/playwright.config.js`, `tests/specs/bootstrap.spec.js`
- runtime: R0 + `tests/node_modules/**`
- 금지: §15.7, `tests/scripts/scope-snapshot.mjs`(step 1·2)

## 작업 (순서 고정)

1. 시작 snapshot: 어떤 파일보다 먼저 `python3 -I - step0 <<'PY'` + 설계 §11.7 S 코드 블록 본문(그대로) + `PY`. 최초 `created`, 재시도 `reused`여야 한다.
2. 시작 조건(최초 snapshot 기준, 재시도에도 동일): 아래가 `step0 start clean`을 출력해야 한다. 아니면 중단.
   `python3 -I -c "import json,sys; s=json.load(open('tests/.tmp/start-snapshot-step0.json')); bad=sorted(p for p in set(s['files'])|set(s['xy']) if p=='package.json' or (p.startswith('tests/') and not p.startswith('tests/.tmp/'))); sys.exit('preexisting: '+','.join(bad)) if bad else print('step0 start clean')"`
3. `with-env.sh`: 설계 §11.2 그대로.
4. `start-snapshot.py`: 작업 1 heredoc 본문을 바이트 그대로 저장.
5. `.gitignore`: §11.1 7줄 + 끝 개행 1개. `package.json`: `private`, `type: module`, devDependencies 2개, scripts `test`·`browsers:install`.
6. 설치: `sh tests/scripts/with-env.sh npm --prefix tests install`
7. `playwright.config.js`: 설계 §11.4.
8. `bootstrap.spec.js` (node 전용, desktop-dark만, 나머지 `test.skip`; 테스트 snapshot은 `parity-{숫자}` id만 쓰고 끝나면 삭제, `step{N}` snapshot은 건드리지 않음)
   - config 6 project 이름·viewport·colorScheme, `.gitignore` 7줄 정확 일치, `with-env.sh` 첫 두 줄 `#!/bin/sh`·`set -eu`와 `PLAYWRIGHT_BROWSERS_PATH` export
   - 최초: `python3 -I tests/scripts/start-snapshot.py parity-<A>` → exit 0, `created`, 키 집합이 schema와 같고 `stepId` 일치, `files`에 `tests/playwright.config.js` 있음, RUNTIME 경로 없음
   - 중간 실패 뒤 재사용: 생성 후 탐침 `tests/fixtures/__retry_probe.txt`를 만들고 재실행 → exit 0, `reused`, snapshot sha256·mtime 불변, `files`에 탐침 없음(최초 baseline 유지). 탐침은 finally에서 삭제
   - 다른 identity 거부: 최초 snapshot을 복사해 한 필드씩 바꾼 별도 `parity-<n>` 파일(`stepId` 파일명과 다름, `head` 40자 0, `base`, `projectRoot` `/tmp/other`, `harness.manifestHash`, `harness.lockSha256`, `schemaVersion` 2) → 각각 exit ≠ 0, stderr `identity mismatch: {field}` 또는 `bad start snapshot`, 실행 전후 sha256 불변
   - schema 거부: 여분 키, 키 누락, 깨진 JSON → exit ≠ 0, sha256 불변
   - 잘못된 id(`step`, `../x`, `Step1`) → exit ≠ 0, 파일 생성 없음

## AC (한 셸에서 순서대로, 모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- bootstrap.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step0` (마지막은 `reused`: 저장 스크립트가 최초 snapshot을 덮어쓰지 않음)
2. 범위 gate: `python3 -I - step0 'tests/scripts/with-env.sh,tests/scripts/start-snapshot.py,tests/package.json,tests/package-lock.json,tests/.gitignore,tests/playwright.config.js,tests/specs/bootstrap.spec.js' 'tests/scripts/with-env.sh,tests/scripts/start-snapshot.py,tests/package.json,tests/package-lock.json,tests/.gitignore,tests/playwright.config.js,tests/specs/bootstrap.spec.js' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
