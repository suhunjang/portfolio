# Step 1 — tests-browser-smoke

- 예상 시간: 14분
- 실행 횟수: 시작 snapshot 1회, 브라우저 설치 1회, smoke spec 2회, 전체 테스트 1회, snapshot 비교 1회
- 선행 step: 0 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §3(테마), §11.4, §11.7
3. index.json에서 step 0이 completed인지 확인한다. 아니면 중단한다.
4. `THEME_KEY`, `playwright.config.js`, `scope-snapshot.mjs`를 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log, `-w` 없는 hash-object)과 §11.7 시작 snapshot 명령은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/helpers/theme.js`
- `tests/specs/smoke.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.pw-browsers/**`, `tests/.npm-cache/**`
- `tests/.tmp/**` (시작 snapshot 포함), `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖의 모든 파일
- step 0에서 만든 tests 파일
- `tests/.tmp/start-snapshot-step1.json` (생성 후 다시 쓰지 않는다)

## 작업 (순서 고정)

1. 시작 snapshot — 이 step의 첫 동작이다. 어떤 파일보다 먼저 아래 명령을 그대로 실행한다(§11.7, `{N}` = 1).

```
mkdir -p tests/.tmp && python3 -I - <<'PY'
import hashlib, json, os, subprocess, sys
OUT = 'tests/.tmp/start-snapshot-step1.json'
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

2. 브라우저 설치: `sh tests/scripts/with-env.sh npm --prefix tests run browsers:install`
3. `theme.js`
   - fixture는 `THEME_KEY`가 null일 때만 테마를 주입한다.
   - `collectConsoleErrors`를 §11.4 계약대로 구현한다.
4. `smoke.spec.js` (6개 project)
   - collect를 goto보다 먼저 호출한다.
   - heroName과 테마를 확인한다.
   - finish 결과의 두 배열이 빈 배열인지 확인한다.
   - 비동기 throw를 일으키면 pageErrors가 1건 잡히는지 확인한다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- smoke.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step1.json --allow tests/helpers/theme.js,tests/specs/smoke.spec.js --require-absent tests/helpers/theme.js,tests/specs/smoke.spec.js` → 모두 exit 0 (smoke는 6개 project 모두 통과)
- 마지막 명령은 시작 snapshot이 이 step의 파일보다 늦게 만들어졌거나, 시작 보호 경로가 변경·삭제·원복되었거나, tests 밖 새 경로·runtime 노출·허용 밖 tests 파일이 있으면 exit 1이다.
