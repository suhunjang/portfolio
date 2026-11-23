# Step 0 — tests-env-bootstrap

- 예상 시간: 16분
- 실행 횟수: 시작 snapshot 1회, npm install 1회, bootstrap spec 2회, 전체 테스트 1회, inline 범위 검사 1회
- 선행 step: 없음

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §3, §11.1~§11.4, §11.6, §11.7
3. index.json을 확인한다. 이 step은 선행 step이 없다.
4. 다음을 확인한다: 루트 package.json 없음, `tests/` 없음
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - 하네스 전용: Git 상태를 바꾸는 명령(init, checkout, switch, add, commit, push, reset, stash, merge, rebase, tag 등), Harness 운영 명령(`harness --project-root . ...`)
   - 허용: 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log, `-w` 없는 hash-object), §11.7 시작 snapshot·범위 검사 명령
   - 금지: main 직접 변경, merge, deploy
7. BASE = `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`
8. 공통 실행 계약: `tests/scripts/with-env.sh`를 만든 뒤 npm·node·playwright는 모두 이 래퍼를 거쳐 실행한다.
9. 비교 도구(`scope-snapshot.mjs`)는 이 step에서 만들지 않는다(step 1). 이 step의 범위 gate는 §11.7 inline 검사 C다.

## tracked source 허용 파일 (exact)

- `tests/scripts/with-env.sh`
- `tests/scripts/start-snapshot.py`
- `tests/package.json`
- `tests/package-lock.json`
- `tests/.gitignore`
- `tests/playwright.config.js`
- `tests/specs/bootstrap.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/node_modules/**`, `tests/.npm-cache/**`
- `tests/.tmp/**` (시작 snapshot 포함), `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖의 모든 파일
- `tests/.tmp/start-snapshot-step0.json` (생성 후 다시 쓰지 않는다)
- 위 허용 목록 밖의 tests 파일 (`tests/scripts/scope-snapshot.mjs` 포함)

## 작업 (순서 고정)

1. 시작 snapshot — 이 step의 첫 동작이다. 어떤 파일보다 먼저 아래 명령을 그대로 실행한다(§11.7 S).

```
python3 -I - tests/.tmp/start-snapshot-step0.json <<'PY'
import hashlib, json, os, subprocess, sys
RUNTIME = ('tests/node_modules/', 'tests/.npm-cache/', 'tests/.pw-browsers/', 'tests/.tmp/', 'tests/test-results/', 'tests/playwright-report/', 'tests/screenshots/')
OUT = sys.argv[1]
if not OUT.startswith('tests/.tmp/start-snapshot-') or not OUT.endswith('.json'):
    sys.exit('bad snapshot path: ' + OUT)
os.makedirs('tests/.tmp', exist_ok=True)
def git(*args):
    return subprocess.run(['git', *args], check=True, capture_output=True).stdout
status = git('status', '--porcelain=v1', '-z', '--untracked-files=all')
recs = status.split(bytes(1))
xy = {}
i = 0
while i < len(recs):
    rec = recs[i]
    i += 1
    if not rec:
        continue
    code = rec[:2].decode()
    xy[rec[3:].decode()] = code
    if code[0] in 'RC' or code[1] in 'RC':
        xy[recs[i].decode()] = code
        i += 1
paths = set(xy)
paths.update(p.decode() for p in git('ls-files', '-z').split(bytes(1)) if p)
for root, dirs, names in os.walk('tests'):
    dirs[:] = [d for d in dirs if not (root + '/' + d + '/').startswith(RUNTIME)]
    paths.update(root + '/' + n for n in names)
def digest(p):
    if os.path.isfile(p) and not os.path.islink(p):
        return hashlib.sha256(open(p, 'rb').read()).hexdigest()
    return None
files = {p: digest(p) for p in sorted(paths) if not p.startswith(RUNTIME)}
with open(OUT, 'x') as f:
    json.dump({'statusZHex': status.hex(), 'xy': xy, 'files': files}, f, indent=1, sort_keys=True)
PY
```

2. `with-env.sh`: §11.2 내용을 그대로 쓴다.
3. `tests/scripts/start-snapshot.py`: 위 heredoc의 `PY` 사이 본문을 바이트 단위로 그대로 저장한다(step 1 이후 각 step의 첫 동작이 이 파일을 쓴다).
4. `tests/.gitignore`: §11.1의 7줄을 쓰고 끝에 개행 1개를 둔다.
5. `tests/package.json`: `private`, `type: module`, devDependencies 2개, scripts `test`와 `browsers:install`
6. 설치: `sh tests/scripts/with-env.sh npm --prefix tests install`
7. `playwright.config.js`
   - testDir `./specs`, reporter list, retries 0, outputDir `./test-results`
   - webServer: `python3 -m http.server 4173 --bind 127.0.0.1`, cwd `..`, reuseExistingServer
   - baseURL `http://127.0.0.1:4173`
   - projects 6개. 각각 `colorScheme`과 `metadata.theme`을 지정한다.
     - mobile-dark/light: 375×812
     - tablet-dark/light: 768×1024
     - desktop-dark/light: 1280×800
8. `bootstrap.spec.js` (브라우저 page fixture를 쓰지 않는 node 전용 테스트, desktop-dark에서만 실행하고 나머지 project는 `test.skip`)
   - config: project 6개의 이름·viewport·colorScheme가 위와 같다.
   - `tests/.gitignore`: 끝 개행 1개만 제거한 내용이 §11.1의 7줄과 정확히 같다.
   - `with-env.sh`: 첫 두 줄이 `#!/bin/sh`, `set -eu`이고 `PLAYWRIGHT_BROWSERS_PATH`를 export한다.
   - `start-snapshot.py` subprocess: `python3 -I tests/scripts/start-snapshot.py tests/.tmp/start-snapshot-bootstrap-test-<pid>.json` → exit 0, 결과 JSON에 `statusZHex`·`xy`·`files`가 있고 `files`에 `tests/playwright.config.js`가 있으며 RUNTIME 접두어 경로가 없다. 같은 경로로 다시 실행하면 exit ≠ 0(immutable). `tests/.tmp/other.json` 경로는 exit ≠ 0. 끝나면 테스트 파일을 지운다.
9. 범위 gate: 아래 AC의 마지막 명령(§11.7 C)을 실행한다.

## 완료 기준 (AC)

아래 명령을 하나의 셸에서 순서대로 실행해 모두 exit 0이어야 한다. 마지막 inline 검사는 시작 snapshot 대비 exact 허용 파일 밖의 tests 안팎 변경·삭제·원복, status 변화, runtime 노출, snapshot이 허용 파일보다 늦게 만들어진 경우에 exit 1이다.

```
sh tests/scripts/with-env.sh npm --prefix tests test -- bootstrap.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I - tests/.tmp/start-snapshot-step0.json 'tests/scripts/with-env.sh,tests/scripts/start-snapshot.py,tests/package.json,tests/package-lock.json,tests/.gitignore,tests/playwright.config.js,tests/specs/bootstrap.spec.js' 'tests/scripts/with-env.sh,tests/scripts/start-snapshot.py,tests/package.json,tests/package-lock.json,tests/.gitignore,tests/playwright.config.js,tests/specs/bootstrap.spec.js' <<'PY'
import hashlib, json, os, subprocess, sys
RUNTIME = ('tests/node_modules/', 'tests/.npm-cache/', 'tests/.pw-browsers/', 'tests/.tmp/', 'tests/test-results/', 'tests/playwright-report/', 'tests/screenshots/')
EXEMPT = ('.harness/', '.venv/', 'phases/HOO-81-portfolio-redesign/')
GUARDED = ('.harness/harness.lock.json', '.harness/policy.json')
START = sys.argv[1]
allow = {p for p in sys.argv[2].split(',') if p}
absent = {p for p in sys.argv[3].split(',') if p}
start = json.load(open(START))
def git(*args):
    return subprocess.run(['git', *args], check=True, capture_output=True).stdout
status = git('status', '--porcelain=v1', '-z', '--untracked-files=all')
recs = status.split(bytes(1))
xy = {}
i = 0
while i < len(recs):
    rec = recs[i]
    i += 1
    if not rec:
        continue
    code = rec[:2].decode()
    xy[rec[3:].decode()] = code
    if code[0] in 'RC' or code[1] in 'RC':
        xy[recs[i].decode()] = code
        i += 1
paths = set(xy) | set(start['files'])
paths.update(p.decode() for p in git('ls-files', '-z').split(bytes(1)) if p)
for root, dirs, names in os.walk('tests'):
    dirs[:] = [d for d in dirs if not (root + '/' + d + '/').startswith(RUNTIME)]
    paths.update(root + '/' + n for n in names)
def digest(p):
    if os.path.isfile(p) and not os.path.islink(p):
        return hashlib.sha256(open(p, 'rb').read()).hexdigest()
    return None
files = {p: digest(p) for p in sorted(paths) if not p.startswith(RUNTIME)}
bad = ['snapshot-not-first:' + p for p in sorted(absent) if p in start['files'] or p in start['xy']]
for p in sorted(files):
    if p in allow or (p.startswith(EXEMPT) and p not in GUARDED):
        continue
    if start['files'].get(p) != files[p]:
        bad.append(('tests-changed:' if p.startswith('tests/') else 'outside-tests:') + p)
    elif start['xy'].get(p) != xy.get(p):
        bad.append('status-changed:' + p)
bad += ['runtime-visible:' + p for p in sorted(xy) if p.startswith(RUNTIME) and p not in start['xy']]
with open(START[:-5] + '-after.z', 'wb') as f:
    f.write(status)
if bad:
    sys.exit('\n'.join(bad))
print('scope-snapshot: OK')
PY
```
