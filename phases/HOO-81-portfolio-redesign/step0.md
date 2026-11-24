# Step 0 — tests-env-bootstrap (재검증)

- 목적: 시작 snapshot을 먼저 남기고 tests 실행 환경을 갖춘다. HEAD에 기존 구현이 있으므로 설계 §11.6 재검증 모드.
- 예상 18분 / 선행 없음(§17 preflight 완료 전제) / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §3, §11.1~§11.4, §11.6, §11.7, §17
- tracked 허용(exact): `tests/scripts/with-env.sh`, `tests/scripts/start-snapshot.py`, `tests/package.json`, `tests/package-lock.json`, `tests/.gitignore`, `tests/playwright.config.js`, `tests/specs/bootstrap.spec.js`
- runtime: R0 + `tests/node_modules/**`
- 금지: §15.7, S·C 본문 변경, 비runtime symlink·FIFO

## 작업

1. 시작 snapshot: 어떤 파일보다 먼저 `python3 -I - step0 <<'PY'` + 설계 §11.7 S 코드 블록 본문(그대로) + `PY`. `created`/`reused`가 아니면 중단·보고(§17이 끝나지 않아 2.0.0 snapshot이 남아 있으면 identity mismatch로 멈춘다).
2. 재검증 모드 판정: 7개 파일이 모두 `git ls-files`에 있으면 재검증 모드(`step0 start clean` 생략). 없으면 최초 구축: `python3 -I -c "import json,sys; s=json.load(open('tests/.tmp/start-snapshot-step0.json')); bad=sorted(p for p in set(s['files'])|set(s['xy']) if p=='package.json' or (p.startswith('tests/') and not p.startswith('tests/.tmp/'))); sys.exit('preexisting: '+','.join(bad)) if bad else print('step0 start clean')"`가 `step0 start clean`이어야 한다.
3. 알려진 불일치: 커밋된 `tests/scripts/start-snapshot.py`의 `HARNESS`가 2.0.0이다. 설계 §11.7 S 블록과 바이트 그대로 같게 고친다. 그 밖 파일은 AC가 실패할 때만 고친다.
4. 계약: `with-env.sh` = §11.2; `.gitignore` = §11.1 7줄; `package.json` = `private`, `type: module`, devDependencies 2개, scripts `test`·`browsers:install`(이후 step이 추가한 script 유지); 설치 `sh tests/scripts/with-env.sh npm --prefix tests install`; `playwright.config.js` = §11.4.
5. `bootstrap.spec.js` 계약(node 전용, desktop-dark만, timeout 10초, 실제 저장소에는 parity 파일·retry probe만 쓰고 삭제): config `workers === 1`·`fullyParallel === false`·6 project; `.gitignore` 7줄; `with-env.sh` 첫 두 줄·`PLAYWRIGHT_BROWSERS_PATH`; `start-snapshot.py` bytes = 설계 S 블록; 최초 `parity-<A>` `created`·키·`tests/playwright.config.js` sha256·null 경로 부재·SKIP 없음; probe 후 `reused`·sha256·mtime 불변; identity 변형 6종(`stepId`, `head`, `base`, `projectRoot`, `harness.manifestHash`, `harness.lockSha256`) 거부; schemaVersion 변형(`2`·`true`·`1.0`·`1e0` → `bad start snapshot: schemaVersion`, 최상위 중복 3종 → `invalid json`, 최상위 `1.0` + `harness` 안 `"schemaVersion": 1` → `schemaVersion`, `files` 값 `NaN` → `invalid json`); 잘못된 id `step`·`../x`·`Step1` 거부·파일 없음.
6. 로그: `reverify step0: fixed tests/scripts/start-snapshot.py`(+ 추가 수정 파일).

## AC (한 셸에서 순서대로, 모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests install && sh tests/scripts/with-env.sh npm --prefix tests test -- bootstrap.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step0` (마지막은 `reused`)
2. 범위 gate: `python3 -I - step0 'tests/scripts/with-env.sh,tests/scripts/start-snapshot.py,tests/package.json,tests/package-lock.json,tests/.gitignore,tests/playwright.config.js,tests/specs/bootstrap.spec.js' '' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY` (최초 구축 모드면 세 번째 인자는 두 번째와 같은 목록)
