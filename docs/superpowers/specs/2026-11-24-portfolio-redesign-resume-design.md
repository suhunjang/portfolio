# HOO-81 resume 설계 보완 (runtime-replan v47 · base-fix v48 · astra-findings v49)

- 원 설계(유효, 수정 금지): `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md`(compact v46). `§n`은 원 설계 절, `§R n`은 이 문서 절.
- 원 phase `HOO-81-portfolio-redesign`: step 0~39 completed, step 40 `axe-classify` blocked(이력 evidence, 읽기만). resume phase `HOO-81-portfolio-redesign-resume`: step 0~32.
- resume BASE_HEAD(불변): `4b2ec3b325f400edefca0fbcfb8ff83bf739ff89`(`chore(HOO-81): record step 40 runtime blocker`, metadata-only). 마지막 완료 구현 commit(이력): `1d5d27b0377ef575b9e54d79b7f8178e9af3daad`.
- blocker(불변): `tests/fixtures/axe-collected.json` = entry 12 / occurrence 139(color-contrast 61, nested-interactive 78) / 서로 다른 `ruleId|canonical target` pair 25. 원 §6.2 산정 147분 > 20 → step 40 blocked. 원 step 0~39 재실행·step 40 재설정·blocker evidence 편집 금지.
- 리뷰 반영: Astra record `b0a51811c7c6612b4804c04d642eb342029258fe04b86ebc8971bc21c0a9e4da`(major 3: verify-scope 호환 준비 step, occurrence 기반 분류 배치+통합 step, prune step의 no-op 규칙 제외).
- 원 승인·리뷰 재사용 없음. §ID·§G·§8.5 약어·§6.4/§6.5·§11·§THEME는 원 설계 참조.
- §R FLOW: materialize → 현재 브랜치 plan-only commit → Astra `gpt-6-astra` CLEAN → 새 대표 exact 승인 → resume phase만 fresh runner(step 0~32) → 전체 검증 → exact-commit 리뷰 CLEAN → feature push → OPEN PR → tested·reviewed·pushed·PR head SHA 동일 확인. merge·deploy·main 직접 변경 없음.

## R1. 불변·금지

- 원 §9 공통 금지 전부 유지. 추가: 기존 구현 commit·artifact·runtime snapshot(`tests/.tmp/start-snapshot-step0..40*`) 보존, `git reset/restore/checkout/clean`·광범위 삭제·push 금지, 원 phase `phases/HOO-81-portfolio-redesign/**`와 원 설계·`CLAUDE.md` 읽기만.
- `css/themes.css` 읽기 전용. 색 값·색 역할, 서체 asset·weight, 문구·수치·콘텐츠, 새 이미지·아이콘, 범위 확장 금지(원 §11.3).
- 빌더 Git 읽기: 원 §9 목록(rev-parse, diff, show, ls-files, ls-tree, status, log, `-w` 없는 hash-object).
- 모든 step 20분 이하(하네스 30분 상한 미만). 각 step은 exact 허용 파일·runtime·선행·AC(`… → FULL → VS → RGATE`)·중단 조건을 갖는다.

## R2. 약어 (원 §8.5에 추가)

- `RSNAP k` = `python3 -I tests/scripts/start-snapshot.py step{100+k}`(snapshot id `step100`~`step132`, 원 `step0..40`과 충돌 없음, 고정 S 정규식 `step[0-9]+` 안).
- `RGATE k <A> [<R>]` = `W node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step{100+k}.json --allow <A> [--require-absent <R>]`.
- `PREFLIGHT` = `python3 -I - <<'PY'` + §R4 블록 + `PY`; `OCC_CHECK b` = `python3 -I - b <<'PY'` + §R5 블록 + `PY`; `INTEGRATE_CHECK` = `python3 -I - <<'PY'` + §R6 블록 + `PY`; `MERGE_CHECK` = `python3 -I - <<'PY'` + §R7 블록 + `PY`.
- `SHA_SAVE <file> <tag>` = `python3 -I -c "import hashlib,os,sys; os.makedirs('tests/.tmp/resume-sha', exist_ok=True); open('tests/.tmp/resume-sha/'+sys.argv[2]+'.txt','w').write(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" <file> <tag>`.
- `SHA_DIFF <file> <tag> <label>` = `python3 -I -c "import hashlib,sys; a=open('tests/.tmp/resume-sha/'+sys.argv[2]+'.txt').read(); b=hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest(); print(sys.argv[3]+': '+('unchanged' if a==b else 'changed'))" <file> <tag> <label>`(쓰기 없음, 로그만).
- no-op 규칙(이월 step 16~28, 32만): `RSNAP` 뒤 AC(모두 쓰기 없는 명령)를 먼저 실행해 통과하면 파일 불변·로그 `resume step{k}: no-op`, 실패하면 그 step 허용 파일 안에서만 원 승인 작업 수행. step 29·30·31은 §R8 명시적 작업 step이며 no-op 규칙 대상이 아니다.

## R3. verify-scope 호환 준비 (resume step 0)

- 문제: 원 `tests/scripts/verify-scope.mjs`(원 §8.4)는 commit된 resume 설계와 `phases/HOO-81-portfolio-redesign-resume/**`를 범위 밖으로 거부 → 모든 `VS` 실패.
- 변경(이 step만, 허용 파일 2개): `tests/scripts/verify-scope.mjs`, `tests/specs/verify-scope-resume.spec.js`(신규).
  - 하네스 소유 committed 면제 목록에 정확히 `docs/superpowers/specs/2026-11-24-portfolio-redesign-resume-design.md` 1개 추가(원 설계와 같은 취급: committed 면제, staged·worktree 변경은 위반).
  - 하네스 런타임 면제에 `phases/HOO-81-portfolio-redesign-resume/**` 추가(원 phase 경로와 같은 취급, 접두 정확 일치 `phases/HOO-81-portfolio-redesign-resume/`).
  - 그 밖 정책·상수(`GIT_DIFF_PATH_ARGS`, `GIT_DIFF_PATCH_ARGS`, 위반 판정)는 불변. `--self-test`에 아래 사례 추가.
- 회귀(self-test와 spec 모두, 가짜 git 입력): 허용 — committed resume 설계, committed·worktree·untracked `phases/HOO-81-portfolio-redesign-resume/index.json`·`step0.md`; 위반 — worktree·staged 변경된 resume 설계, committed `docs/superpowers/specs/other.md`, committed `docs/superpowers/specs/2026-11-24-portfolio-redesign-resume-design.md.bak`, committed·worktree `phases/OTHER/x.json`, committed `phases/HOO-81-portfolio-redesign-resume-x/a.json`(접두 함정), 미커밋 `.harness/policy.json`, worktree 원 설계 수정, 미커밋 `CLAUDE.md`; 기존 self-test 사례 전부 통과 유지. 실저장소 `VS` → `verify-scope: OK`.

## R4. resume step 1 preflight (검증 전용)

```
import json, os, subprocess, sys
BASE_HEAD = '4b2ec3b325f400edefca0fbcfb8ff83bf739ff89'
PLAN = ('docs/superpowers/specs/2026-11-24-portfolio-redesign-resume-design.md', 'tests/scripts/verify-scope.mjs', 'tests/specs/verify-scope-resume.spec.js')
def git(*a):
    return subprocess.run(['git', *a], check=True, capture_output=True).stdout.decode()
if BASE_HEAD not in git('log', '--format=%H', 'HEAD').split():
    sys.exit('preflight: head-not-descendant')
extra = [p for p in git('diff', '--no-renames', '--name-only', BASE_HEAD, 'HEAD').split('\n') if p and p not in PLAN and not p.startswith('phases/HOO-81-portfolio-redesign-resume/')]
if extra:
    sys.exit('preflight: unexpected-commit-paths:' + ','.join(extra))
if git('diff', '--no-renames', '--name-only', BASE_HEAD, '--', 'phases/HOO-81-portfolio-redesign/', 'docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md', 'CLAUDE.md').strip():
    sys.exit('preflight: original-changed')
idx = json.loads(git('show', BASE_HEAD + ':phases/HOO-81-portfolio-redesign/index.json'))
st = {s['step']: s for s in idx['steps']}
bad = [str(n) for n in range(40) if st[n]['status'] != 'completed']
if bad:
    sys.exit('preflight: not-completed:' + ','.join(bad))
if st[40]['status'] != 'blocked' or '147' not in json.dumps(st[40], ensure_ascii=False):
    sys.exit('preflight: step40-blocker')
if git('diff', '--no-renames', '--name-only', BASE_HEAD, '--', 'tests/fixtures/axe-collected.json').strip():
    sys.exit('preflight: collected-changed')
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
need = ['tests/scripts/with-env.sh', 'tests/scripts/start-snapshot.py', 'tests/scripts/scope-snapshot.mjs', 'tests/scripts/design-intake-check.py', 'tests/scripts/verify-scope.mjs', 'tests/scripts/make-fixtures.mjs', 'tests/specs/verify-scope-resume.spec.js', 'tests/helpers/css-parse.js', 'tests/helpers/color-vocab.js', 'tests/helpers/design-guard-color-pairs.js', 'tests/helpers/design-guard-color-rules.js', 'tests/helpers/design-guard-color.js', 'tests/helpers/design-guard-font.js', 'tests/helpers/design-guard-css.js', 'tests/helpers/design-guard.js', 'tests/helpers/theme.js', 'tests/helpers/content.js', 'tests/helpers/modal.js', 'tests/helpers/axe.js', 'tests/helpers/axe-prepare.js', 'tests/specs/smoke.spec.js', 'tests/specs/axe-helper.spec.js', 'tests/specs/axe.spec.js', 'tests/fixtures/claude-design-intake.json', 'tests/fixtures/baseline-data.json', 'tests/fixtures/baseline-index.html', 'tests/fixtures/content-exceptions.json']
miss = [p for p in need if not os.path.isfile(p) or os.path.islink(p)]
if miss:
    sys.exit('preflight: missing:' + ','.join(miss))
late = [p for p in ('tests/fixtures/axe-baseline.json', 'tests/fixtures/axe-remediation-plan.json') if os.path.lexists(p)]
if late:
    sys.exit('preflight: classify-output-exists:' + ','.join(late))
print('resume-preflight: OK')
```

## R5. occurrence 분류 배치 (resume step 2~13)

- occurrence = collected entry `e`의 target `t` 하나: (key, scenario, project, ruleId, target, pair = `ruleId|target`). 139개를 (key, target) 코드 포인트 오름차순 정렬, batch b(1~12) = 정렬 목록 `[(b-1)*12, b*12)`. 개수(정확): batch 1~11 각 12, batch 12 = 7(11×12 + 7 = 139).
- 산정(고정, 준비·조사·검증 포함): `2 + occurrenceCount×1 + 6` → batch 1~11 = 20분, batch 12 = 15분. pair 중복 제거로 조사를 줄이지 않는다(occurrence마다 그 scenario·project 맥락에서 조사).
- 조사: Playwright를 `W node --input-type=module -` stdin 스크립트로 실행(스크립트 파일 저장 없음), occurrence마다 §THEME null-only 테마 context + `prepareForAxe({ scenario })`에서 대상 요소 조사. 판정 기준 = 원 step 40 작업 3(기존 색 값·색 custom property·색 적용 위치를 바꿔야 해소 → `requiresColorChange: true`, 크기·여백·레이아웃·속성·마크업·렌더만으로 해소 → false; `css-token` 항상 true, `js-render`·`static-markup`·`text-change` 항상 false). `evidence` = 근거(선언·속성 이름) 비어 있지 않은 문자열.
- 산출물(runtime, 배치마다 이 파일 하나만): `tests/.tmp/axe-classify/occ-batch-{b}.json` = `{ "schemaVersion": 1, "batch": b, "occurrences": [ { "key", "scenario", "project", "ruleId", "target", "pair", "fixKind", "requiresColorChange", "evidence" } ] }`(배치 정렬 순서). 같은 배치 안 같은 pair 판정이 다르면 파일을 쓰지 않고 `classification-inconsistent:{pair}` exit 1(재계획). baseline·plan은 만들지 않는다.
- `OCC_CHECK b` 블록:

```
import json, sys
b = int(sys.argv[1])
col = json.load(open('tests/fixtures/axe-collected.json', encoding='utf-8'))
occ = sorted(((e['key'], t, e) for e in col for t in e['targets']), key=lambda x: (x[0], x[1]))
if len(occ) != 139:
    sys.exit('occ-check: count')
want = occ[(b - 1) * 12:b * 12]
if not 1 <= b <= 12 or len(want) != (7 if b == 12 else 12):
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

## R6. pair 통합 (resume step 14)

- 입력 occ-batch-1~12(139 occurrence). 배치를 넘는 pair까지 모든 occurrence 판정(`fixKind`, `requiresColorChange`) 일치 확인(불일치면 `classification-inconsistent:{pair}` 중단·재계획). 출력(runtime, 이 파일만): `tests/.tmp/axe-classify/pairs.json` = `{ "schemaVersion": 1, "pairs": [ { "pair", "ruleId", "target", "fixKind", "requiresColorChange", "evidence", "occurrenceCount" } ] }`(pair 코드 포인트 오름차순, evidence는 그 pair occurrence evidence를 `; `로 이은 문자열). 산정 12분.
- `INTEGRATE_CHECK` 블록:

```
import json, sys
col = json.load(open('tests/fixtures/axe-collected.json', encoding='utf-8'))
occ = {}
for e in col:
    for t in e['targets']:
        occ.setdefault(e['ruleId'] + '|' + t, []).append(e['key'])
rows = []
for b in range(1, 13):
    rows += json.load(open('tests/.tmp/axe-classify/occ-batch-%d.json' % b, encoding='utf-8'))['occurrences']
if len(rows) != 139 or len({(o['key'], o['target']) for o in rows}) != 139:
    sys.exit('integrate-check: count')
dec = {}
for o in rows:
    v = (o['fixKind'], o['requiresColorChange'])
    if dec.setdefault(o['pair'], v) != v:
        sys.exit('classification-inconsistent:' + o['pair'])
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
    if (x['fixKind'], x['requiresColorChange']) != dec[k] or x['occurrenceCount'] != len(occ[k]):
        sys.exit('integrate-check: pair-mismatch:' + k)
    if not isinstance(x['evidence'], str) or not x['evidence']:
        sys.exit('integrate-check: pair-evidence:' + k)
print('integrate-check: OK 25 139')
```

## R7. merge (resume step 15)

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

## R8. 변경형 step (resume 29 gate · 30 recheck · 31 finalize)

- no-op 규칙 제외. 작업 순서(고정): `RSNAP` → 쓰기 없는 사전 검사(`COLLECT_CHAIN --out tests/.tmp/axe-current.json`, `REGRESSION_GATE`; 회귀 실패면 tracked 불변 중단) → `SHA_SAVE <대상> <tag>` → 작업 부분에서만 변경 명령(29·30 `AXE --prune-plan --collected tests/.tmp/axe-current.json`, 31 baseline `[]` 기록) → `SHA_DIFF <대상> <tag> <label>`(로그 `plan-pruned: changed|unchanged` 또는 `baseline-finalized: changed|unchanged`, no-op 선언 없음) → AC(쓰기 없는 검증 → `FULL` → `VS` → `RGATE`).
- `--prune-plan`은 AC나 사전 probe에서 실행하지 않는다. 재계획 `axe-remediation-{id}`는 resume 29와 30 사이.

## R9. step 대응 (원 step N(41~57) = resume step N−25)

| resume | name | 원 | 분 |
|---|---|---|---|
| 0 | verify-scope-resume-compat | — | 18 |
| 1 | resume-preflight | — | 15 |
| 2~12 | axe-classify-occ-batch-1~11 | 40 분할(각 12 occurrence) | 20 |
| 13 | axe-classify-occ-batch-12 | 40 분할(7 occurrence) | 15 |
| 14 | axe-classify-pair-integrate | 40 분할 | 12 |
| 15 | axe-classify-merge | 40 분할 | 18 |
| 16 | featured-projects | 41 | 19 |
| 17 | hero-first-screen | 42 | 20 |
| 18 | hero-two-column | 43 | 19 |
| 19 | section-structure | 44 | 19 |
| 20 | section-layout | 45 | 17 |
| 21 | component-hit-open | 46 | 19 |
| 22 | state-sequence | 47 | 18 |
| 23 | state-colors-fixture | 48 | 19 |
| 24 | component-hover-active | 49 | 16 |
| 25 | component-clamp-stripe | 50 | 15 |
| 26 | focus-trap-modal | 51 | 17 |
| 27 | focus-trap-lightbox | 52 | 17 |
| 28 | print-pdf | 53 | 17 |
| 29 | axe-remediation-gate | 54 | 18 |
| (재계획) | axe-remediation-{id} | 54~55 사이 | ≤20 |
| 30 | axe-remediation-recheck | 55 | 18 |
| 31 | axe-finalize | 56 | 16 |
| 32 | final-verification | 57 | 17 |

- 원 설계 step 번호 상호참조: §9 `index.html` 구조 변경 step 41·42·44 → resume 16·17·19, 예외 (a)·(b) step 44 → resume 19, §11.2 step 46~50 → resume 21~25, 원 step 54와 55 사이 재계획 → resume 29와 30 사이. 선행 = 작은 번호 전부(30은 재계획 그룹 포함).
