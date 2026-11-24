# Step 0 — tests-env-bootstrap (재검증)

- 목적: 시작 snapshot 후 tests 환경 확인, 최초 전체 테스트 전에 S와 `HARNESS_IDENTITY`를 §ID 값으로 동기화. 설계 §8.6.
- 19분 / 선행 없음(§12 완료 전제) / 공통 설계 §9 / gate CGATE
- 허용(exact): `tests/scripts/with-env.sh`, `tests/scripts/start-snapshot.py`, `tests/package.json`, `tests/package-lock.json`, `tests/.gitignore`, `tests/playwright.config.js`, `tests/specs/bootstrap.spec.js`, `tests/scripts/scope-snapshot.mjs`(`HARNESS_IDENTITY` 3값 줄만)
- runtime: R0 + `tests/node_modules/**`
- 추가 금지: S·C 본문 변경, `scope-snapshot.mjs`의 3값 외 변경

## 작업
1. 어떤 파일보다 먼저 `python3 -I - step0 <<'PY'` + 설계 §8.7 S 본문 + `PY`(created/reused 아니면 중단; 2.0.0 snapshot이 남아 있으면 identity mismatch로 멈춤).
2. 원래 7개 파일이 모두 `git ls-files`에 있으면 재검증 모드. 없으면 최초 구축: `python3 -I -c "import json,sys; s=json.load(open('tests/.tmp/start-snapshot-step0.json')); bad=sorted(p for p in set(s['files'])|set(s['xy']) if p=='package.json' or (p.startswith('tests/') and not p.startswith('tests/.tmp/'))); sys.exit('preexisting: '+','.join(bad)) if bad else print('step0 start clean')"` → `step0 start clean`.
3. 테스트 전 동기화: (a) `start-snapshot.py`를 설계 S 블록과 바이트 동일하게; (b) `scope-snapshot.mjs` `HARNESS_IDENTITY` 3값 = §ID. 그 밖 허용 파일은 AC 실패 시에만.
4. 계약: with-env = §8.2, `.gitignore` = §8.1, package·config = §8.3(설치 `W npm --prefix tests install`).
5. `bootstrap.spec.js`(node, desktop-dark, timeout 10초, parity 파일·retry probe만 쓰고 삭제): `workers === 1`·`fullyParallel === false`·6 project; `.gitignore` 7줄; with-env 첫 두 줄·`PLAYWRIGHT_BROWSERS_PATH`; `start-snapshot.py` bytes = S 블록; `HARNESS_IDENTITY` deep-equal S `HARNESS`; `parity-<A>` created·키·`tests/playwright.config.js` sha256·null 경로 부재·SKIP 없음; probe 후 reused·sha256·mtime 불변; identity 변형 6종(`stepId`, `head`, `base`, `projectRoot`, `harness.manifestHash`, `harness.lockSha256`) 거부; schemaVersion `2`·`true`·`1.0`·`1e0` → `bad start snapshot: schemaVersion`, 최상위 중복 3종 → `invalid json`, 최상위 `1.0`+`harness` 안 `"schemaVersion": 1` → `schemaVersion`, files 값 `NaN` → `invalid json`; id `step`·`../x`·`Step1` 거부·파일 없음.
6. 로그 `reverify step0: fixed tests/scripts/start-snapshot.py,tests/scripts/scope-snapshot.mjs`(+추가 파일).

## AC
1. `git diff --no-renames --unified=0 HEAD -- tests/scripts/scope-snapshot.mjs | python3 -I -c "import re,sys; L=[l for l in sys.stdin.read().splitlines() if l.startswith(('+','-')) and not l.startswith(('+++','---'))]; bad=[l for l in L if not re.search('sourceCommit|manifestHash|distributionVersion', l)]; sys.exit('identity-diff: '+repr(bad)) if bad or sum(l[0]=='+' for l in L)>3 else print('identity-diff: OK')"`
2. `W npm --prefix tests install && T bootstrap.spec.js && T scope-snapshot-identity.spec.js scope-snapshot-cli.spec.js scope-snapshot-parity-core.spec.js scope-snapshot-parity-paths.spec.js scope-snapshot-parity-artifacts.spec.js && FULL && SNAP 0`(reused)
3. `CGATE 0 tests/scripts/with-env.sh,tests/scripts/start-snapshot.py,tests/package.json,tests/package-lock.json,tests/.gitignore,tests/playwright.config.js,tests/specs/bootstrap.spec.js,tests/scripts/scope-snapshot.mjs`(최초 구축이면 마지막 항목 제외 7개)
