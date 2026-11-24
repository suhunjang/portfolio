# HOO-81 resume 설계 보완 (runtime-replan-step40-v47, base-fix-v48)

- 원 설계(유효, 수정 금지): `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md`(compact v46). 이 문서의 `§n`은 원 설계 절, `§R n`은 이 문서 절이다.
- 원 phase: `HOO-81-portfolio-redesign`(step 0~39 completed, step 40 `axe-classify` blocked). resume phase: `HOO-81-portfolio-redesign-resume`(step 0~21).
- resume BASE_HEAD(불변 사실): `4b2ec3b325f400edefca0fbcfb8ff83bf739ff89`(`chore(HOO-81): record step 40 runtime blocker`, metadata-only — 원 phase index.json에 step 0~39 completed·step 40 blocked·147분 사유 기록). 이력 참고: 마지막 완료 step 39 산출 commit `1d5d27b0377ef575b9e54d79b7f8178e9af3daad`(resume 기준 아님).
- blocker(불변 사실): `tests/fixtures/axe-collected.json` = entry 12 / target occurrence 139(color-contrast 61, nested-interactive 78) / 서로 다른 `ruleId|canonical target` pair 25. 원 §6.2 산정(묶음별 2분 + target×1분 + 6분) = 147분 > 20 → step 40은 정당하게 blocked. step 40 상태·blocker evidence는 재설정·편집·삭제하지 않고 원 승인 계획은 재실행하지 않는다.
- 원 승인·리뷰는 재사용하지 않는다. §ID·§G·§8.5 약어·§6.4/§6.5·§11 계약·§THEME는 원 설계 그대로 참조한다.
- §R FLOW: materialize → 현재 브랜치 plan-only commit → Astra `gpt-6-astra` CLEAN → 새 대표 exact 승인 → resume phase만 fresh runner(step 0~21) → 전체 검증 → exact-commit 리뷰 → feature push → OPEN PR. merge·deploy·main 직접 변경 없음.

## R1. 불변·금지

- 원 §9 공통 금지 전부 유지. 추가: 기존 구현 commit·artifact·runtime snapshot(`tests/.tmp/start-snapshot-step0..40*`) 보존(삭제·덮어쓰기 금지), `git reset/restore/checkout/clean`·삭제·push 금지, 원 phase `phases/HOO-81-portfolio-redesign/**` 읽기만.
- `css/themes.css` 읽기 전용. 색 값·색 역할, 서체 asset·weight, 문구·수치·콘텐츠, 새 이미지·아이콘, 범위 확장 금지(원 §11.3).
- 빌더 Git 읽기: 원 §9 목록(rev-parse, diff, show, ls-files, ls-tree, status, log, `-w` 없는 hash-object).
- 모든 step 20분 이하. 각 step은 exact 허용 파일·runtime·선행·AC(`T` → `FULL` → `VS` → `RGATE`)를 갖는다.

## R2. 약어 (원 §8.5에 추가)

- `RSNAP k` = `python3 -I tests/scripts/start-snapshot.py step{100+k}`(resume step k의 snapshot id는 `step{100+k}`; 원 `step0..40` snapshot과 충돌 방지, 고정 S 정규식 `step[0-9]+` 안).
- `RGATE k <A> [<R>]` = `W node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step{100+k}.json --allow <A> [--require-absent <R>]`.
- `PREFLIGHT` = `python3 -I - <<'PY'` + §R3 블록 + `PY`. `BATCH_CHECK n` = `python3 -I - n <<'PY'` + §R4 블록 + `PY`. `MERGE_CHECK` = `python3 -I - <<'PY'` + §R5 블록 + `PY`.
- 이월 no-op 규칙: 이월 step(5~21)은 `RSNAP` 뒤 AC를 먼저 실행해 통과하면 파일 불변·로그 `resume step{k}: no-op`, 실패하면 그 step 허용 파일 안에서만 원 승인 작업을 수행한다.

## R3. resume step 0 preflight (검증 전용)

```
import json, os, subprocess, sys
BASE_HEAD = '4b2ec3b325f400edefca0fbcfb8ff83bf739ff89'
PLAN = ('docs/superpowers/specs/2026-11-24-portfolio-redesign-resume-design.md',)
def git(*a):
    return subprocess.run(['git', *a], check=True, capture_output=True).stdout.decode()
if BASE_HEAD not in git('log', '--format=%H', 'HEAD').split():
    sys.exit('preflight: head-not-descendant')
extra = [p for p in git('diff', '--no-renames', '--name-only', BASE_HEAD, 'HEAD').split('\n') if p and p not in PLAN and not p.startswith('phases/HOO-81-portfolio-redesign-resume/')]
if extra:
    sys.exit('preflight: unexpected-commit-paths:' + ','.join(extra))
idx = json.loads(git('show', BASE_HEAD + ':phases/HOO-81-portfolio-redesign/index.json'))
if git('diff', '--no-renames', '--name-only', BASE_HEAD, '--', 'phases/HOO-81-portfolio-redesign/').strip():
    sys.exit('preflight: original-phase-changed')
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
need = ['tests/scripts/with-env.sh', 'tests/scripts/start-snapshot.py', 'tests/scripts/scope-snapshot.mjs', 'tests/scripts/design-intake-check.py', 'tests/scripts/verify-scope.mjs', 'tests/scripts/make-fixtures.mjs', 'tests/helpers/css-parse.js', 'tests/helpers/color-vocab.js', 'tests/helpers/design-guard-color-pairs.js', 'tests/helpers/design-guard-color-rules.js', 'tests/helpers/design-guard-color.js', 'tests/helpers/design-guard-font.js', 'tests/helpers/design-guard-css.js', 'tests/helpers/design-guard.js', 'tests/helpers/theme.js', 'tests/helpers/content.js', 'tests/helpers/modal.js', 'tests/helpers/axe.js', 'tests/helpers/axe-prepare.js', 'tests/specs/smoke.spec.js', 'tests/specs/axe-helper.spec.js', 'tests/specs/axe.spec.js', 'tests/fixtures/claude-design-intake.json', 'tests/fixtures/baseline-data.json', 'tests/fixtures/baseline-index.html', 'tests/fixtures/content-exceptions.json']
miss = [p for p in need if not os.path.isfile(p) or os.path.islink(p)]
if miss:
    sys.exit('preflight: missing:' + ','.join(miss))
late = [p for p in ('tests/fixtures/axe-baseline.json', 'tests/fixtures/axe-remediation-plan.json') if os.path.lexists(p)]
if late:
    sys.exit('preflight: classify-output-exists:' + ','.join(late))
print('resume-preflight: OK')
```

## R4. 분류 배치 (resume step 1~3)

- pair = `ruleId + '|' + canonical target`(collected 각 entry의 targets). 25개 pair를 코드 포인트 오름차순 정렬, batch n = 정렬 목록의 `[(n-1)*12, n*12)` → batch 1 = 12, batch 2 = 12, batch 3 = 1.
- 산정(고정): `2 + canonicalPairCount×1 + 6` → 20 / 20 / 9분.
- 산출물(배치마다 정확히 1개, runtime): `tests/.tmp/axe-classify/batch-{n}.json` = `{ "schemaVersion": 1, "batch": n, "pairs": [ { "pair", "ruleId", "target", "fixKind", "requiresColorChange", "evidence", "occurrences": [ { "key", "scenario", "project" } ] } ] }`(pairs는 batch 정렬 순서, occurrences는 그 pair가 나타나는 collected entry 전부).
- 조사: Playwright를 `W node --input-type=module -` stdin 스크립트로 실행(스크립트 파일을 남기지 않음), occurrence마다 해당 scenario·project 조건(§THEME null-only 테마 + `prepareForAxe`)에서 대상 요소를 조사. `fixKind`·`requiresColorChange` 기준은 원 step 40(§6.4·원 step40 작업 3) 그대로: 기존 색 값·색 custom property·색 적용 위치를 바꿔야 해소되면 true, 크기·여백·레이아웃·속성·마크업·렌더만으로 해소되면 false; `css-token` 항상 true, `js-render`·`static-markup`·`text-change` 항상 false. `evidence` = 판정 근거(선언·속성 이름) 비어 있지 않은 문자열.
- 같은 pair의 occurrence 간 판정(`fixKind`, `requiresColorChange`)이 다르면 파일을 쓰지 않고 `classification-inconsistent:{pair}`로 exit 1, 재계획.
- `BATCH_CHECK n` 블록:

```
import json, sys
n = int(sys.argv[1])
col = json.load(open('tests/fixtures/axe-collected.json', encoding='utf-8'))
occ = {}
for e in col:
    for t in e['targets']:
        occ.setdefault(e['ruleId'] + '|' + t, []).append({'key': e['key'], 'scenario': e['scenario'], 'project': e['project']})
pairs = sorted(occ)
if len(pairs) != 25:
    sys.exit('batch-check: pairs-count')
want = pairs[(n - 1) * 12:n * 12]
b = json.load(open('tests/.tmp/axe-classify/batch-%d.json' % n, encoding='utf-8'))
if not isinstance(b, dict) or set(b) != {'schemaVersion', 'batch', 'pairs'} or b['schemaVersion'] != 1 or b['batch'] != n:
    sys.exit('batch-check: shape')
if [p.get('pair') for p in b['pairs']] != want:
    sys.exit('batch-check: pairs')
KINDS = ('css-token', 'css-rule', 'js-render', 'static-markup', 'text-change')
FIXED = {'css-token': True, 'js-render': False, 'static-markup': False, 'text-change': False}
PF = {'pair', 'ruleId', 'target', 'fixKind', 'requiresColorChange', 'evidence', 'occurrences'}
for p in b['pairs']:
    k = p['pair']
    if set(p) != PF:
        sys.exit('batch-check: pair-shape:' + k)
    r, t = k.split('|', 1)
    if p['ruleId'] != r or p['target'] != t:
        sys.exit('batch-check: pair-split:' + k)
    if p['fixKind'] not in KINDS or type(p['requiresColorChange']) is not bool:
        sys.exit('batch-check: pair-kind:' + k)
    if p['fixKind'] in FIXED and FIXED[p['fixKind']] != p['requiresColorChange']:
        sys.exit('batch-check: pair-color:' + k)
    if not isinstance(p['evidence'], str) or not p['evidence']:
        sys.exit('batch-check: pair-evidence:' + k)
    if sorted(p['occurrences'], key=lambda o: o['key']) != sorted(occ[k], key=lambda o: o['key']):
        sys.exit('batch-check: pair-occurrences:' + k)
print('batch-check %d: OK %d' % (n, len(want)))
```

## R5. merge (resume step 4)

- 입력: batch-1~3. 출력(tracked, 이 step만): `tests/fixtures/axe-baseline.json`(원 §6.4: collected entry마다, fixes는 targets 순서 1:1, 각 fix의 `fixKind`·`requiresColorChange` = 그 pair의 batch 결정, fixFiles = `FIX_FILES_BY_KIND`, entry fixFiles 합집합), `tests/fixtures/axe-remediation-plan.json`(원 §6.5: PlanTarget·id 정렬, coverage 완전, 각 그룹 R = `requiredBlockReason(targets, baseline)`; R ≠ `""`면 blocked true·reason R, 아니면 false·`""`, manual block 생성 금지, 그룹 estMinutes 1~20).
- `MERGE_CHECK` 블록:

```
import json, sys
col = json.load(open('tests/fixtures/axe-collected.json', encoding='utf-8'))
dec = {}
for n in (1, 2, 3):
    for p in json.load(open('tests/.tmp/axe-classify/batch-%d.json' % n, encoding='utf-8'))['pairs']:
        if p['pair'] in dec:
            sys.exit('merge-check: dup-pair:' + p['pair'])
        dec[p['pair']] = p
if len(dec) != 25 or sum(len(p['occurrences']) for p in dec.values()) != 139:
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

- blocked 그룹이 있거나 `--check-executable` 실패면 step 4는 실패로 끝나고 원 §6.2 remediation 재계획 경로로 멈춘다.

## R6. step 대응 (원 step N(41~57) = resume step N−36)

| resume | name | 원 step | 분 |
|---|---|---|---|
| 0 | resume-preflight | — | 15 |
| 1 | axe-classify-batch-1 | 40 분할 | 20 |
| 2 | axe-classify-batch-2 | 40 분할 | 20 |
| 3 | axe-classify-batch-3 | 40 분할 | 9 |
| 4 | axe-classify-merge | 40 분할 | 18 |
| 5 | featured-projects | 41 | 19 |
| 6 | hero-first-screen | 42 | 20 |
| 7 | hero-two-column | 43 | 19 |
| 8 | section-structure | 44 | 19 |
| 9 | section-layout | 45 | 17 |
| 10 | component-hit-open | 46 | 19 |
| 11 | state-sequence | 47 | 18 |
| 12 | state-colors-fixture | 48 | 19 |
| 13 | component-hover-active | 49 | 16 |
| 14 | component-clamp-stripe | 50 | 15 |
| 15 | focus-trap-modal | 51 | 17 |
| 16 | focus-trap-lightbox | 52 | 17 |
| 17 | print-pdf | 53 | 17 |
| 18 | axe-remediation-gate | 54 | 18 |
| (재계획) | axe-remediation-{id} | 54~55 사이 | ≤20 |
| 19 | axe-remediation-recheck | 55 | 18 |
| 20 | axe-finalize | 56 | 16 |
| 21 | final-verification | 57 | 17 |

- 원 설계의 step 번호 상호참조(§6.2 단계, §9 `index.html` 구조 변경 step 41·42·44 → resume 5·6·8, 예외 (a)·(b) step 44 → resume 8, §11.2 step 46~50 → resume 10~14, 원 step 54와 55 사이 재계획 → resume 18과 19 사이)는 이 표로 읽는다. 선행 = 작은 번호 전부(19는 재계획 그룹 포함).
