# HOO-81 color-resume 설계 (v52 색 결정 · v56 필수 범위 · v57 direct worktree · v58 Astra 교정)

- phase: `HOO-81-portfolio-redesign-color-resume`(step 0~5). 원 설계 `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md`(§n)와 resume 설계 `docs/superpowers/specs/2026-11-24-portfolio-redesign-resume-design.md`(§R n)는 유효하며 수정하지 않는다. 이 문서의 절 번호는 `§C n`이다.
- 결정:
  - `representative-color-scope-v52`: color-contrast는 기존 token만 쓰는 최소 색 변경으로 고친다.
  - `final-required-scope-parallel-v56`: resume 18~30이 필수 범위다.
  - `executable-direct-worktree-v57`: Harness 2.0.1은 linked worktree를 project root로 받지 않고 parallel runner도 없다. 따라서 direct Claude worktree worker가 작업하고 canonical Harness가 검증한다.
  - Astra record `a39a4d9240abbbdf8a3f29d6462cc8cd3cce67f8279821b9e150addb418852c9`의 major 6건을 반영했다(§C4~§C7).
  - v57 계획 commit은 리뷰 이력으로 보존한다.
- BASE_HEAD(불변): `aa6f37c803ffaf8712418e94971ed4567e2a390d`. 이력 commit: `1d5d27b0377ef575b9e54d79b7f8178e9af3daad`, `dce163d89666acdd30a49705ebc4e93c6dba4636`.
- 승계(재실행하지 않음): 원 phase는 step 0~39 completed, 40 blocked. resume phase는 step 0~16 completed, 17 blocked. 아래 두 hash는 이력 seed다(color 12 pair/61 occurrence, nested 13 pair/78 occurrence). 정본은 step 3의 final collect다.
  - `tests/.tmp/axe-classify/pairs.json` sha256 `1ba8778ab6cc9254b4404a5349f53c4463c0c55e4a1b2b447eac02a8bd8acaa1`
  - `tests/fixtures/axe-collected.json` sha256 `ff7c76a6214034251f5ebc028706b9ae383ec6ecb9ce8a4c3ed97e266672e63c`
- 작업 지시서: `phases/HOO-81-portfolio-redesign-resume/step18.md`~`step30.md`를 읽기 전용으로 승계한다. 허용 anchor·RED spec·AC(`REQ`·`RBRANCH`·§R10·§R11 포함)를 그대로 따르고, 내용을 복사하지 않는다.
- 보존 대상: 텍스트·숫자, 서체 asset·weight, 6개 섹션, PROJECTS 13개와 순서, 이미지·아이콘, 완료된 레이아웃·컴포넌트·간격·타이포.
- 금지: 팔레트 재설계, 새 token, 리터럴 색, `css/themes.css` 변경.
- §C FLOW: materialize → plan-only commit → GPT-6 Astra 리뷰 1회(비차단 개선은 HOO-107로) → 새 대표 exact 승인 → Harness step 0 → step 1 → coordinator `doctor`와 wave 1 → step 2 → step 3 → coordinator wave 2 → step 4 → step 5 → exact-commit Astra CLEAN → feature push → OPEN PR → tested = reviewed = pushed = PR-head SHA. 진행 보고는 시작·fan-out·실패/재시도·통합·최종 검증·완료 때만 한다.

## C1. 불변·금지

- 원 §9와 resume §R1을 유지한다. 원 phase·resume phase, 두 설계 문서, `CLAUDE.md`, `tests/fixtures/axe-collected.json`은 읽기만 한다.
- 금지:
  - `git reset/restore/checkout/clean`, 광범위 삭제
  - main 직접 변경, merge, cherry-pick, deploy, runner·worker의 push
  - Harness linked root 호출, Harness 내부 함수 호출
- 허용하는 git 쓰기:
  - Harness runner의 step commit
  - coordinator의 `git worktree add`, lane local commit, canonical `git apply --index`, integration commit, 검증된 lane의 exact `git worktree remove <path>`·`git branch -D <branch>`
  - `parallel-wave.mjs`의 composite tree 계산에 한해, `tests/.tmp/parallel/idx-*`를 임시 index(`GIT_INDEX_FILE`)로 써서 `git read-tree`·`git apply --cached`·`git write-tree`를 실행하는 것. object만 생성하고 ref·canonical index·worktree는 바꾸지 않는다.
- worker는 git 쓰기를 하지 않는다.
- 시간: 모든 step에서 agent 예상 작업은 **20분 이하**다. **Harness hard timeout은 30분**으로 따로 둔다. 테스트 subprocess timeout은 기존 설정(`tests/playwright.config.js`와 각 spec의 `test.setTimeout`)을 따르고, agent 예상 작업 시간과 구분한다.
- Harness step은 background worker를 기다리지 않는다.

## C2. 약어 (원 §8.5·resume §R2에 추가)

- `XSNAP k` = `python3 -I tests/scripts/start-snapshot.py step{200+k}`
- `XGATE k <A> [<R>]` = `W node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step{200+k}.json --allow <A> [--require-absent <R>]`
- `PREFLIGHT` = `python3 -I - <<'PY'` + §C3 블록 + `PY`
- `PW` = `W node tests/scripts/parallel-wave.mjs`
- `SCR` = `/Users/hoon/.hermes/profiles/ryan/cache/scratch/HOO-81-parallel-<run>`
- `<run>`은 `^[a-z0-9]{6,32}$`를 만족해야 한다.

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
need = ['tests/package.json', 'tests/playwright.config.js', 'tests/node_modules/@playwright/test/index.js', 'tests/scripts/with-env.sh', 'tests/scripts/start-snapshot.py', 'tests/scripts/scope-snapshot.mjs', 'tests/scripts/verify-scope.mjs', 'tests/helpers/css-parse.js', 'tests/helpers/axe.js', 'tests/helpers/axe-prepare.js', 'tests/helpers/theme.js', 'tests/helpers/design-guard.js', 'tests/helpers/design-guard-color-rules.js', 'tests/specs/design-guard-color-rules.spec.js', 'tests/specs/axe.spec.js', 'tests/specs/smoke.spec.js', 'tests/specs/verify-scope-resume.spec.js'] + ['phases/HOO-81-portfolio-redesign-resume/step%d.md' % n for n in range(18, 31)]
miss = [p for p in need if not os.path.isfile(p) or os.path.islink(p)]
if miss:
    sys.exit('preflight: missing:' + ','.join(miss))
late = [p for p in ('tests/fixtures/axe-baseline.json', 'tests/fixtures/axe-remediation-plan.json', 'tests/scripts/parallel-wave.mjs', 'tests/specs/parallel-wave.spec.js') if os.path.lexists(p)]
if late:
    sys.exit('preflight: output-exists:' + ','.join(late))
print('color-resume-preflight: OK')
```

## C4. `tests/scripts/parallel-wave.mjs` 인터페이스 (step 1)

- 공통 규칙:
  - Node ESM이며 의존성은 node 내장 모듈과 저장소 helper(`tests/helpers/css-parse.js`, `tests/helpers/design-guard-color-rules.js`)뿐이다.
  - 성공하면 stdout에 `parallel-wave <sub>: OK …`를 쓰고 exit 0.
  - 계약 위반이면 stderr에 `parallel-wave: <code>:<detail>`을 쓰고 exit 1.
  - 인자 오류는 exit 2.
  - `--apply`가 없는 모든 명령은 파일·git 쓰기를 하지 않는다. 예외는 §C1의 임시 index object 생성뿐이다.

### `doctor [--claude-bin <path>] [--help-text <file>]`

- `<claude-bin> --help` 출력(spec에서는 `--help-text`)에 `-p`·`--print`, `--permission-mode`, `--allowedTools`, `--max-turns`, `--add-dir`, `--setting-sources`, `--output-format`이 모두 있어야 한다.
- 함께 확인하는 것:
  - `git worktree list`가 동작한다.
  - canonical의 `tests/node_modules/@playwright/test/index.js`와 `tests/.pw-browsers`가 존재한다.
  - 127.0.0.1 포트 4174~4184가 모두 연결 거부 상태다.
  - 환경변수에 `OPENROUTER_API_KEY`·`ANTHROPIC_BASE_URL`이 없다.
- 생성 명령에는 `--bare`·`--dangerously-skip-permissions`가 들어갈 수 없다. 코드 상수로 금지한다.
- 실패 코드: `doctor:flag-missing:<f>`, `doctor:dep-missing:<p>`, `doctor:port-busy:<n>`, `doctor:forbidden-env:<k>`.

### `prepare --wave <1|2> --run-root <SCR> --base <sha> [--manifest <path>] [--apply]`

- lane contract(§C5)로부터 lane별 다음 값을 확정한다:
  - `worktree` = `<SCR>/lane-<id>`
  - `branch` = `hoo81-<run>-w<wave>-lane-<id>`
  - `port`
  - `evidence` = `<SCR>/evidence/lane-<id>`
  - `prompt` = `<evidence>/prompt.md`
  - `argv`
- `argv` = `['claude', '-p', <prompt 내용>, '--setting-sources', 'user', '--permission-mode', 'acceptEdits', '--add-dir', <evidence>, '--max-turns', '200', '--output-format', 'json', '--allowedTools', <allowlist>]`, 환경변수 `PW_PORT=<port>`.
- `<allowlist>` = `Read`, `Glob`, `Grep`, `Edit`, `Write`, 그리고 contract `requiredCommands`의 각 명령을 `Bash(<정확한 명령>)`으로 감싼 것, `Bash(git diff:*)`, `Bash(git status:*)`.
- prompt는 다음을 고정한다:
  - `CLAUDE.md` 전문, 원 §9·§11.3 금지
  - 승계 step 파일 전문(wave 2는 shard 항목)
  - 허용 파일·anchor, lane 내부 step 순서, requiredCommands
  - checkpoint 형식 `<evidence>/checkpoint-<step>.json` = `{lane, step, commands: [{cmd, exit}], result}`
  - 금지 목록
- 출력: `--apply`가 없으면 위 내용을 정렬된 JSON으로 stdout에 낸다.
- `--apply`일 때만 수행하는 것:
  - `git worktree add -b <branch> <worktree> <base>`
  - lane worktree에 symlink 2개(`tests/node_modules`, `tests/.pw-browsers` → canonical)
  - prompt 파일 작성
- wave 2는 먼저 `validate-manifest`를 통과해야 한다. 통과하지 못하면 `prepare:manifest-invalid`.

### `validate-lane --wave <w> --lane <id> --base <sha> --lane-commit <sha> --result <evidence dir>`

- `<lane-commit>`의 first parent가 `<base>`여야 한다. 아니면 `lane:bad-base`.
- `git diff --binary --no-renames base laneCommit`에서 다음을 계산해 contract와 대조한다. 위반 코드는 `lane:files`, `lane:anchor:<file>:<anchor>`.
  - diff sha256
  - 변경 파일 ⊆ contract의 `files`
  - 각 hunk의 semantic anchor ⊆ contract의 `anchors`
- checkpoint 파일 집합의 step 목록이 contract `steps`와 정확히 같고 모두 `result: 'pass'`여야 한다(`lane:checkpoints`).
- 각 step의 `commands`가 contract `requiredCommands[step]`과 정확히 같은 목록이고 모두 `exit: 0`이어야 한다(`lane:commands:<step>`).
- 출력: `{lane, diffSha256, files, anchors}`.

### semantic anchor 판정 (validate-lane·check-overlap 공통)

- CSS: `css-parse.js`로 hunk 줄이 속한 rule의 `(at-rule chain, selectors)`를 구한다.
- HTML: hunk 시작 줄에서 가장 가까운 조상 요소의 `id`. 조상에 id가 없으면 `body`.
- JS: hunk 시작 줄에서 위로 중괄호 깊이를 세어 가장 안쪽 enclosing 시그니처를 찾는다.
  - `function NAME(` → `fn:NAME`
  - `X.addEventListener("E"` → `listener:X:E`
  - `const NAME =` → `const:NAME`
  - 어디에도 속하지 않으면 `module`이다. 이때 hunk의 추가 줄 전부가 contract `linePatterns` 중 하나와 맞아야 한다.

### `check-overlap --wave <w> --lanes <id>=<base>..<commit>[,…]`

- lane 쌍마다 다음 중 하나라도 있으면 overlap이다:
  - 같은 파일에서 base 줄 범위가 교차하는 hunk
  - 같은 (file, anchor)
- overlap 출력: `overlap:<a>,<b>:<file>:<anchor|lines>`.
- 같은 파일이라도 hunk가 disjoint이고 anchor가 다르면 허용한다.

### `fan-in --wave <w> --canonical <repo> --lanes <id>=<base>..<commit>[,…] [--apply]`

- 먼저 `check-overlap`을 통과해야 한다.
- 순서는 contract의 `importOrder`를 따른다.
- `--apply`가 없으면: 임시 index에서 import 기준 tree에 lane patch를 순서대로 `apply --cached`하고 composite tree hash만 출력한다.
- `--apply`면:
  1. canonical에서 `git apply --index --check`, 이어서 `git apply --index`
  2. 적용 후 `git write-tree`(canonical index)가 composite tree와 같은지 확인한다. 다르면 `fan-in:bytes`.
  3. `<SCR>/fanin-<w>.json`(lane별 diffSha256, compositeTree)을 기록한다.
- integration commit은 coordinator가 만든다. merge·cherry-pick은 쓰지 않는다.

### `record --wave <w> --run-root <SCR> --runtime tests/.tmp/parallel/wave-<w>.json --external <SCR>/record-wave-<w>.json --wave-base <sha> --parallel-base <sha> --integration <sha> --lanes <id>=<base>..<commit>[,…] [--manifest <path>]`

- §C6 envelope를 두 경로에 같은 bytes로 쓴다.
- lane 필드는 `validate-lane` 결과, `<SCR>/run-<w>.json`(coordinator가 기록한 pid·sessionId·worktree·branch·port), checkpoint로부터 만든다.

### `verify-record --wave <w> --runtime <p> --external <p> [--manifest <p>]`

- 실패 코드는 다음과 같다.
  - 두 파일이 byte 단위로 다름 → `record:mismatch`
  - envelope 키가 정확히 `schemaVersion`·`payload`·`payloadSha256`가 아님, 또는 `schemaVersion`이 1이 아님 → `record:envelope`
  - payload hash 재계산 결과가 다름 → `record:hash`
  - `payload.phase`·`wave` 불일치 → `record:phase`
  - `integrationCommit`이 HEAD가 아님 → `record:head`
  - `waveBase`·`parallelBase`가 HEAD의 조상이 아님 → `record:ancestry`
  - lane 목록이 contract와 다름 → `record:lanes`
- 각 lane에 대해 `validate-lane`과 같은 검사를 git object에서 다시 수행한다(`lane:*`).
- composite tree 검증:
  - wave 1: `waveBase` + P 패치 = `parallelBase` tree이고, `parallelBase` + A→E 패치 = `integrationCommit` tree여야 한다.
  - wave 2: `parallelBase` + shard 패치 = `integrationCommit` tree여야 한다.
  - 하나라도 다르면 `record:composite`.
- 출력: `parallel-wave verify-record: OK wave <w> <n> lanes`.

### `validate-manifest --collected <p> --manifest <p>`

- §C7 계약을 검사한다.
- 출력: `parallel-wave validate-manifest: OK <targets> targets <shards> shards`.

### 직렬 재시도 계약 (coordinator)

- `check-overlap`이 실패하면 겹친 두 lane 중 import 순서가 뒤인 lane만 다시 실행한다. 새 base는 앞 lane까지 통합한 상태다. lane id 뒤에 `r1`을 붙이고, 1회만 재시도한다.
- canonical 통합 후 Harness checkpoint에서 실패한 spec이 있으면, 그 spec을 소유한 lane만 같은 방식으로 다시 실행한다. spec 소유자는 contract의 `files`로 정한다.
- 성공한 다른 lane은 보존한다. 재시도에서 다시 실패하면 그 lane을 block 처리하고 보존한다.

## C5. lane contract

- 공통: `baseSha`는 실행 시 주입한다(wave 1 P는 `waveBase`, A~E는 `parallelBase`).
- 각 step의 `requiredCommands`는 승계 step 파일 AC에서 `FULL`·`VS`·`RGATE`·`RGATE_B`를 뺀 명령을 정확한 문자열 그대로 쓴다. 해당 step의 `REQ`·`RBRANCH` probe도 포함한다.
- 아래 표는 코드 상수 `WAVE1_CONTRACT`(importOrder `['A','B','C','D','E']`)다.
- P · port 4174 · steps `[18]`
  - files: `index.html`, `js/data.js`, `js/main.js`, `css/style.css`, `tests/specs/featured.spec.js`
  - anchors:
    - html `hero`
    - js `fn:renderFeaturedProjects`, `fn:openProjectModal`, `listener:heroFeatured:click`, `listener:heroFeatured:keydown`
    - `module` + linePatterns `^\s*renderFeaturedProjects\(\);?$`
    - data `featured: true,` 줄
    - css selector `^\.featured-`와 `.project-card`를 포함한 기존 color rule에 `.featured-card` 대응 선택자를 추가하는 것
  - requiredCommands: 18 = `DI`, `T featured.spec.js GS`
- A · port 4175 · steps `[19, 20]`
  - files: `index.html`, `js/main.js`, `css/style.css`, `tests/specs/hero.spec.js`, `tests/specs/hero-layout.spec.js`
  - anchors:
    - html `hero`
    - js `module` + linePatterns `^\s*setText\('heroTagline', PROFILE\.tagline\);$`
    - css selector `^(\.hero|#hero|\.stat|\.featured-)`, 그리고 `@media (min-width: 1024px)` 안의 같은 선택자
  - requiredCommands:
    - 19 = `DI`, `T hero.spec.js GS`
    - 20 = `RBRANCH 20 tests/specs/hero-layout.spec.js`, `DI`, `T hero-layout.spec.js hero.spec.js GS`
- B · port 4176 · steps `[21, 22]`
  - files: `index.html`, `js/main.js`, `css/style.css`, `tests/specs/structure.spec.js`, `tests/specs/layout.spec.js`
  - anchors:
    - html: `hero` 밖 섹션 id와 `nav`, 그리고 `.scroll-hint` 줄
    - js `fn:onScroll`, `const:items`
    - css selector `^(section|\.section|#career|#projects|#strengths|#about|#contact|\.career|#projectGrid|#strengthsGrid|#skillsGrid|\.subsection-title|h2)`
  - requiredCommands:
    - 21 = `DI`, `T structure.spec.js GS`
    - 22 = `DI`, `T layout.spec.js GS`
- C · port 4177 · steps `[23, 24, 25, 26, 27]`
  - files: `css/style.css`, `tests/helpers/component-state.js`, `tests/specs/component-hit.spec.js`, `tests/helpers/state-sequence.js`, `tests/specs/state-sequence.spec.js`, `tests/scripts/make-state-colors.mjs`, `tests/fixtures/component-state-colors.json`, `tests/specs/state-colors.spec.js`, `tests/specs/component-hover.spec.js`, `tests/specs/component-clamp.spec.js`
  - anchors: css selector `^(\.nav-link|#menuToggle|#themeToggle|\.hero-cta \.btn|\.featured-card|\.featured-blurb|#projectGrid \.project-card|\.project-blurb|#contactActions a|\.scroll-hint|\.strength-card::before)`의 비색 선언, 그리고 `:hover`·`:active`
  - requiredCommands:
    - 23 = `RBRANCH 23 tests/helpers/component-state.js,tests/specs/component-hit.spec.js`, `DI`, `T component-hit.spec.js GS`
    - 24 = `RBRANCH 24 tests/helpers/state-sequence.js,tests/specs/state-sequence.spec.js`, `T state-sequence.spec.js component-hit.spec.js`
    - 25 = `RBRANCH 25 tests/scripts/make-state-colors.mjs,tests/fixtures/component-state-colors.json,tests/specs/state-colors.spec.js`, `W node tests/scripts/make-state-colors.mjs --check`, `T state-colors.spec.js state-sequence.spec.js`
    - 26 = `RBRANCH 26 tests/specs/component-hover.spec.js`, `DI`, `W node tests/scripts/make-state-colors.mjs --check`, `T component-hover.spec.js state-sequence.spec.js state-colors.spec.js component-hit.spec.js GS`
    - 27 = `RBRANCH 27 tests/specs/component-clamp.spec.js`, `DI`, `T component-clamp.spec.js component-hover.spec.js component-hit.spec.js GS`
- D · port 4178 · steps `[28, 29]`
  - files: `js/main.js`, `css/style.css`, `tests/specs/focus-modal.spec.js`, `tests/specs/focus-lightbox.spec.js`
  - anchors:
    - js `fn:trapFocus`, `fn:openProjectModal`, `fn:closeProjectModal`, `fn:ensureLightbox`, `fn:openLightbox`, `fn:closeLightbox`, `listener:document:keydown`, `listener:lightbox:keydown`
    - css selector에 `:focus-visible`가 있는 rule
  - requiredCommands:
    - 28 = `T focus-modal.spec.js`
    - 29 = `T focus-lightbox.spec.js focus-modal.spec.js GS`
- E · port 4179 · steps `[30]`
  - files: `css/style.css`, `tests/specs/print.spec.js`
  - anchors: css at-rule chain `@media print` 안의 rule
    - `.featured-blurb`와 카드 blurb에 `-webkit-line-clamp: unset`을 반드시 포함한다. C(27)의 clamp에 대응하기 위해서다.
  - requiredCommands: 30 = `T print.spec.js GS`
- wave 2 contract는 검증된 manifest에서 만든다.
  - lane id = shard id(`s1`~`s5`), port 4180~4184, steps `[]`, checkpoint는 `[]` 대신 `focus` 1개
  - files·anchors는 shard 값 그대로다
  - requiredCommands = `COLLECT_CHAIN --out tests/.tmp/axe-shard.json`, 그리고 shard 안 nested change의 `requiredCommands`
  - importOrder는 shard id 오름차순이다.

## C6. record envelope

- `canon(v)`: 객체 키를 코드 단위 순서로 재귀 정렬한다.
- `payloadBytes` = `JSON.stringify(canon(payload), null, 2) + '\n'`
- `payloadSha256` = sha256(payloadBytes)
- 파일 bytes = `JSON.stringify({ schemaVersion: 1, payload: canon(payload), payloadSha256 }, null, 2) + '\n'`. envelope 자체는 hash하지 않는다.
- runtime과 external은 byte 단위로 같아야 한다.
- payload 필드: `{wave, phase, runId, waveBase, parallelBase, integrationCommit, integrationTree, compositeTree, importOrder, manifestSha256|null, lanes: [{id, steps, port, worktree, branch, baseSha, laneCommit, diffSha256, files, anchors, pid, sessionId, commands: [{step, cmd, exit}], checkpoints: [{step, result}], result, cleanup}]}`
- `cleanup`은 기록 시점에 항상 `pending`이다.
- 실제 cleanup은 Harness verify step(2·4)이 PASS한 뒤에만 한다. 대상은 exact `git worktree remove <worktree>`와 `git branch -D <branch>`이고, 결과는 `<SCR>/cleanup-<w>.json`에 남긴다. 실패했거나 결과가 불명확한 lane은 보존한다.

## C7. wave 2 manifest·색 범위 (step 3)

- `tests/.tmp/a11y-wave/components.json` = `{schemaVersion: 1, collectedSha256, rules, shards: [{id, files, anchors, targets: [{key, target}]}], changes: [...]}`
- `changes`는 tagged union이다:
  - `{type: 'color-declaration', shard, file: 'css/style.css', selectors, prop, base, to, targets}`
    - `to`는 기존 color token `var(--x)`만 허용한다.
  - `{type: 'nested-interactive', shard, file: 'js/main.js', anchor, before, after, interaction, targets, requiredCommands}`
    - `anchor`는 §C4 JS anchor다.
    - `before`·`after`는 카드 article과 내부 `button.project-more`의 role·tabindex·aria 구조 계약이다.
    - `interaction`은 card click 위임으로 모달이 열리는지, keyboard로 모달 진입과 닫힌 뒤 트리거 복귀가 되는지에 대한 계약이다.
    - `requiredCommands`는 정확히 `T modal-regression.spec.js featured.spec.js focus-modal.spec.js focus-lightbox.spec.js component-hit.spec.js`다.
- 색 후보 선택: 6 project 모두에서 axe를 통과하는 token 중, 양 테마에서 base 계산색과의 sRGB 거리 합이 가장 작은 것. 동률이면 token 이름의 코드 포인트 순서. 해결할 수 없으면 `color-scope-themes-required:{target}`로 중단한다.
- rule이 color-contrast·nested-interactive 밖이면 `a11y: out-of-scope-rule:{ruleId}`로 중단·보고하고 수정하지 않는다.
- shard는 anchor 연결 성분이다. 5개를 넘으면 anchor가 처음 등장한 순서로 인접 성분을 병합한다. id는 `s1`부터 순서대로 붙인다.
- `HOO81_COLOR_V52_ALLOW`(`tests/helpers/design-guard-color-rules.js` export)에는 `color-declaration`만 `{file, selectors, prop, base, to}`로 정렬해 투영한다. nested 항목은 절대 넣지 않는다.
  - guard는 그 정확한 위치에서 값이 `base` 그대로이거나 정확히 `to`인 경우만 색 규칙에서 제외한다.
  - `component-hover.spec.js`는 이 상수에 대응하는 측정 id·prop만 BASE fixture 비교에서 제외한다.
- `validate-manifest` 검사 항목:
  - collected 파일 bytes sha256 = `collectedSha256`, `schemaVersion` 1
  - `rules` ⊆ {color-contrast, nested-interactive}이고 collected의 실제 rule 집합과 같음
  - collected의 모든 (key, target)이 정확히 shard 1개에 배정됨(중복·누락 0)
  - shard 수 5 이하, id는 `s1..sn` 순서
  - files·anchors 형식
  - change `type`은 두 종류만, 필드 집합 정확
  - color target 집합 = color-declaration targets 합집합, nested target 집합 = nested-interactive targets 합집합
  - 각 change의 `shard`가 존재하고 그 shard의 targets를 포함함
  - `HOO81_COLOR_V52_ALLOW`가 import 결과로 color 투영과 정확히 같음
  - 위반 0이면 `rules: []`, `shards: []`, `changes: []`만 허용하고, 이때 `HOO81_COLOR_V52_ALLOW`도 `[]`
