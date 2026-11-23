# Step 0 — tests-env-bootstrap

- 예상 시간: 19분
- 실행 횟수: 시작 snapshot 1회, npm install 1회, scope-snapshot spec 2회, 전체 테스트 1회, snapshot 비교 1회
- 선행 step: 없음

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §3, §11.1~§11.4, §11.7
3. index.json을 확인한다. 이 step은 선행 step이 없다.
4. 다음을 확인한다: 루트 package.json 없음, `tests/` 없음
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - 하네스 전용: Git 상태를 바꾸는 명령(init, checkout, switch, add, commit, push, reset, stash, merge, rebase, tag 등), Harness 운영 명령(`harness --project-root . ...`)
   - 허용: 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log, `-w` 없는 hash-object), §11.7 시작 snapshot 명령
   - 금지: main 직접 변경, merge, deploy
7. BASE = `d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d`
8. 공통 실행 계약: `tests/scripts/with-env.sh`를 만든 뒤 npm·node·playwright는 모두 이 래퍼를 거쳐 실행한다.

## tracked source 허용 파일 (exact)

- `tests/scripts/with-env.sh`
- `tests/scripts/scope-snapshot.mjs`
- `tests/package.json`
- `tests/package-lock.json`
- `tests/.gitignore`
- `tests/playwright.config.js`
- `tests/specs/scope-snapshot.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/node_modules/**`, `tests/.npm-cache/**`
- `tests/.tmp/**` (시작 snapshot 포함), `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖의 모든 파일
- `tests/.tmp/start-snapshot-step0.json` (생성 후 다시 쓰지 않는다)

## 작업 (순서 고정)

1. 시작 snapshot — 이 step의 첫 동작이다. `with-env.sh`, `scope-snapshot.mjs`를 포함한 어떤 파일보다 먼저 아래 명령을 그대로 실행한다(§11.7, `{N}` = 0).

```
mkdir -p tests/.tmp && python3 -I - <<'PY'
import hashlib, json, os, subprocess, sys
OUT = 'tests/.tmp/start-snapshot-step0.json'
if os.path.exists(OUT):
    sys.exit('start snapshot already exists: ' + OUT)
def git(*args):
    return subprocess.run(['git', *args], check=True, capture_output=True).stdout
status = git('status', '--porcelain=v1', '-z', '--untracked-files=all')
recs = status.split(bytes(1))
paths = set()
i = 0
while i < len(recs):
    rec = recs[i]
    i += 1
    if not rec:
        continue
    paths.add(rec[3:].decode())
    if rec[0:1] in (b'R', b'C') or rec[1:2] in (b'R', b'C'):
        paths.add(recs[i].decode())
        i += 1
paths.update(p.decode() for p in git('ls-files', '-z').split(bytes(1)) if p)
protected = {}
for p in sorted(paths):
    if p.startswith('tests/'):
        continue
    protected[p] = hashlib.sha256(open(p, 'rb').read()).hexdigest() if os.path.isfile(p) else None
with open(OUT, 'x') as f:
    json.dump({'statusZHex': status.hex(), 'protected': protected}, f, indent=1, sort_keys=True)
PY
```

2. `with-env.sh`: §11.2 내용을 그대로 쓴다.
3. `scope-snapshot.mjs`: §11.7 비교 도구 계약(`STATUS_ARGS`, `parseStatusZ`, `loadStartSnapshot`, `hashPath`, `takeCurrent`, `diffAgainstStart`, `classifyChanges`, `checkSnapshotFirst`, CLI `--check`)을 구현한다. git 실행 함수와 fs는 주입할 수 있게 하고 Git 읽기 명령만 쓴다. 시작 snapshot 파일을 만들거나 고치는 기능은 두지 않는다.
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
8. `scope-snapshot.spec.js` (브라우저 page fixture를 쓰지 않는 node 전용 테스트, desktop-dark에서만 실행하고 나머지 project는 `test.skip`, git·fs는 가짜 주입)
   - `parseStatusZ`
     - ` M CLAUDE.md`, `?? docs/a.md` → xy·path 정확
     - `R  new.md` + NUL + `old.md` → `origPath === 'old.md'`
     - 빈 입력 → `[]`, 잘린 레코드 → throw
   - `loadStartSnapshot`: 파일 없음, 깨진 JSON, `protected` 누락 → throw
   - 시작 당시 수정돼 있던 `CLAUDE.md` (시작 status ` M`, 시작 hash h1)
     - 현재 ` M`, hash h1 → 위반 0 (시작 전 Harness 변경 허용)
     - 원복: 현재 status에 없음, hash h0 → Change `{ kind: 'content-changed', xyBefore: ' M', xyAfter: null }`, `outside-tests:CLAUDE.md`
     - 삭제: 현재 ` D`, hash null → Change `{ kind: 'deleted' }`, `outside-tests:CLAUDE.md`
     - 같은 status ` M`에서 내용 변경 h2 → Change `{ kind: 'content-changed', xyBefore: ' M', xyAfter: ' M' }`, `outside-tests:CLAUDE.md`
   - 시작 때 깨끗했던 추적 파일 `README.md`(status에 없음, 보호 hash h)
     - 현재 ` M`, hash h' → `outside-tests:README.md`
     - 현재 status에 없음, hash h → 위반 0
   - 새 `?? docs/x.md` → `outside-tests:docs/x.md`
   - 새 `?? .harness/runtime/a.json`, `phases/HOO-81-portfolio-redesign/step3.md` hash 변경 → 위반 0 (런타임 면제)
   - `.harness/policy.json`, `.harness/harness.lock.json` hash 변경 → 각각 `outside-tests:`
   - 새 `?? tests/node_modules/x/index.js` → `runtime-visible:`
   - 새 `?? tests/specs/scope-snapshot.spec.js` → 위반 0, 새 `?? tests/specs/other.spec.js` → `unexpected-tests:`
   - 새 `R  tests/x.js` + 원래 경로 `README.md`, README hash null → `outside-tests:README.md`와 `unexpected-tests:tests/x.js`
   - `checkSnapshotFirst`: 시작 status에 `?? tests/scripts/scope-snapshot.mjs`가 있으면 → `snapshot-not-first:tests/scripts/scope-snapshot.mjs`, 없으면 `[]`
   - `takeCurrent`: 시작 보호 경로는 현재 status에 없어도 모두 hash된다. tests 안 경로는 hash하지 않는다.
   - 모든 함수가 입력을 변경하지 않는다.
   - CLI subprocess: `--check`에 없는 start 파일 → exit 1, 깨진 JSON → exit 1

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step0.json --allow tests/scripts/with-env.sh,tests/scripts/scope-snapshot.mjs,tests/package.json,tests/package-lock.json,tests/.gitignore,tests/playwright.config.js,tests/specs/scope-snapshot.spec.js --require-absent tests/scripts/with-env.sh,tests/scripts/scope-snapshot.mjs` → 모두 exit 0
- 마지막 명령은 다음 중 하나라도 있으면 exit 1이다: 시작 snapshot이 도구보다 늦게 만들어짐, 시작 보호 경로의 변경·삭제·원복, tests 밖 새 경로, tests 안 runtime 경로 노출, 허용 목록 밖 tests 파일.
