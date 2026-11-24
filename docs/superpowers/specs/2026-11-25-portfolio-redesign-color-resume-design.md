# HOO-81 color-resume 설계 (representative v52 색 결정 · v56 필수 범위 · v57 direct worktree 실행)

- phase: `HOO-81-portfolio-redesign-color-resume` (step 0~4). 원 설계 `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md`(§n), resume 설계 `docs/superpowers/specs/2026-11-24-portfolio-redesign-resume-design.md`(§R n)는 유효하며 수정 금지. 이 문서 절은 `§C n`.
- 결정: 대표 `representative-color-scope-v52`(color-contrast 위반은 기존 token을 쓴 최소 색 변경으로 수정 허용), `final-required-scope-parallel-v56`(resume 18~30 필수 범위, 병렬 wave), `executable-direct-worktree-v57`(Harness 2.0.1은 linked worktree를 project root로 거부하고 parallel runner가 없음 → direct Claude worktree worker + canonical Harness 검증). v55의 범위 제외 문구는 철회됐다.
- BASE_HEAD(불변): `aa6f37c803ffaf8712418e94971ed4567e2a390d`(`chore(HOO-81): record color scope blocker`). 이력 commit: `1d5d27b0377ef575b9e54d79b7f8178e9af3daad`(원 phase 마지막 구현), `dce163d89666acdd30a49705ebc4e93c6dba4636`(resume 마지막 성공 출력).
- 승계(재실행 없음): 원 phase step 0~39 completed·40 blocked, resume phase step 0~16 completed·17 blocked(`color change excluded`). 분류 evidence: `tests/.tmp/axe-classify/pairs.json` sha256 `1ba8778ab6cc9254b4404a5349f53c4463c0c55e4a1b2b447eac02a8bd8acaa1`, `tests/fixtures/axe-collected.json` sha256 `ff7c76a6214034251f5ebc028706b9ae383ec6ecb9ce8a4c3ed97e266672e63c`(color-contrast 12 pair/61 occurrence css-rule·색 변경 필요, nested-interactive 13 pair/78 occurrence js-render). 이 두 파일은 이력 seed로만 보존하고, wave 2 final collect가 정본이다.
- 보존: 텍스트·숫자·서체 asset·weight, 정보 구조 6개 섹션, PROJECTS 13개·순서, 이미지·아이콘, 완료된 레이아웃·컴포넌트·간격·타이포. 팔레트 재설계·장식 색 변경·새 color token·리터럴 색·`css/themes.css` 변경 금지.
- §C FLOW: materialize → plan-only commit → GPT-6 Astra 리뷰 1회(확인된 major/blocker만 교정, 비차단은 HOO-107) → 새 대표 exact 승인 → Harness step 0 → coordinator wave 1 → Harness step 1 → Harness step 2 → coordinator wave 2 → Harness step 3 → Harness step 4 → exact-commit Astra CLEAN → feature push → OPEN PR → tested = reviewed = pushed = PR-head SHA. 진행 보고는 시작·fan-out·실패/재시도·통합·최종 검증·완료 때만.

## C1. 불변·금지

- 원 §9 공통 금지와 resume §R1 유지. 원 phase·resume phase 디렉터리, 원·resume 설계, `CLAUDE.md`, `tests/fixtures/axe-collected.json`은 읽기만.
- `git reset/restore/checkout/clean`, 광범위 삭제, main 직접 변경, merge, cherry-pick, deploy, runner·worker push 금지. Harness linked worktree 우회·Harness 내부 함수 호출 금지.
- 허용 git 쓰기: Harness runner의 step commit, coordinator의 `git worktree add`·lane local commit·canonical 결정적 `git apply --index`+integration commit·검증된 lane의 exact `git worktree remove <path>`·exact local branch 삭제. worker는 git 쓰기 없음.
- 각 Harness step 30분 이하. Harness step은 background worker를 기다리지 않는다.

## C2. 약어 (원 §8.5·resume §R2에 추가)

- `XSNAP k` = `python3 -I tests/scripts/start-snapshot.py step{200+k}`; `XGATE k <A> [<R>]` = `W node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step{200+k}.json --allow <A> [--require-absent <R>]`.
- `PREFLIGHT` = `python3 -I - <<'PY'` + §C3 블록 + `PY`; `WAVE_CHECK w` = `python3 -I - w <<'PY'` + §C6 블록 + `PY`.
- `W`·`T`·`FULL`·`VS`·`DI`·`GS`·`AXE`·`COLLECT_CHAIN`·`REGRESSION_GATE`는 원 §8.5 그대로. `REQ`·`RBRANCH`·`RGATE_B`는 resume §R10·§R11 블록을 worker가 lane 안에서 판정 용도로만 사용(snapshot 대신 lane base 기준).
- W1_FILES(wave 1 허용 파일, resume step18~30 허용 파일 합집합): `index.html`, `js/data.js`, `js/main.js`, `css/style.css`, `tests/specs/featured.spec.js`, `tests/specs/hero.spec.js`, `tests/specs/hero-layout.spec.js`, `tests/specs/structure.spec.js`, `tests/specs/layout.spec.js`, `tests/specs/component-hit.spec.js`, `tests/specs/state-sequence.spec.js`, `tests/specs/state-colors.spec.js`, `tests/specs/component-hover.spec.js`, `tests/specs/component-clamp.spec.js`, `tests/specs/focus-modal.spec.js`, `tests/specs/focus-lightbox.spec.js`, `tests/specs/print.spec.js`, `tests/helpers/component-state.js`, `tests/helpers/state-sequence.js`, `tests/scripts/make-state-colors.mjs`, `tests/fixtures/component-state-colors.json`.
- W1_SPECS = 위 `tests/specs/*` 13개 이름(`featured.spec.js` … `print.spec.js`).

## C3. step 0 preflight 블록

```
import hashlib, json, os, subprocess, sys
BASE_HEAD = 'aa6f37c803ffaf8712418e94971ed4567e2a390d'
HIST = ('1d5d27b0377ef575b9e54d79b7f8178e9af3daad', 'dce163d89666acdd30a49705ebc4e93c6dba4636')
PLAN = ('docs/superpowers/specs/2026-11-25-portfolio-redesign-color-resume-design.md', 'tests/scripts/verify-scope.mjs', 'tests/specs/verify-scope-resume.spec.js', 'tests/playwright.config.js', 'tests/specs/smoke.spec.js')
PROTECTED = ('phases/HOO-81-portfolio-redesign/', 'phases/HOO-81-portfolio-redesign-resume/', 'docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md', 'docs/superpowers/specs/2026-11-24-portfolio-redesign-resume-design.md', 'CLAUDE.md', 'tests/fixtures/axe-collected.json')
HASH = {'tests/.tmp/axe-classify/pairs.json': '1ba8778ab6cc9254b4404a5349f53c4463c0c55e4a1b2b447eac02a8bd8acaa1', 'tests/fixtures/axe-collected.json': 'ff7c76a6214034251f5ebc028706b9ae383ec6ecb9ce8a4c3ed97e266672e63c'}
def git(*a):
    return subprocess.run(['git', *a], check=True, capture_output=True).stdout.decode()
def names(*a):
    return [p for p in git(*a).split('\n') if p]
hist = git('log', '--format=%H', 'HEAD').split()
for c in (BASE_HEAD,) + HIST:
    if c not in hist:
        sys.exit('preflight: not-ancestor:' + c)
extra = [p for p in names('diff', '--no-renames', '--name-only', BASE_HEAD, 'HEAD') if p not in PLAN and not p.startswith('phases/HOO-81-portfolio-redesign-color-resume/')]
if extra:
    sys.exit('preflight: unexpected-commit-paths:' + ','.join(extra))
LAYERS = (
    ('commit', ('diff', '--no-renames', '--name-only', BASE_HEAD, 'HEAD', '--') + PROTECTED),
    ('index', ('diff', '--cached', '--no-renames', '--name-only', 'HEAD', '--') + PROTECTED),
    ('worktree', ('diff', '--no-renames', '--name-only', '--') + PROTECTED),
    ('untracked', ('ls-files', '--others', '--exclude-standard', '--', PROTECTED[0], PROTECTED[1])),
)
for layer, args in LAYERS:
    hit = names(*args)
    if hit:
        sys.exit('preflight: protected-changed:' + layer + ':' + ','.join(hit))
for p, h in HASH.items():
    if not os.path.isfile(p) or os.path.islink(p) or hashlib.sha256(open(p, 'rb').read()).hexdigest() != h:
        sys.exit('preflight: hash:' + p)
o = {s['step']: s for s in json.loads(git('show', BASE_HEAD + ':phases/HOO-81-portfolio-redesign/index.json'))['steps']}
if any(o[n]['status'] != 'completed' for n in range(40)) or o[40]['status'] != 'blocked':
    sys.exit('preflight: original-phase-state')
r = {s['step']: s for s in json.loads(git('show', BASE_HEAD + ':phases/HOO-81-portfolio-redesign-resume/index.json'))['steps']}
if any(r[n]['status'] != 'completed' for n in range(17)) or r[17]['status'] != 'blocked' or 'color change excluded' not in r[17].get('blocked_reason', ''):
    sys.exit('preflight: resume-phase-state')
need = ['tests/package.json', 'tests/playwright.config.js', 'tests/node_modules/@playwright/test/index.js', 'tests/scripts/with-env.sh', 'tests/scripts/start-snapshot.py', 'tests/scripts/scope-snapshot.mjs', 'tests/scripts/verify-scope.mjs', 'tests/helpers/axe.js', 'tests/helpers/axe-prepare.js', 'tests/helpers/theme.js', 'tests/helpers/design-guard.js', 'tests/helpers/design-guard-color-rules.js', 'tests/specs/design-guard-color-rules.spec.js', 'tests/specs/axe.spec.js', 'tests/specs/smoke.spec.js', 'tests/specs/verify-scope-resume.spec.js'] + ['phases/HOO-81-portfolio-redesign-resume/step%d.md' % n for n in range(18, 31)]
miss = [p for p in need if not os.path.isfile(p) or os.path.islink(p)]
if miss:
    sys.exit('preflight: missing:' + ','.join(miss))
late = [p for p in ('tests/fixtures/axe-baseline.json', 'tests/fixtures/axe-remediation-plan.json') if os.path.lexists(p)]
if late:
    sys.exit('preflight: classify-output-exists:' + ','.join(late))
print('color-resume-preflight: OK')
```

## C4. coordinator 실행 절차 (Ryan/Hermes, Harness 밖)

- 전제(실행 전, 불성립이면 실행 전 blocker 보고): `claude --help`에서 `-p`, `--permission-mode`, `--allowedTools`, `--max-turns`, `--add-dir`, project hooks를 로드하지 않는 설정 옵션(예: `--setting-sources user`)이 실제로 존재·동작함을 확인. `--bare`·OpenRouter·`--dangerously-skip-permissions` 사용 금지.
- 경로: `SCR=/Users/hoon/.hermes/profiles/ryan/cache/scratch/HOO-81-parallel-<run>`, lane worktree `$SCR/lane-<id>`, evidence `$SCR/evidence/lane-<id>/`, 외부 record `$SCR/record-wave-<w>.json`. local branch `hoo81-<run>-w<w>-lane-<id>`(push 없음).
- worktree 생성: canonical에서 `git worktree add -b <branch> $SCR/lane-<id> <BASE>`. 생성 직후 lane worktree에만 symlink 2개 `tests/node_modules` → canonical `tests/node_modules`, `tests/.pw-browsers` → canonical `tests/.pw-browsers`(ignore 경로, patch 포함 금지, 읽기 전용 사용).
- port: wave 1 lane P 4174, A 4175, B 4176, C 4177, D 4178, E 4179; wave 2 shard 1~5 = 4180~4184. worker는 `PW_PORT=<port>`로만 테스트 실행.
- worker 명령: `cd $SCR/lane-<id> && PW_PORT=<port> claude -p "$(cat $SCR/evidence/lane-<id>/prompt.md)" <hooks 미로드 설정> --permission-mode acceptEdits --add-dir $SCR/evidence/lane-<id> --max-turns 200 --allowedTools '<Read,Glob,Grep,Edit,Write, 원 §8.5 T·GS·DI 명령 prefix와 W node tests/scripts/make-state-colors.mjs prefix의 Bash 패턴, Bash(git diff:*), Bash(git status:*)>' --output-format json > $SCR/evidence/lane-<id>/result.json 2> $SCR/evidence/lane-<id>/stderr.log &` — PID 기록.
- prompt 고정 내용: 프로젝트 `CLAUDE.md` 전문, 원 설계 §9·§11.3 금지, 승계 step 파일 전문(wave 1: `phases/HOO-81-portfolio-redesign-resume/step{N}.md`, wave 2: 해당 shard manifest), exact 허용 파일·anchor, lane 내부 step 순서, focused test 명령, 금지(git 쓰기·phase/index/docs/shared fixture/canonical 수정·네트워크 설치·다른 lane 경로), step마다 `$SCR/evidence/lane-<id>/checkpoint-<step>.json` = `{lane, step, at, focused:[{cmd, exit}], result}` 기록.
- 감시: 20분 동안 새 checkpoint가 없으면 그 lane의 기록된 PID만 종료하고 같은 base에서 1회 재시도(worktree·branch 새 이름), 재실패면 그 lane만 block·보존. 성공 lane은 보존.
- lane 검증·commit: worker 종료 후 coordinator가 `git -C <wt> status --porcelain`·diff 파일 ⊆ lane 허용 파일·anchor 범위(승계 step 파일 허용 서술) 확인, lane focused test 결과 exit 0 확인 → `git -C <wt> add <exact files>` → lane local commit.
- fan-in: lane patch = `git diff --binary --no-renames <BASE> <laneCommit>`. 파일별 hunk 범위(BASE 줄 기준) 교집합 없음 + semantic anchor(CSS selector·declaration, JS function, HTML 요소 id) 중복 없음 확인. 같은 파일의 disjoint hunk 허용. 겹치면 fail-closed, 그 두 lane만 직렬 재실행(앞 lane 통합 결과를 base로). 통과하면 canonical에서 고정 순서로 `git apply --index --check` → `git apply --index`, 적용 후 각 파일 sha256을 lane 결과 합성 기대값과 비교 → integration commit. merge·cherry-pick 금지.
- record: canonical 런타임 `tests/.tmp/parallel/wave-<w>.json`(§C6 스키마)과 외부 record 동일 내용. cleanup: integration commit과 bytes 검증이 끝난 lane만 exact `git worktree remove $SCR/lane-<id>`와 exact `git branch -D <branch>`, 실패·불명 lane은 보존(`cleanup: kept`).

## C5. wave 정의

- wave 1(design): waveBase = Harness step 0 출력 commit 뒤 canonical HEAD. prologue lane P = resume step 18 → 검증·적용·commit = PARALLEL_BASE. 이어 PARALLEL_BASE에서 동시 실행: A 19→20, B 21→22, C 23→24→25→26→27, D 28→29, E 30(lane 내부 직렬, step마다 그 step 파일의 AC 중 `FULL`·`VS`·`RGATE`·`RGATE_B`·`XGATE`를 뺀 focused 부분(`REQ`·`RBRANCH`·`DI`·`T`·`GS`·`make-state-colors --check`) 실행 후 checkpoint). import 순서 A→B→C→D→E.
- wave 2(a11y): Harness step 2가 만든 `tests/.tmp/a11y-wave/components.json`의 shard(최대 5)마다 lane 1개, PARALLEL_BASE = step 2 출력 commit. worker는 shard의 exact anchor·planned change만 적용하고 focused check(`COLLECT_CHAIN --out tests/.tmp/axe-shard.json` 후 shard target 부재·새 위반 없음, nested shard는 `T modal-regression.spec.js featured.spec.js focus-modal.spec.js focus-lightbox.spec.js component-hit.spec.js`) 1회. import 순서 = shard id 오름차순.

## C6. `WAVE_CHECK w` 블록

```
import hashlib, json, os, subprocess, sys
w = int(sys.argv[1])
PHASE = 'HOO-81-portfolio-redesign-color-resume'
SCR = '/Users/hoon/.hermes/profiles/ryan/cache/scratch/HOO-81-parallel-'
W1 = {'index.html', 'js/data.js', 'js/main.js', 'css/style.css', 'tests/specs/featured.spec.js', 'tests/specs/hero.spec.js', 'tests/specs/hero-layout.spec.js', 'tests/specs/structure.spec.js', 'tests/specs/layout.spec.js', 'tests/specs/component-hit.spec.js', 'tests/specs/state-sequence.spec.js', 'tests/specs/state-colors.spec.js', 'tests/specs/component-hover.spec.js', 'tests/specs/component-clamp.spec.js', 'tests/specs/focus-modal.spec.js', 'tests/specs/focus-lightbox.spec.js', 'tests/specs/print.spec.js', 'tests/helpers/component-state.js', 'tests/helpers/state-sequence.js', 'tests/scripts/make-state-colors.mjs', 'tests/fixtures/component-state-colors.json'}
W1_LANES = [('P', [18]), ('A', [19, 20]), ('B', [21, 22]), ('C', [23, 24, 25, 26, 27]), ('D', [28, 29]), ('E', [30])]
def git(*a):
    return subprocess.run(['git', *a], check=True, capture_output=True).stdout
def sha(b):
    return hashlib.sha256(b).hexdigest()
p = 'tests/.tmp/parallel/wave-%d.json' % w
if not os.path.isfile(p) or os.path.islink(p):
    sys.exit('wave-record-missing:' + p)
r = json.load(open(p, encoding='utf-8'))
K = {'schemaVersion', 'wave', 'phase', 'externalRecord', 'externalRecordSha256', 'waveBase', 'parallelBase', 'integrationCommit', 'combinedDiffSha256', 'importOrder', 'lanes'}
if not isinstance(r, dict) or set(r) != K or r['schemaVersion'] != 1 or r['wave'] != w or r['phase'] != PHASE:
    sys.exit('wave-check: shape')
ext = r['externalRecord']
if not ext.startswith(SCR) or not os.path.isfile(ext) or sha(open(ext, 'rb').read()) != r['externalRecordSha256'] or json.load(open(ext, encoding='utf-8')) != r:
    sys.exit('wave-check: external-record')
head = git('rev-parse', 'HEAD').decode().strip()
if r['integrationCommit'] != head:
    sys.exit('wave-check: head')
hist = git('log', '--format=%H', 'HEAD').decode().split()
if r['waveBase'] not in hist or r['parallelBase'] not in hist:
    sys.exit('wave-check: ancestry')
if sha(git('diff', '--binary', '--no-renames', r['waveBase'], head)) != r['combinedDiffSha256']:
    sys.exit('wave-check: combined-diff')
files = set(p for p in git('diff', '--no-renames', '--name-only', r['waveBase'], head).decode().split('\n') if p)
if w == 1:
    allowed, lanes = W1, W1_LANES
else:
    m = json.load(open('tests/.tmp/a11y-wave/components.json', encoding='utf-8'))
    allowed = set(f for s in m['shards'] for f in s['files'])
    lanes = [(s['id'], []) for s in m['shards']]
if files - allowed:
    sys.exit('wave-check: files-outside:' + ','.join(sorted(files - allowed)))
LK = {'id', 'steps', 'worktree', 'branch', 'baseSha', 'pid', 'sessionId', 'port', 'laneCommit', 'diffSha256', 'files', 'focusedTests', 'checkpoints', 'result', 'cleanup'}
if [(x.get('id'), x.get('steps')) for x in r['lanes']] != lanes:
    sys.exit('wave-check: lanes')
for x in r['lanes']:
    if set(x) != LK or x['result'] != 'pass' or x['cleanup'] not in ('removed', 'kept') or not x['worktree'].startswith(SCR) or not set(x['files']) <= allowed:
        sys.exit('wave-check: lane:' + str(x.get('id')))
    if not x['focusedTests'] or any(t.get('exit') != 0 for t in x['focusedTests']):
        sys.exit('wave-check: focused:' + x['id'])
    if [c.get('step') for c in x['checkpoints']] != x['steps'] or any(c.get('result') != 'pass' for c in x['checkpoints']):
        sys.exit('wave-check: checkpoints:' + x['id'])
if r['importOrder'] != [i for i, _ in lanes if not (w == 1 and i == 'P')]:
    sys.exit('wave-check: import-order')
print('wave-check %d: OK %d lanes' % (w, len(r['lanes'])))
```

- wave 2에서 `steps`는 `[]`, `checkpoints`도 `[]`(focused 1회만)로 기록한다.

## C7. 색 변경 범위 (step 2)

- 대상: final collect의 color-contrast target만. 색 출처 선언은 `css/style.css` 기존 선언(예: `.stat-label`·`.about-meta dt`·`.footer-inner`의 `color: var(--text-faint)`, `.btn-primary`·`.brand-mark`·`.about-avatar`의 강조색 위 전경색). 후보 = 기존 color token `var(--x)`, 6 project 모두 axe 통과·양 테마 base 계산색과 sRGB 거리 합 최소·동률이면 token 이름 코드 포인트 순. 해결 불가면 `color-scope-themes-required:{target}` 중단(themes.css는 재계획·재리뷰 없이 다루지 않음).
- design guard 예외: `tests/helpers/design-guard-color-rules.js`에 상수 `HOO81_COLOR_V52_ALLOW` 1개(decision `representative-color-scope-v52`, 항목 `{file: 'css/style.css', selectors, prop, base, to}` 정렬). 그 정확한 위치에서 값이 `base` 그대로이거나 정확히 `to`일 때만 색 규칙 위반에서 제외. 그 밖 판정 불변. `tests/specs/design-guard-color-rules.spec.js`에 회귀 1개(목록 밖 위치·목록 위치의 다른 값은 여전히 위반, 목록 위치의 `to`는 통과).
- `tests/specs/component-hover.spec.js`는 같은 상수를 import해 해당 (selector, prop)에 대응하는 측정 id·prop만 BASE fixture 색 비교에서 제외한다(그 밖 비교 불변).
- nested-interactive: `js/main.js` project-card 렌더(현재 `role="button" tabindex="0"` article 안 `button.project-more`)와 위임 처리 anchor. 승인된 기존 spec(modal·featured·focus·hit)을 바꿔야만 해결되면 중단·보고.
- 다른 rule이 나오면 그 rule만 `a11y: out-of-scope-rule:{ruleId}` blocker 보고, 임의 수정 금지.
- manifest `tests/.tmp/a11y-wave/components.json` = `{schemaVersion: 1, collectedSha256, rules, shards: [{id: 's1'…, files, anchors, targets: [{key, target}], changes: [{file, selectors, prop, base, to}]}]}`; shard = edit anchor 연결 성분, 5개 초과면 anchor 첫 등장 순으로 인접 성분 병합해 5개 이하.
