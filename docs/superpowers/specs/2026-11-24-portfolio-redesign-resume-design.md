# HOO-81 resume 설계 보완 (runtime-replan v47 · base-fix v48 · astra-findings v49 · v50 · v51)

- 원 설계(유효, 수정 금지): `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md`(compact v46). `§n`은 원 설계 절, `§R n`은 이 문서 절.
- 원 phase `HOO-81-portfolio-redesign`: step 0~39 completed, step 40 `axe-classify` blocked(이력 evidence, 읽기만). resume phase `HOO-81-portfolio-redesign-resume`: step 0~34.
- resume BASE_HEAD(불변): `4b2ec3b325f400edefca0fbcfb8ff83bf739ff89`(`chore(HOO-81): record step 40 runtime blocker`, metadata-only). 마지막 완료 구현 commit(이력): `1d5d27b0377ef575b9e54d79b7f8178e9af3daad`.
- blocker(불변): `tests/fixtures/axe-collected.json` = entry 12 / occurrence 139(color-contrast 61, nested-interactive 78) / 서로 다른 `ruleId|canonical target` pair 25. 원 §6.2 산정 147분 > 20 → step 40 blocked. 원 step 0~39 재실행·step 40 재설정·blocker evidence 편집 금지.
- 리뷰 반영: Astra record `b0a51811c7c6612b4804c04d642eb342029258fe04b86ebc8971bc21c0a9e4da`(v49: verify-scope 호환 step, occurrence 배치+통합, prune no-op 제외), `04b99cce0e542dd289fd8eab84634fdd4686f8a6afc899ba83415f8a26872cad`(v50: 보호 경로 3계층 §R4, 배치 브라우저 환경·재분할 §R5, 기존 산출물 분기 §R10), `4d568872c3acc8a009eee0e43a123b90a235144f07d554ac2d5feda03a608333`(v51: no-op 전 필수 산출물 존재 검사 §R11, `OCC_RUN` 단일 cleanup §R5.1, evidence 정확 집계 검증 §R6).
- 원 승인·리뷰 재사용 없음. §ID·§G·§8.5 약어·§6.4/§6.5·§11·§THEME는 원 설계 참조.
- §R FLOW: materialize → 현재 브랜치 plan-only commit → Astra `gpt-6-astra` CLEAN → 새 대표 exact 승인 → resume phase만 fresh runner(step 0~34) → 전체 검증 → exact-commit Astra 리뷰 CLEAN → feature push → OPEN PR → tested·reviewed·pushed·PR head SHA 동일 확인. merge·deploy·main 직접 변경 없음.

## R1. 불변·금지

- 원 §9 공통 금지 전부 유지. 추가: 기존 구현 commit·artifact·runtime snapshot(`tests/.tmp/start-snapshot-step0..40*`) 보존, `git reset/restore/checkout/clean`·광범위 삭제·push 금지, 원 phase `phases/HOO-81-portfolio-redesign/**`와 원 설계·`CLAUDE.md`·`tests/fixtures/axe-collected.json` 읽기만.
- `css/themes.css` 읽기 전용. 색 값·색 역할, 서체 asset·weight, 문구·수치·콘텐츠, 새 이미지·아이콘, 범위 확장 금지(원 §11.3).
- 빌더 Git 읽기: 원 §9 목록(rev-parse, diff, show, ls-files, ls-tree, status, log, `-w` 없는 hash-object).
- 프로세스: 각 step이 스스로 띄운 자식 프로세스만 종료할 수 있다. 다른 프로세스 종료(`kill`·`pkill`·`killall` 등) 금지.
- 모든 step 20분 이하(하네스 30분 상한 미만). 각 step은 exact 허용 파일·runtime·선행·AC(`… → FULL → VS → RGATE`/`RGATE_B`)·중단 조건을 갖는다.

## R2. 약어 (원 §8.5에 추가)

- `RSNAP k` = `python3 -I tests/scripts/start-snapshot.py step{100+k}`(snapshot id `step100`~`step134`, 원 `step0..40`과 충돌 없음, 고정 S 정규식 `step[0-9]+` 안). snapshot은 O_EXCL로 생성되고 재시도 시 identity 검사 후 재사용되므로 step 중 불변.
- `RGATE k <A> [<R>]` = `W node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step{100+k}.json --allow <A> [--require-absent <R>]`.
- `PREFLIGHT` = `python3 -I - <<'PY'` + §R4 블록 + `PY`; `OCC_CHECK b` = `python3 -I - b <<'PY'` + §R5 블록 + `PY`; `OCC_RUN b` = §R5.1 공용 실행 절차; `INTEGRATE_CHECK` = `python3 -I - <<'PY'` + §R6 블록 + `PY`; `MERGE_CHECK` = `python3 -I - <<'PY'` + §R7 블록 + `PY`.
- `RBRANCH k <R>` = `python3 -I - k --probe <R> <<'PY'` + §R10 블록 + `PY`; `RGATE_B k <A> <R>` = `python3 -I - k <A> <R> <<'PY'` + §R10 블록 + `PY`.
- `REQ k <P>` = `python3 -I - k <P> <<'PY'` + §R11 블록 + `PY`(P = 쉼표 구분 exact 경로, 쓰기 없음).
- `SHA_SAVE <file> <tag>` = `python3 -I -c "import hashlib,os,sys; os.makedirs('tests/.tmp/resume-sha', exist_ok=True); open('tests/.tmp/resume-sha/'+sys.argv[2]+'.txt','w').write(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" <file> <tag>`.
- `SHA_DIFF <file> <tag> <label>` = `python3 -I -c "import hashlib,sys; a=open('tests/.tmp/resume-sha/'+sys.argv[2]+'.txt').read(); b=hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest(); print(sys.argv[3]+': '+('unchanged' if a==b else 'changed'))" <file> <tag> <label>`(쓰기 없음, 로그만).
- no-op 규칙(이월 step 18·19·21·22·28·29·30·34만): `RSNAP` 뒤 첫 probe는 그 step의 `REQ`(§R11). `REQ` PASS일 때만 AC-first no-op 가능: 나머지 AC(모두 쓰기 없는 명령)를 실행해 통과하면 파일 불변·로그 `resume step{k}: no-op`. `REQ` FAIL이면 no-op 불가 — 그 step 허용 경로 안에서 원 승인 작업을 수행한 뒤 완전한 AC(`REQ`부터)를 재실행한다(없는 산출물이 허용 경로 밖이면 원인 step 보고·중단). `REQ` PASS여도 AC가 실패하면 허용 파일 안에서 원 승인 작업 후 완전한 AC 재실행. §R10 분기 step(20·23·24·25·26·27)은 §R10이 우선하고, step 31·32·33은 §R8 변경형이며 no-op 대상이 아니다.

## R3. verify-scope 호환 준비 (resume step 0)

- 문제: 원 `tests/scripts/verify-scope.mjs`(원 §8.4)는 commit된 resume 설계와 `phases/HOO-81-portfolio-redesign-resume/**`를 범위 밖으로 거부 → 모든 `VS` 실패.
- 변경(이 step만, 허용 파일 2개): `tests/scripts/verify-scope.mjs`, `tests/specs/verify-scope-resume.spec.js`(신규).
  - 하네스 소유 committed 면제 목록에 정확히 `docs/superpowers/specs/2026-11-24-portfolio-redesign-resume-design.md` 1개 추가(원 설계와 같은 취급: committed 면제, staged·worktree 변경은 위반).
  - 하네스 런타임 면제에 `phases/HOO-81-portfolio-redesign-resume/**` 추가(원 phase 경로와 같은 취급, 접두 정확 일치 `phases/HOO-81-portfolio-redesign-resume/`).
  - 그 밖 정책·상수(`GIT_DIFF_PATH_ARGS`, `GIT_DIFF_PATCH_ARGS`, 위반 판정)는 불변. `--self-test`에 아래 사례 추가.
- 회귀(self-test와 spec 모두, 가짜 git 입력): 허용 — committed resume 설계, committed·worktree·untracked `phases/HOO-81-portfolio-redesign-resume/index.json`·`step0.md`; 위반 — worktree·staged 변경된 resume 설계, committed `docs/superpowers/specs/other.md`, committed `docs/superpowers/specs/2026-11-24-portfolio-redesign-resume-design.md.bak`, committed·worktree `phases/OTHER/x.json`, committed `phases/HOO-81-portfolio-redesign-resume-x/a.json`(접두 함정), 미커밋 `.harness/policy.json`, worktree 원 설계 수정, 미커밋 `CLAUDE.md`; 기존 self-test 사례 전부 통과 유지. 실저장소 `VS` → `verify-scope: OK`.

## R4. resume step 1 preflight (검증 전용)

- 보호 경로 P = 원 phase 디렉터리 `phases/HOO-81-portfolio-redesign/`, 원 설계, `CLAUDE.md`, `tests/fixtures/axe-collected.json`. 계층(같은 P pathspec, 각각 실행, 하나라도 출력이 있으면 중단): (a) commit `git diff --no-renames --name-only BASE_HEAD HEAD -- P`, (b) HEAD→index `git diff --cached --no-renames --name-only HEAD -- P`, (c) index→worktree `git diff --no-renames --name-only -- P`, (c′) 원 phase untracked `git ls-files --others --exclude-standard -- phases/HOO-81-portfolio-redesign/`. 변경이 없으면 출력이 비고 exit 0(`--exit-code` 미사용)이라 안전하다.

```
import json, os, subprocess, sys
BASE_HEAD = '4b2ec3b325f400edefca0fbcfb8ff83bf739ff89'
PLAN = ('docs/superpowers/specs/2026-11-24-portfolio-redesign-resume-design.md', 'tests/scripts/verify-scope.mjs', 'tests/specs/verify-scope-resume.spec.js')
PROTECTED = ('phases/HOO-81-portfolio-redesign/', 'docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md', 'CLAUDE.md', 'tests/fixtures/axe-collected.json')
def git(*a):
    return subprocess.run(['git', *a], check=True, capture_output=True).stdout.decode()
def names(*a):
    return [p for p in git(*a).split('\n') if p]
if BASE_HEAD not in git('log', '--format=%H', 'HEAD').split():
    sys.exit('preflight: head-not-descendant')
extra = [p for p in names('diff', '--no-renames', '--name-only', BASE_HEAD, 'HEAD') if p not in PLAN and not p.startswith('phases/HOO-81-portfolio-redesign-resume/')]
if extra:
    sys.exit('preflight: unexpected-commit-paths:' + ','.join(extra))
LAYERS = (
    ('commit', ('diff', '--no-renames', '--name-only', BASE_HEAD, 'HEAD', '--') + PROTECTED),
    ('index', ('diff', '--cached', '--no-renames', '--name-only', 'HEAD', '--') + PROTECTED),
    ('worktree', ('diff', '--no-renames', '--name-only', '--') + PROTECTED),
    ('untracked', ('ls-files', '--others', '--exclude-standard', '--', PROTECTED[0])),
)
for layer, args in LAYERS:
    hit = names(*args)
    if hit:
        sys.exit('preflight: protected-changed:' + layer + ':' + ','.join(hit))
idx = json.loads(git('show', BASE_HEAD + ':phases/HOO-81-portfolio-redesign/index.json'))
st = {s['step']: s for s in idx['steps']}
bad = [str(n) for n in range(40) if st[n]['status'] != 'completed']
if bad:
    sys.exit('preflight: not-completed:' + ','.join(bad))
if st[40]['status'] != 'blocked' or '147' not in json.dumps(st[40], ensure_ascii=False):
    sys.exit('preflight: step40-blocker')
col = json.load(open('tests/fixtures/axe-collected.json', encoding='utf-8'))
F = {'key', 'scenario', 'project', 'ruleId', 'impact', 'targets', 'selectors'}
if not isinstance(col, list) or len(col) != 12 or any(not isinstance(e, dict) or set(e) != F for e in col):
    sys.exit('preflight: collected-shape')
cnt = {}
for e in col:
    cnt[e['ruleId']] = cnt.get(e['ruleId'], 0) + len(e['targets'])
if cnt != {'color-contrast': 61, 'nested-interactive': 78}:
    sys.exit('preflight: collected-counts:' + json.dumps(cnt))
if len({e['ruleId'] + '|' + t for e in col for t in e['targets']}) != 25:
    sys.exit('preflight: collected-pairs')
need = ['tests/package.json', 'tests/playwright.config.js', 'tests/node_modules/@playwright/test/index.js', 'tests/scripts/with-env.sh', 'tests/scripts/start-snapshot.py', 'tests/scripts/scope-snapshot.mjs', 'tests/scripts/design-intake-check.py', 'tests/scripts/verify-scope.mjs', 'tests/scripts/make-fixtures.mjs', 'tests/specs/verify-scope-resume.spec.js', 'tests/helpers/css-parse.js', 'tests/helpers/color-vocab.js', 'tests/helpers/design-guard-color-pairs.js', 'tests/helpers/design-guard-color-rules.js', 'tests/helpers/design-guard-color.js', 'tests/helpers/design-guard-font.js', 'tests/helpers/design-guard-css.js', 'tests/helpers/design-guard.js', 'tests/helpers/theme.js', 'tests/helpers/content.js', 'tests/helpers/modal.js', 'tests/helpers/axe.js', 'tests/helpers/axe-prepare.js', 'tests/specs/smoke.spec.js', 'tests/specs/axe-helper.spec.js', 'tests/specs/axe.spec.js', 'tests/fixtures/claude-design-intake.json', 'tests/fixtures/baseline-data.json', 'tests/fixtures/baseline-index.html', 'tests/fixtures/content-exceptions.json']
miss = [p for p in need if not os.path.isfile(p) or os.path.islink(p)]
if miss:
    sys.exit('preflight: missing:' + ','.join(miss))
late = [p for p in ('tests/fixtures/axe-baseline.json', 'tests/fixtures/axe-remediation-plan.json') if os.path.lexists(p)]
if late:
    sys.exit('preflight: classify-output-exists:' + ','.join(late))
print('resume-preflight: OK')
```

## R5. occurrence 분류 배치 (resume step 2~15)

- occurrence = collected entry `e`의 target `t` 하나: (key, scenario, project, ruleId, target, pair = `ruleId|target`). 139개를 (key, target) 코드 포인트 오름차순 정렬, batch b(1~14) = 정렬 목록 `[(b-1)*10, b*10)`. 개수(정확): batch 1~13 각 10, batch 14 = 9(13×10 + 9 = 139).
- 산정(고정): `2(준비) + 2(서버 기동·readiness·브라우저 기동·정리) + occurrenceCount×1 + 6(검증)` → batch 1~13 = 20분, batch 14 = 19분. pair 중복 제거로 조사를 줄이지 않는다.
- 판정 기준 = 원 step 40 작업 3(기존 색 값·색 custom property·색 적용 위치를 바꿔야 해소 → `requiresColorChange: true`, 크기·여백·레이아웃·속성·마크업·렌더만으로 해소 → false; `css-token` 항상 true, `js-render`·`static-markup`·`text-change` 항상 false). `evidence` = 근거(선언·속성 이름) 비어 있지 않은 문자열.
- 산출물(runtime, 배치마다 이 두 파일만): `tests/.tmp/axe-classify/occ-batch-{b}.json` = `{ "schemaVersion": 1, "batch": b, "occurrences": [ { "key", "scenario", "project", "ruleId", "target", "pair", "fixKind", "requiresColorChange", "evidence" } ] }`(배치 정렬 순서), `tests/.tmp/axe-classify/server-{b}.json`(서버 소유 기록). 같은 배치 안 같은 pair 판정이 다르면 occ-batch 파일을 쓰지 않고 `classification-inconsistent:{pair}` exit 1(재계획). baseline·plan은 만들지 않는다.

### R5.1 `OCC_RUN b` 공용 실행 절차 (step 2~15 동일)

- 명령: `W env OCC_BATCH=b node --input-type=module -`(stdin heredoc, 스크립트 파일 저장 금지). `W`(`tests/scripts/with-env.sh`)가 저장소 루트로 cd하고 `TMPDIR`·`npm_config_cache`·`PLAYWRIGHT_BROWSERS_PATH=tests/.pw-browsers`를 설정한다.
- import(저장소 근거: `tests/package.json` `"type": "module"`, devDependency `@playwright/test`, 설치 위치 `tests/node_modules/@playwright/test/index.js`·`index.mjs`; 저장소 루트에는 node_modules가 없어 bare import 불가): `chromium` = `createRequire(<ROOT>/tests/package.json)('@playwright/test').chromium`; `installProjectTheme` = `import(pathToFileURL(<ROOT>/tests/helpers/theme.js).href)`; `prepareForAxe` = `import(pathToFileURL(<ROOT>/tests/helpers/axe-prepare.js).href)`; project 설정 = `import(pathToFileURL(<ROOT>/tests/playwright.config.js).href)).default`. import 실패 → `occ-env: import-failed` exit 1(재계획; batch 1의 첫 실행이 일반 Node helper import 자가 검사).
- project 대응(현재 `tests/playwright.config.js` 고정값, config에서 읽고 대조, 불일치 → `occ-env: config-mismatch`): baseURL `http://127.0.0.1:4173`; webServer command `python3 -m http.server 4173 --bind 127.0.0.1`; projects 정확히 6개 `{mobile,tablet,desktop}-{dark,light}`, viewport mobile 375×812·tablet 768×1024·desktop 1280×800, colorScheme = 이름 접미사.
- 서버: probe `GET http://127.0.0.1:4173/index.html`(1000ms timeout). 200·본문 바이트 = 저장소 `index.html` → 재사용(child = null, 신호 없음). 응답이 있으나 다름 → `occ-env: port-foreign` exit 1(어떤 프로세스에도 신호 없음). 연결 실패 → `python3 -m http.server 4173 --bind 127.0.0.1` spawn(소유). `server-{b}.json` = `{pid, owned}`. readiness = 250ms 간격·최대 15000ms 같은 바이트 비교, 초과 → `occ-env: server-not-ready`.
- 정리(단일·멱등): `cleanup()`은 첫 호출에서 만든 Promise를 저장해 재호출 시 같은 Promise를 반환(이중 정리 없음). 내부 `try`: 열린 context 전부·browser close(오류는 로그만); `finally`: `stopOwned()`. `stopOwned()`: child(이 실행이 spawn한 서버)만 대상, 이미 exit면 반환; SIGTERM → exit 최대 5000ms 대기 → 미종료면 SIGKILL → exit 최대 5000ms 대기·확인 → 그래도 미종료면 `occ-env: server-kill-failed`(exit 1). 재사용·foreign 서버에는 신호를 보내지 않는다.
- 보호 구간: 서버 probe·spawn·`server-{b}.json` 기록·readiness·`chromium.launch`·occurrence 처리·`occ-batch-{b}.json` 기록 전부가 하나의 `try { … } catch { code = 1 } finally { await cleanup() }` 안에 있다. 종료 status: 성공 0, 오류 1, SIGINT 130, SIGTERM 143(신호 처리기는 같은 `cleanup()`을 기다린 뒤 고정 status로 exit).
- occurrence마다 순서(고정): `browser.newContext({ baseURL, viewport, colorScheme })` → `installProjectTheme(context, { project: { name: o.project } })` → `context.newPage()` → `page.goto('/')` → `prepareForAxe(page, { scenario: o.scenario })`(수집과 같이 projectIndex 미지정) → 대상 조사(쓰기 없음) → `context.close()`.
- 고정 골격(빌더는 `// 조사`·판정 부분만 작성):

```
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
const ROOT = process.cwd();
const B = Number(process.env.OCC_BATCH);
const BASE = 'http://127.0.0.1:4173';
const at = (p) => pathToFileURL(path.join(ROOT, p)).href;
const msg = (e) => String((e && e.message) || e);
let child = null;
let childExited = false;
let browser = null;
const contexts = new Set();
let cleaning = null;
async function waitExit(ms) {
  const until = Date.now() + ms;
  while (!childExited) {
    if (Date.now() >= until) return false;
    await new Promise((r) => setTimeout(r, 50));
  }
  return true;
}
async function stopOwned() {
  if (child === null || childExited) return;
  child.kill('SIGTERM');
  if (await waitExit(5000)) return;
  child.kill('SIGKILL');
  if (!(await waitExit(5000))) throw new Error('occ-env: server-kill-failed');
}
function cleanup() {
  if (cleaning === null) {
    cleaning = (async () => {
      try {
        for (const c of [...contexts]) await c.close().catch((e) => console.error(msg(e)));
        if (browser !== null) await browser.close();
      } catch (e) {
        console.error(msg(e));
      } finally {
        await stopOwned();
      }
    })();
  }
  return cleaning;
}
for (const [sig, status] of [['SIGINT', 130], ['SIGTERM', 143]]) {
  process.on(sig, () => {
    cleanup().catch((e) => console.error(msg(e))).finally(() => process.exit(status));
  });
}
const INDEX = fs.readFileSync(path.join(ROOT, 'index.html'));
async function probe() {
  try {
    const r = await fetch(BASE + '/index.html', { signal: AbortSignal.timeout(1000) });
    const body = Buffer.from(await r.arrayBuffer());
    return r.status === 200 && body.equals(INDEX) ? 'same' : 'foreign';
  } catch {
    return 'down';
  }
}
let code = 0;
try {
  let chromium, installProjectTheme, prepareForAxe, config;
  try {
    ({ chromium } = createRequire(path.join(ROOT, 'tests/package.json'))('@playwright/test'));
    ({ installProjectTheme } = await import(at('tests/helpers/theme.js')));
    ({ prepareForAxe } = await import(at('tests/helpers/axe-prepare.js')));
    config = (await import(at('tests/playwright.config.js'))).default;
  } catch (e) {
    console.error(msg(e));
    throw new Error('occ-env: import-failed');
  }
  const VP = { mobile: [375, 812], tablet: [768, 1024], desktop: [1280, 800] };
  const PROJ = {};
  for (const p of config.projects || []) {
    const [d, t] = p.name.split('-');
    const v = p.use && p.use.viewport;
    if (!VP[d] || !['dark', 'light'].includes(t) || !v || v.width !== VP[d][0] || v.height !== VP[d][1] || p.use.colorScheme !== t) throw new Error('occ-env: config-mismatch');
    PROJ[p.name] = { viewport: { width: v.width, height: v.height }, colorScheme: t };
  }
  if (Object.keys(PROJ).length !== 6 || config.use.baseURL !== BASE || config.webServer.command !== 'python3 -m http.server 4173 --bind 127.0.0.1') throw new Error('occ-env: config-mismatch');
  if (!(B >= 1 && B <= 14)) throw new Error('occ-env: batch');
  const cmp = (a, b) => (a < b ? -1 : a > b ? 1 : 0);
  const col = JSON.parse(fs.readFileSync(path.join(ROOT, 'tests/fixtures/axe-collected.json'), 'utf8'));
  const ALL = col.flatMap((e) => e.targets.map((t) => ({ key: e.key, scenario: e.scenario, project: e.project, ruleId: e.ruleId, target: t, pair: e.ruleId + '|' + t })));
  ALL.sort((x, y) => cmp(x.key, y.key) || cmp(x.target, y.target));
  const OCC = ALL.slice((B - 1) * 10, B * 10);
  fs.mkdirSync(path.join(ROOT, 'tests/.tmp/axe-classify'), { recursive: true });
  const SERVER_FILE = path.join(ROOT, `tests/.tmp/axe-classify/server-${B}.json`);
  const first = await probe();
  if (first === 'foreign') throw new Error('occ-env: port-foreign');
  if (first === 'down') {
    child = spawn('python3', ['-m', 'http.server', '4173', '--bind', '127.0.0.1'], { cwd: ROOT, stdio: 'ignore' });
    child.on('exit', () => { childExited = true; });
    child.on('error', () => { childExited = true; });
    fs.writeFileSync(SERVER_FILE, JSON.stringify({ pid: child.pid ?? null, owned: true }) + '\n');
    const until = Date.now() + 15000;
    while ((await probe()) !== 'same') {
      if (Date.now() >= until) throw new Error('occ-env: server-not-ready');
      await new Promise((r) => setTimeout(r, 250));
    }
  } else {
    fs.writeFileSync(SERVER_FILE, JSON.stringify({ pid: null, owned: false }) + '\n');
  }
  browser = await chromium.launch();
  const out = [];
  for (const o of OCC) {
    const pj = PROJ[o.project];
    if (!pj) throw new Error('occ-env: unknown-project:' + o.project);
    const context = await browser.newContext({ baseURL: BASE, viewport: pj.viewport, colorScheme: pj.colorScheme });
    contexts.add(context);
    try {
      await installProjectTheme(context, { project: { name: o.project } });
      const page = await context.newPage();
      await page.goto('/');
      await prepareForAxe(page, { scenario: o.scenario });
      // 조사(빌더 작성, 쓰기 없음) → { fixKind, requiresColorChange, evidence }
      // out.push({ ...o, fixKind, requiresColorChange, evidence });
    } finally {
      contexts.delete(context);
      await context.close();
    }
  }
  // 배치 내 같은 pair 판정 불일치 → throw new Error('classification-inconsistent:' + pair)
  // 일치 → occ-batch-{B}.json = { schemaVersion: 1, batch: B, occurrences: out } (2칸 들여쓰기·끝 개행 1)
} catch (e) {
  console.error(msg(e));
  code = 1;
} finally {
  try {
    await cleanup();
  } catch (e) {
    console.error(msg(e));
    code = 1;
  }
}
process.exit(code);
```

- `OCC_CHECK b` 블록:

```
import json, sys
b = int(sys.argv[1])
col = json.load(open('tests/fixtures/axe-collected.json', encoding='utf-8'))
occ = sorted(((e['key'], t, e) for e in col for t in e['targets']), key=lambda x: (x[0], x[1]))
if len(occ) != 139:
    sys.exit('occ-check: count')
want = occ[(b - 1) * 10:b * 10]
if not 1 <= b <= 14 or len(want) != (9 if b == 14 else 10):
    sys.exit('occ-check: batch-size')
d = json.load(open('tests/.tmp/axe-classify/occ-batch-%d.json' % b, encoding='utf-8'))
if not isinstance(d, dict) or set(d) != {'schemaVersion', 'batch', 'occurrences'} or d['schemaVersion'] != 1 or d['batch'] != b:
    sys.exit('occ-check: shape')
if [(o.get('key'), o.get('target')) for o in d['occurrences']] != [(k, t) for k, t, _ in want]:
    sys.exit('occ-check: members')
OF = {'key', 'scenario', 'project', 'ruleId', 'target', 'pair', 'fixKind', 'requiresColorChange', 'evidence'}
KINDS = ('css-token', 'css-rule', 'js-render', 'static-markup', 'text-change')
FIXED = {'css-token': True, 'js-render': False, 'static-markup': False, 'text-change': False}
seen = {}
for o, (k, t, e) in zip(d['occurrences'], want):
    tag = k + '|' + t
    if set(o) != OF:
        sys.exit('occ-check: occ-shape:' + tag)
    if (o['scenario'], o['project'], o['ruleId']) != (e['scenario'], e['project'], e['ruleId']) or o['pair'] != e['ruleId'] + '|' + t:
        sys.exit('occ-check: occ-context:' + tag)
    if o['fixKind'] not in KINDS or type(o['requiresColorChange']) is not bool:
        sys.exit('occ-check: occ-kind:' + tag)
    if o['fixKind'] in FIXED and FIXED[o['fixKind']] != o['requiresColorChange']:
        sys.exit('occ-check: occ-color:' + tag)
    if not isinstance(o['evidence'], str) or not o['evidence']:
        sys.exit('occ-check: occ-evidence:' + tag)
    v = (o['fixKind'], o['requiresColorChange'])
    if seen.setdefault(o['pair'], v) != v:
        sys.exit('classification-inconsistent:' + o['pair'])
print('occ-check %d: OK %d' % (b, len(want)))
```

## R6. pair 통합 (resume step 16)

- 입력 occ-batch-1~14(139 occurrence). 순회 순서(고정): batch 번호 1→14, 각 배치 `occurrences` 배열 순서. 배치를 넘는 pair까지 모든 occurrence 판정(`fixKind`, `requiresColorChange`) 일치 확인(불일치면 `classification-inconsistent:{pair}` 중단·재계획). 출력(runtime, 이 파일만): `tests/.tmp/axe-classify/pairs.json` = `{ "schemaVersion": 1, "pairs": [ { "pair", "ruleId", "target", "fixKind", "requiresColorChange", "evidence", "occurrenceCount" } ] }`(pair 코드 포인트 오름차순). `evidence` = 그 pair에 해당하는 occurrence의 evidence를 위 순회 순서대로 모은 목록 L에 대해 정확히 `'; '.join(L)`. 산정 12분.
- `INTEGRATE_CHECK` 블록:

```
import json, sys
col = json.load(open('tests/fixtures/axe-collected.json', encoding='utf-8'))
occ = {}
for e in col:
    for t in e['targets']:
        occ.setdefault(e['ruleId'] + '|' + t, []).append(e['key'])
rows = []
for b in range(1, 15):
    rows += json.load(open('tests/.tmp/axe-classify/occ-batch-%d.json' % b, encoding='utf-8'))['occurrences']
if len(rows) != 139 or len({(o['key'], o['target']) for o in rows}) != 139:
    sys.exit('integrate-check: count')
dec = {}
ev = {}
for o in rows:
    v = (o['fixKind'], o['requiresColorChange'])
    if dec.setdefault(o['pair'], v) != v:
        sys.exit('classification-inconsistent:' + o['pair'])
    ev.setdefault(o['pair'], []).append(o['evidence'])
if len(dec) != 25 or sorted(dec) != sorted(occ):
    sys.exit('integrate-check: pairs')
p = json.load(open('tests/.tmp/axe-classify/pairs.json', encoding='utf-8'))
if not isinstance(p, dict) or set(p) != {'schemaVersion', 'pairs'} or p['schemaVersion'] != 1:
    sys.exit('integrate-check: shape')
if [x.get('pair') for x in p['pairs']] != sorted(occ):
    sys.exit('integrate-check: order')
PF = {'pair', 'ruleId', 'target', 'fixKind', 'requiresColorChange', 'evidence', 'occurrenceCount'}
for x in p['pairs']:
    k = x['pair']
    r, t = k.split('|', 1)
    if set(x) != PF or x['ruleId'] != r or x['target'] != t:
        sys.exit('integrate-check: pair-shape:' + k)
    if (x['fixKind'], x['requiresColorChange']) != dec[k] or x['occurrenceCount'] != len(occ[k]) or len(ev[k]) != len(occ[k]):
        sys.exit('integrate-check: pair-mismatch:' + k)
    if not isinstance(x['evidence'], str) or x['evidence'] != '; '.join(ev[k]):
        sys.exit('integrate-check: pair-evidence:' + k)
print('integrate-check: OK 25 139')
```

## R7. merge (resume step 17)

- 입력 pairs.json. 출력(tracked, 이 step만): `tests/fixtures/axe-baseline.json`(원 §6.4: collected entry마다, fixes는 targets 순서 1:1, 각 fix `fixKind`·`requiresColorChange` = 그 pair 결정, fixFiles = `FIX_FILES_BY_KIND`, entry fixFiles 합집합), `tests/fixtures/axe-remediation-plan.json`(원 §6.5: PlanTarget·id 정렬, coverage 완전, 각 그룹 R = `requiredBlockReason(targets, baseline)`; R ≠ `""`면 blocked true·reason R, 아니면 false·`""`, manual block 금지, estMinutes 1~20). blocked 그룹이 있거나 executable 실패면 원 §6.2 remediation 재계획 경로로 중단.
- `MERGE_CHECK` 블록:

```
import json, sys
col = json.load(open('tests/fixtures/axe-collected.json', encoding='utf-8'))
dec = {x['pair']: x for x in json.load(open('tests/.tmp/axe-classify/pairs.json', encoding='utf-8'))['pairs']}
if len(dec) != 25 or sum(x['occurrenceCount'] for x in dec.values()) != 139:
    sys.exit('merge-check: count')
base = {e['key']: e for e in json.load(open('tests/fixtures/axe-baseline.json', encoding='utf-8'))}
if sorted(base) != sorted(e['key'] for e in col):
    sys.exit('merge-check: keys')
n = 0
for e in col:
    for f in base[e['key']]['fixes']:
        d = dec[e['ruleId'] + '|' + f['target']]
        if (f['fixKind'], f['requiresColorChange']) != (d['fixKind'], d['requiresColorChange']):
            sys.exit('merge-check: mismatch:' + e['key'] + '|' + f['target'])
        n += 1
if n != 139:
    sys.exit('merge-check: occurrences')
print('merge-check: OK 25 139')
```

## R8. 변경형 step (resume 31 gate · 32 recheck · 33 finalize)

- no-op 규칙 제외. 작업 순서(고정): `RSNAP` → 쓰기 없는 사전 검사(`COLLECT_CHAIN --out tests/.tmp/axe-current.json`, `REGRESSION_GATE`; 회귀 실패면 tracked 불변 중단) → `SHA_SAVE <대상> <tag>` → 작업 부분에서만 변경 명령(31·32 `AXE --prune-plan --collected tests/.tmp/axe-current.json`, 33 baseline `[]` 기록) → `SHA_DIFF <대상> <tag> <label>`(로그 `plan-pruned: changed|unchanged` 또는 `baseline-finalized: changed|unchanged`, no-op 선언 없음) → AC(쓰기 없는 검증 → `FULL` → `VS` → `RGATE`).
- `--prune-plan`은 AC나 사전 probe에서 실행하지 않는다. 재계획 `axe-remediation-{id}`는 resume 31과 32 사이.

## R9. step 대응 (원 step N(41~57) = resume step N−23)

| resume | name | 원 | 분 |
|---|---|---|---|
| 0 | verify-scope-resume-compat | — | 18 |
| 1 | resume-preflight | — | 15 |
| 2~14 | axe-classify-occ-batch-1~13 | 40 분할(각 10 occurrence) | 20 |
| 15 | axe-classify-occ-batch-14 | 40 분할(9 occurrence) | 19 |
| 16 | axe-classify-pair-integrate | 40 분할 | 12 |
| 17 | axe-classify-merge | 40 분할 | 18 |
| 18 | featured-projects | 41 | 19 |
| 19 | hero-first-screen | 42 | 20 |
| 20 | hero-two-column | 43 | 19 |
| 21 | section-structure | 44 | 19 |
| 22 | section-layout | 45 | 17 |
| 23 | component-hit-open | 46 | 19 |
| 24 | state-sequence | 47 | 18 |
| 25 | state-colors-fixture | 48 | 19 |
| 26 | component-hover-active | 49 | 16 |
| 27 | component-clamp-stripe | 50 | 15 |
| 28 | focus-trap-modal | 51 | 17 |
| 29 | focus-trap-lightbox | 52 | 17 |
| 30 | print-pdf | 53 | 17 |
| 31 | axe-remediation-gate | 54 | 18 |
| (재계획) | axe-remediation-{id} | 54~55 사이 | ≤20 |
| 32 | axe-remediation-recheck | 55 | 18 |
| 33 | axe-finalize | 56 | 16 |
| 34 | final-verification | 57 | 17 |

- 원 설계 step 번호 상호참조: §9 `index.html` 구조 변경 step 41·42·44 → resume 18·19·21, 예외 (a)·(b) step 44 → resume 21, §11.2 step 46~50 → resume 23~27, 원 step 54와 55 사이 재계획 → resume 31과 32 사이. 선행 = 작은 번호 전부(32는 재계획 그룹 포함).

## R10. 기존 산출물 분기 RGATE (resume step 20·23·24·25·26·27)

- 근거: start snapshot `tests/.tmp/start-snapshot-step{100+k}.json`의 `files` 맵(경로 → sha256 또는 null)만 사용. 별도 hash 저장 없음. snapshot 재생성·수정·삭제 금지(O_EXCL 생성·identity 재사용으로 step 중 불변).
- 조건: R 경로 전부 null 또는 맵에 없음 → `new`(RGATE에 `--require-absent <R>`, 생성 후 검증); 전부 sha256 있음 → `existing`(`--require-absent` 생략, 현재 sha256 = snapshot 값 확인); 일부만 → `rbranch: branch-mixed` 중단.
- existing 분기 절차: 작업 생략 → 쓰기 없는 AC 전체 실행(`RGATE_B` 포함) → 모두 통과할 때만 `resume step{k}: no-op`. AC 실패나 `rbranch: existing-changed:{path}`면 tracked 불변 중단·재계획(기존 산출물 수정 금지).
- 적용(R 경로): 20 `tests/specs/hero-layout.spec.js`; 23 `tests/helpers/component-state.js,tests/specs/component-hit.spec.js`; 24 `tests/helpers/state-sequence.js,tests/specs/state-sequence.spec.js`; 25 `tests/scripts/make-state-colors.mjs,tests/fixtures/component-state-colors.json,tests/specs/state-colors.spec.js`; 26 `tests/specs/component-hover.spec.js`; 27 `tests/specs/component-clamp.spec.js`.
- §R10 블록(`RBRANCH`는 A=`--probe`로 분기 로그만, `RGATE_B`는 분기에 맞춰 RGATE 실행):

```
import hashlib, json, os, subprocess, sys
k, A = int(sys.argv[1]), sys.argv[2]
R = [p for p in sys.argv[3].split(',') if p]
if not R:
    sys.exit('rbranch: bad-args')
snap = 'tests/.tmp/start-snapshot-step%d.json' % (100 + k)
files = json.load(open(snap, encoding='utf-8'))['files']
have = [files.get(p) is not None for p in R]
if any(have) and not all(have):
    sys.exit('rbranch: branch-mixed:' + ','.join(p for p, h in zip(R, have) if h))
if all(have):
    for p in R:
        if not os.path.isfile(p) or os.path.islink(p) or hashlib.sha256(open(p, 'rb').read()).hexdigest() != files[p]:
            sys.exit('rbranch: existing-changed:' + p)
    branch = 'existing'
else:
    branch = 'new'
print('rbranch step%d: %s' % (100 + k, branch))
if A == '--probe':
    sys.exit(0)
cmd = ['sh', 'tests/scripts/with-env.sh', 'node', 'tests/scripts/scope-snapshot.mjs', '--check', snap, '--allow', A]
if branch == 'new':
    cmd += ['--require-absent', ','.join(R)]
sys.exit(subprocess.run(cmd).returncode)
```

## R11. 필수 산출물 존재 검사 `REQ` (resume step 18·19·21·22·28·29·30·34)

- 목적: `T`의 spec 인자는 Playwright 필터라 전용 spec이 없어도 guard spec만 실행돼 통과할 수 있다(거짓 no-op). `REQ`가 no-op 첫 probe이자 AC 첫 명령으로 전용 산출물의 존재·형식을 강제한다. 내용 검사(`T` 목록·`GS`)와 범위 gate(`RGATE`)는 그대로.
- 판정: 경로마다 `os.lstat` → 없음(`OSError`) `required-artifact-missing:{path}`, 일반 파일 아님(symlink 포함, `S_ISREG` 거짓) `required-artifact-not-regular:{path}`, 첫 실패에서 exit 1. 통과 `required-artifacts step{100+k}: OK {n}`. 쓰기 없음.
- 적용(exact P):
  - 18 `tests/specs/featured.spec.js,index.html,js/data.js,js/main.js,css/style.css`
  - 19 `tests/specs/hero.spec.js,index.html,js/main.js,css/style.css`
  - 21 `tests/specs/structure.spec.js,index.html,js/main.js`
  - 22 `tests/specs/layout.spec.js,css/style.css`
  - 28 `tests/specs/focus-modal.spec.js,js/main.js`
  - 29 `tests/specs/focus-lightbox.spec.js,tests/specs/focus-modal.spec.js,js/main.js,css/style.css`
  - 30 `tests/specs/print.spec.js,css/style.css`
  - 34 `tests/specs/screenshots.spec.js,tests/specs/design-intake.spec.js,tests/specs/hero-layout.spec.js,tests/specs/component-hit.spec.js,tests/specs/state-sequence.spec.js,tests/specs/state-colors.spec.js,tests/specs/component-hover.spec.js,tests/specs/verify-scope-resume.spec.js,tests/helpers/component-state.js,tests/helpers/state-sequence.js,tests/scripts/make-state-colors.mjs,tests/fixtures/component-state-colors.json`
- `REQ` FAIL → no-op 불가, 허용 경로 안 원 승인 작업 후 완전한 AC 재실행. 없는 경로가 그 step 허용 경로 밖(예: 29의 `focus-modal.spec.js`, 34의 helper·fixture)이면 원인 step 보고·중단.
- §R11 블록:

```
import os, stat, sys
k = int(sys.argv[1])
P = [p for p in sys.argv[2].split(',') if p]
if not P:
    sys.exit('required-artifacts: bad-args')
for p in P:
    try:
        st = os.lstat(p)
    except OSError:
        sys.exit('required-artifact-missing:' + p)
    if not stat.S_ISREG(st.st_mode):
        sys.exit('required-artifact-not-regular:' + p)
print('required-artifacts step%d: OK %d' % (100 + k, len(P)))
```
