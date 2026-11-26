# HOO-81 color-resume 설계 (v52 색 결정 · v56 필수 범위 · v57 direct worktree · v58·v59 Astra 교정)

- phase: `HOO-81-portfolio-redesign-color-resume`(step 0~9).
- 유효하며 수정하지 않는 설계: 원 설계 `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md`(§n)와 resume 설계 `docs/superpowers/specs/2026-11-24-portfolio-redesign-resume-design.md`(§R n). 이 문서의 절은 `§C n`이다.
- 결정:
  - `representative-color-scope-v52`: color-contrast 위반은 기존 token을 쓴 최소 색 변경으로 고친다.
  - `final-required-scope-parallel-v56`: resume 18~30이 필수 범위다.
  - `executable-direct-worktree-v57`: Harness 2.0.1은 linked worktree를 project root로 받지 않고 parallel runner도 없다. 그래서 direct Claude worktree worker가 작업하고 canonical Harness가 검증한다.
  - Astra `a39a4d9240abbbdf8a3f29d6462cc8cd3cce67f8279821b9e150addb418852c9`(v58 반영)와 `e2ad56c8b033430a14c85b3516e09cf3202c0ca7c34f7138499fbb8df1803a24`(v59, major 8건)을 반영했다. 대응표는 §C11에 있다.
  - v57·v58 계획 commit은 리뷰 이력으로 보존한다.
- BASE_HEAD(불변): `aa6f37c803ffaf8712418e94971ed4567e2a390d`. 이력 commit: `1d5d27b0377ef575b9e54d79b7f8178e9af3daad`, `dce163d89666acdd30a49705ebc4e93c6dba4636`.
- 승계하며 다시 실행하지 않는 것:
  - 원 phase: step 0~39 completed, 40 blocked
  - resume phase: step 0~16 completed, 17 blocked
  - 이력 seed: pairs `tests/.tmp/axe-classify/pairs.json`(sha256 `1ba8778ab6cc9254b4404a5349f53c4463c0c55e4a1b2b447eac02a8bd8acaa1`), collected `tests/fixtures/axe-collected.json`(sha256 `ff7c76a6214034251f5ebc028706b9ae383ec6ecb9ce8a4c3ed97e266672e63c`). 당시 분류는 color 12 pair/61, nested 13 pair/78이다. 정본은 step 7의 final collect다.
- 작업 지시서: `phases/HOO-81-portfolio-redesign-resume/step18.md`~`step30.md`를 읽기 전용으로 승계한다(허용 anchor·RED spec·AC·§R10·§R11). 내용은 복사하지 않는다.
- 보존 대상: 텍스트·숫자, 서체 asset·weight, 6개 섹션, PROJECTS 13개와 순서, 이미지·아이콘, 이미 완료된 레이아웃·컴포넌트·간격·타이포.
- 금지: 팔레트 재설계, 새 token, 리터럴 색, `css/themes.css` 변경.
- §C FLOW:
  1. materialize → plan-only commit → GPT-6 Astra 리뷰 1회(비차단 개선은 HOO-107로)
  2. 새 대표 exact 승인
  3. Harness step 0~5
  4. `COORD_WAVE1`(§C10) → step 6 → `COORD_CLEANUP 1`
  5. step 7 → `COORD_WAVE2` → step 8 → `COORD_CLEANUP 2`
  6. step 9
  7. exact-commit Astra CLEAN → feature push → OPEN PR → tested = reviewed = pushed = PR-head SHA 확인
  - 진행 보고는 시작·fan-out·실패/재시도·통합·최종 검증·완료 때만 한다.

## C1. 불변·금지·시간

- 원 §9와 resume §R1을 유지한다. 원·resume phase, 두 설계 문서, `CLAUDE.md`, `tests/fixtures/axe-collected.json`은 읽기만 한다.
- 금지:
  - `git reset/restore/checkout/clean`, 광범위 삭제
  - main 직접 변경, merge, cherry-pick, deploy
  - runner·worker push
  - Harness linked root 호출, Harness 내부 함수 호출
- 허용되는 git 쓰기는 두 가지뿐이다.
  - Harness runner의 step commit
  - `parallel-wave.mjs`의 `--apply` 명령: `worktree add`, lane local commit, canonical `git apply --index`, integration commit, retry base `commit-tree`, cleanup의 exact `worktree remove`·`branch -D`
- composite 계산은 `tests/.tmp/parallel/idx-*`를 임시 `GIT_INDEX_FILE`로 써서 `read-tree`·`apply --cached`·`write-tree`로 한다. 만드는 것은 git object뿐이고 ref·canonical index·worktree는 바꾸지 않는다.
- worker는 git 쓰기를 하지 않는다.
- 시간:
  - 모든 step의 agent 예상 작업 시간은 **20분 이하**이고, 근거는 각 step 문서에 적는다.
  - 이와 별개로 **Harness hard timeout은 30분**이다.
  - 테스트 subprocess timeout은 기존 설정(`tests/playwright.config.js`, 각 spec의 `test.setTimeout`)을 따르며 agent 예상 시간과 구분한다.
  - Harness step은 background worker를 기다리지 않는다.

## C2. 약어

- `XSNAP k` = `python3 -I tests/scripts/start-snapshot.py step{200+k}`
- `XGATE k <A> [<R>]` = `W node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step{200+k}.json --allow <A> [--require-absent <R>]`
- `PREFLIGHT` = `python3 -I - <<'PY'` + §C3 블록 + `PY`
- `PW` = `W node tests/scripts/parallel-wave.mjs`
- `SCR_PREFIX` = `/Users/hoon/.hermes/profiles/ryan/cache/scratch/HOO-81-parallel-`
- runId는 `^[a-z0-9]{6,32}$`를 만족해야 한다. runRoot는 `SCR_PREFIX + runId`와 정확히 같아야 한다.
- `W`·`T`·`FULL`·`VS`·`DI`·`GS`·`AXE`·`COLLECT_CHAIN`은 원 §8.5 정의를 따른다. `REQ`·`RBRANCH`는 resume §R10·§R11을 따른다.

## C3. step 0 preflight 블록

```
import hashlib, json, os, subprocess, sys
BASE_HEAD = 'aa6f37c803ffaf8712418e94971ed4567e2a390d'
HIST = ('1d5d27b0377ef575b9e54d79b7f8178e9af3daad', 'dce163d89666acdd30a49705ebc4e93c6dba4636')
PLAN = ('docs/superpowers/specs/2026-11-25-portfolio-redesign-color-resume-design.md', 'tests/scripts/verify-scope.mjs', 'tests/specs/verify-scope-resume.spec.js', 'tests/playwright.config.js', 'tests/specs/smoke.spec.js')
PROTECTED = ('phases/HOO-81-portfolio-redesign/', 'phases/HOO-81-portfolio-redesign-resume/', 'docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md', 'docs/superpowers/specs/2026-11-24-portfolio-redesign-resume-design.md', 'CLAUDE.md', 'tests/fixtures/axe-collected.json')
HASH = {'tests/.tmp/axe-classify/pairs.json': '1ba8778ab6cc9254b4404a5349f53c4463c0c55e4a1b2b447eac02a8bd8acaa1', 'tests/fixtures/axe-collected.json': 'ff7c76a6214034251f5ebc028706b9ae383ec6ecb9ce8a4c3ed97e266672e63c'}
NEW = ['tests/scripts/parallel-wave.mjs'] + ['tests/helpers/parallel-wave-%s.js' % m for m in ('contract', 'anchor', 'run', 'record', 'manifest')] + ['tests/specs/parallel-wave.spec.js'] + ['tests/specs/parallel-wave-%s.spec.js' % m for m in ('contract', 'anchor', 'run', 'record', 'manifest')]
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
need = ['tests/package.json', 'tests/playwright.config.js', 'tests/node_modules/@playwright/test/index.js', 'tests/scripts/with-env.sh', 'tests/scripts/start-snapshot.py', 'tests/scripts/scope-snapshot.mjs', 'tests/scripts/verify-scope.mjs', 'tests/scripts/make-fixtures.mjs', 'tests/helpers/css-parse.js', 'tests/helpers/axe.js', 'tests/helpers/axe-prepare.js', 'tests/helpers/theme.js', 'tests/helpers/design-guard.js', 'tests/helpers/design-guard-color-rules.js', 'tests/specs/design-guard-color-rules.spec.js', 'tests/specs/axe.spec.js', 'tests/specs/smoke.spec.js', 'tests/specs/verify-scope-resume.spec.js', 'css/themes.css'] + ['phases/HOO-81-portfolio-redesign-resume/step%d.md' % n for n in range(18, 31)]
miss = [p for p in need if not os.path.isfile(p) or os.path.islink(p)]
if miss:
    sys.exit('preflight: missing:' + ','.join(miss))
late = [p for p in ['tests/fixtures/axe-baseline.json', 'tests/fixtures/axe-remediation-plan.json'] + NEW if os.path.lexists(p)]
if late:
    sys.exit('preflight: output-exists:' + ','.join(late))
print('color-resume-preflight: OK')
```

## C4. `parallel-wave.mjs` CLI 공통 규칙

- 진입점은 `tests/scripts/parallel-wave.mjs` 하나다. 하위 명령은 `tests/helpers/parallel-wave-{contract,anchor,run,record,manifest}.js`에 구현하고, 진입점은 dispatch만 한다.
- 쓰기를 하는 명령은 모두 `--apply`가 있어야 한다: `prepare`, `run-workers`, `commit-lane`, `plan-retry`, `fan-in`, `commit-integration`, `record`, `cleanup`.
  - `--apply`가 없으면 stdout에 정렬된 JSON preview만 낸다. canonical의 파일·index·ref와 runRoot 모두 바뀌지 않는다.
  - 예외: §C1의 임시 index object 생성은 dry-run에서도 허용한다.
- 출력 규칙:
  - 성공: stdout `parallel-wave <sub>: OK …`, exit 0
  - 계약 위반: stderr `parallel-wave: <code>:<detail>`, exit 1
  - 인자 오류: exit 2
- `--apply`로 runRoot에 쓰는 명령은 먼저 runRoot가 `SCR_PREFIX` + 유효한 runId로 이루어진 absolute 경로인지 검증한다. 아니면 `runroot:invalid`.
- 하위 명령 시그니처:
  - `doctor [--claude-bin <path>] [--help-text <file>]`
    - `--help`에 `-p`·`--print`, `--permission-mode`, `--allowedTools`, `--max-turns`, `--add-dir`, `--setting-sources`, `--output-format`이 모두 있어야 한다.
    - `git worktree list`가 동작하고, canonical의 `tests/node_modules/@playwright/test/index.js`와 `tests/.pw-browsers`가 있어야 한다.
    - 127.0.0.1 포트 4174~4184가 모두 거부 상태여야 한다.
    - env에 `OPENROUTER_API_KEY`·`ANTHROPIC_BASE_URL`이 없어야 한다.
    - 생성되는 argv에 `--bare`·`--dangerously-skip-permissions`가 들어갈 수 없게 코드 상수로 금지한다.
  - `prepare --wave <w> --run-root <r> --base <sha> --lanes <ids> [--attempt <a>] [--apply]`
    - 기본 attempt는 `a0`이다.
    - lane마다 worktree `<r>/lane-<id>-<a>`, branch `hoo81-<run>-w<w>-<id>-<a>`, port, evidence `<r>/evidence/<id>-<a>/`, prompt, argv를 정한다.
    - argv = `claude -p <prompt> --setting-sources user --permission-mode acceptEdits --add-dir <evidence> --max-turns 200 --output-format json --allowedTools <Read,Glob,Grep,Edit,Write + requiredCommands 각 Bash(<정확한 명령>) + Bash(git diff:*) + Bash(git status:*)>`
    - `--apply`일 때만 `git worktree add -b <branch> <worktree> <base>`를 실행하고, lane worktree에 symlink `tests/node_modules`·`tests/.pw-browsers` → canonical을 만들고, prompt 파일과 `<r>/run-<w>.json`의 attempt 항목을 쓴다.
    - wave 2는 `validate-manifest`를 통과해야 한다. 아니면 `prepare:manifest-invalid`.
  - `run-workers --wave <w> --run-root <r> --lanes <ids> [--attempt <a>] [--apply]`: §C7 참조.
  - `commit-lane --wave <w> --run-root <r> --lane <id> [--attempt <a>] [--apply]`
    - worktree의 `git status --porcelain`이 보여주는 변경 파일이 contract 파일 집합 안에 있어야 한다.
    - `git -C <wt> add -- <정렬된 exact files>`, 이어서 `git -C <wt> commit -m 'HOO-81 wave<w> lane <id> <a>'`.
    - laneCommit을 run JSON에 기록한다.
  - `validate-lane --wave <w> --run-root <r> --lane <id> [--attempt <a>]`: §C5·§C6 참조.
  - `check-overlap --wave <w> --run-root <r> --lanes <ids>`: §C6 참조.
  - `plan-retry --wave <w> --run-root <r> (--overlap | --spec <file>) [--apply]`: §C7 참조.
  - `fan-in --wave <w> --run-root <r> --canonical <repo> --lanes <ids> [--stage prologue|wave] [--apply]`
    - `check-overlap`을 통과해야 한다.
    - importOrder에 따라 각 lane의 adopted attempt 패치를 쌓는다.
    - dry-run은 composite tree만 출력한다.
    - `--apply`면 canonical에서 `git apply --index --check`, `git apply --index`를 차례로 실행한 뒤 `git write-tree` = composite인지 확인한다(`fan-in:bytes`). 마지막으로 `<r>/fanin-<w>-<stage>.json`을 쓴다.
  - `commit-integration --wave <w> --run-root <r> --stage prologue|wave [--apply]`
    - canonical index tree가 fanin JSON의 composite와 같아야 한다.
    - `git commit -m 'HOO-81 color-resume wave<w> <stage> integration'`.
  - `record --wave <w> --run-root <r> [--manifest <p>] [--apply]`: §C8 참조.
  - `verify-record --wave <w> (--current | --runtime <p> --external <p>) [--manifest <p>]`: §C8 참조.
  - `validate-manifest --collected <p> --manifest <p>`: §C9 참조.
  - `cleanup --wave <w> --run-root <r> [--apply]`
    - 먼저 `verify-record --current`가 PASS해야 한다.
    - adopted attempt와 폐기된 attempt 모두에 대해 exact `git worktree remove <path>`, `git branch -D <branch>`를 실행한다.
    - 결과는 `<r>/cleanup-<w>.json`에 쓴다. 실패·불명 항목은 보존한다.

## C5. lane contract와 fileRules

- fileRules는 tagged union이다.
  - `{type: 'existing-css', path, anchors: [regex on owner]}`: 비색 선언만 허용한다. color 계열 prop(`color`, `background-color`, `border-color`, `outline-color`, `fill`, `stroke`)의 추가·변경은 `fileRule:color-forbidden`이다.
  - `{type: 'existing-js', path, anchors: [regex on owner path], linePatterns?}`
  - `{type: 'existing-html', path, anchors: [regex on id path]}`
  - `{type: 'data-featured', path: 'js/data.js', projects: [1, 5, 7]}`
    - 추가된 줄은 정확히 3줄 `featured: true,`이고, 각각 PROJECTS[1]·[5]·[7] 객체 소속이어야 한다.
    - 삭제 줄 0, 그 밖의 변경 0.
  - `{type: 'new-test' | 'new-helper' | 'new-script', path, requiredImports, requiredExports, minTests?, forbidden}`
    - base에는 없어야 하고, result 파일 전체를 허용한다.
    - 기본 forbidden 패턴:
      - git 쓰기 동사(`add`, `commit`, `push`, `checkout`, `reset`, `restore`, `clean`, `merge`)
      - `npm (i|install|ci)`
      - 127.0.0.1·base.invalid 이외의 http(s) URL
      - `tests/.tmp/` 밖을 대상으로 하는 `rmSync`
  - `{type: 'json-structured', path, schema: 'component-state-colors'}`
    - 최상위 키는 테마 `dark`·`light`.
    - 그 아래 id는 `hero-cta-btn-<i>`, `grid-card-0`, `grid-card-1`.
    - 그 아래 상태는 3개, 각 상태는 `{backgroundColor, borderColor, color}` 문자열.
    - 키 정렬, 2칸 들여쓰기, 끝 개행 1.
    - 값은 lane에서 필수인 `W node tests/scripts/make-state-colors.mjs --check`의 exit 0으로 증명한다. hunk anchor 판정은 쓰지 않는다.
- `WAVE1_CONTRACT`(코드 상수). importOrder는 `['A','B','C','D','E']`. P는 prologue다.
- **P** · port 4174 · steps `[18]`
  - fileRules:
    - existing-html `index.html`: anchors `^hero(>heroFeatured.*)?$`. `#heroStats` 다음 형제로 `#heroFeatured` subtree를 추가하는 것만 허용.
    - data-featured `js/data.js`
    - existing-js `js/main.js`: anchors `^module>fn:renderFeaturedProjects`, `^module>fn:openProjectModal`, `^module>listener:heroFeatured:(click|keydown)`. `module` 직속 추가 줄은 linePatterns `^\\s*renderFeaturedProjects\\(\\);?$`만 허용.
    - existing-css `css/style.css`: anchors `\\.featured-`, 그리고 `.project-card`를 포함한 기존 rule의 selector 목록에 `.featured-card` 대응을 추가하는 것
    - new-test `tests/specs/featured.spec.js`: requiredImports `@playwright/test`, minTests 1
  - requiredCommands: 18 = [`DI`, `T featured.spec.js GS`]
- **A** · port 4175 · steps `[19, 20]`
  - fileRules:
    - existing-html `index.html`: `^hero(>.*)?$`
    - existing-js `js/main.js`: `module` linePatterns `^\\s*setText\\('heroTagline', PROFILE\\.tagline\\);$`만
    - existing-css `css/style.css`: `(\\.hero|#hero|\\.stat|\\.featured-)` 그리고 `@media (min-width: 1024px)` chain 안의 같은 selector
    - new-test `tests/specs/hero.spec.js`, `tests/specs/hero-layout.spec.js`
  - requiredCommands:
    - 19 = [`DI`, `T hero.spec.js GS`]
    - 20 = [`RBRANCH 20 tests/specs/hero-layout.spec.js`, `DI`, `T hero-layout.spec.js hero.spec.js GS`]
- **B** · port 4176 · steps `[21, 22]`
  - fileRules:
    - existing-html `index.html`: `^(about|career|projects|strengths|contact|nav.*|siteNav.*)(>.*)?$` 그리고 `.scroll-hint` 요소 줄
    - existing-js `js/main.js`: `^module>fn:onScroll`, skill-group 렌더 블록 `^module>render:skillsGrid`
    - existing-css `css/style.css`: `^(section|\\.section|#career|#projects|#strengths|#about|#contact|\\.career|#projectGrid|#strengthsGrid|#skillsGrid|\\.subsection-title|h2)`
    - new-test `tests/specs/structure.spec.js`, `tests/specs/layout.spec.js`
  - requiredCommands:
    - 21 = [`DI`, `T structure.spec.js GS`]
    - 22 = [`DI`, `T layout.spec.js GS`]
- **C** · port 4177 · steps `[23, 24, 25, 26, 27]`
  - fileRules:
    - existing-css `css/style.css`: `(\\.nav-link|#menuToggle|#themeToggle|\\.hero-cta \\.btn|\\.featured-card|\\.featured-blurb|#projectGrid \\.project-card|\\.project-blurb|#contactActions a|\\.scroll-hint|\\.strength-card::before)`, 그리고 각각의 `:hover`·`:active`. `.strength-card::before` rule은 통째 삭제만 허용.
    - new-helper `tests/helpers/component-state.js`: exports `waitForFiniteAnimations`, `measureState`
    - new-helper `tests/helpers/state-sequence.js`: exports `measureStateSequence`
    - new-script `tests/scripts/make-state-colors.mjs`: `--check` 지원
    - json-structured `tests/fixtures/component-state-colors.json`
    - new-test `tests/specs/component-hit.spec.js`, `tests/specs/state-sequence.spec.js`, `tests/specs/state-colors.spec.js`, `tests/specs/component-hover.spec.js`, `tests/specs/component-clamp.spec.js`
  - requiredCommands:
    - 23 = [`RBRANCH 23 tests/helpers/component-state.js,tests/specs/component-hit.spec.js`, `DI`, `T component-hit.spec.js GS`]
    - 24 = [`RBRANCH 24 tests/helpers/state-sequence.js,tests/specs/state-sequence.spec.js`, `T state-sequence.spec.js component-hit.spec.js`]
    - 25 = [`RBRANCH 25 tests/scripts/make-state-colors.mjs,tests/fixtures/component-state-colors.json,tests/specs/state-colors.spec.js`, `W node tests/scripts/make-state-colors.mjs --check`, `T state-colors.spec.js state-sequence.spec.js`]
    - 26 = [`RBRANCH 26 tests/specs/component-hover.spec.js`, `DI`, `W node tests/scripts/make-state-colors.mjs --check`, `T component-hover.spec.js state-sequence.spec.js state-colors.spec.js component-hit.spec.js GS`]
    - 27 = [`RBRANCH 27 tests/specs/component-clamp.spec.js`, `DI`, `T component-clamp.spec.js component-hover.spec.js component-hit.spec.js GS`]
- **D** · port 4178 · steps `[28, 29]`
  - fileRules:
    - existing-js `js/main.js`: `^module>fn:(trapFocus|openProjectModal|closeProjectModal|ensureLightbox|openLightbox|closeLightbox)`, `^module>listener:(document|lightbox|projectGrid):keydown`
    - existing-css `css/style.css`: selector에 `:focus-visible`가 들어간 rule만. outline·outline-offset 선언만 허용.
    - new-test `tests/specs/focus-modal.spec.js`, `tests/specs/focus-lightbox.spec.js`
  - requiredCommands:
    - 28 = [`T focus-modal.spec.js`]
    - 29 = [`T focus-lightbox.spec.js focus-modal.spec.js GS`]
- **E** · port 4179 · steps `[30]`
  - fileRules:
    - existing-css `css/style.css`: chain `^@media print` 안의 rule만. `.featured-blurb`와 카드 blurb에 `-webkit-line-clamp: unset`이 반드시 있어야 한다.
    - new-test `tests/specs/print.spec.js`
  - requiredCommands: 30 = [`T print.spec.js GS`]
- wave 2 contract는 검증된 manifest에서 도출한다(step 5).
  - lane id = shard id `s1`~`s5`, port 4180~4184
  - steps `['focus']`, checkpointSteps `['focus']`
  - requiredCommands = `{focus: ['COLLECT_CHAIN --out tests/.tmp/axe-shard.json', …shard 안 nested change의 requiredCommands]}`
  - fileRules:
    - color-declaration마다 existing-css. anchor = 정확한 `chain|selectors|prop`, `to` 값 변경만 허용, `fileRule:color-forbidden`은 이 선언에만 해제.
    - nested-interactive마다 existing-js. anchor = change.anchor.
  - importOrder는 shard id 오름차순이다.

## C6. line ownership과 경계 검증

- base와 result 파일 각각에 결정적인 owner map(줄 → owner 문자열)을 만든다.
  - **CSS**: `css-parse.js`의 rule 경계를 쓴다. owner = `<at-rule chain>|<selectors>`, 선언 줄은 `|<prop>`를 덧붙인다. rule 사이의 빈 줄과 주석은 `gap`이다.
  - **JS**: 문자열·template literal(`${}` 포함)·주석·정규식 literal을 인식하는 brace-depth 스캐너를 쓴다. 블록 머리 시그니처로 owner를 정한다.
    - `function N(` → `fn:N`
    - `X.addEventListener("E"` → `listener:X:E`
    - `X.innerHTML =` → `render:X`
    - `const N =` → `const:N`
    - 그 밖의 블록은 `block`
    - owner = `module>…` 경로이고, 최상위 IIFE 본문이 `module`이다.
  - **HTML**: tag tokenizer를 쓴다. owner = 조상 중 id가 있는 요소들의 경로(`a>b`)이고, id가 없으면 `body`다.
- 판정:
  - 삭제된 base 줄 전부(base map)와 추가된 result 줄 전부(result map)의 owner가 그 fileRule anchors 중 하나와 일치해야 한다.
  - owner가 `gap`인 줄은 같은 hunk 안의 앞뒤 줄 owner가 모두 허용될 때만 허용한다.
  - 다음은 모두 fail-closed다.
    - 해석 불가 → `anchor:unparsable`
    - 경계 밖 → `anchor:outside`
    - 한 hunk가 허용 owner와 금지 owner에 걸침 → `anchor:cross-boundary`
    - 다른 owner의 블록 머리·닫는 brace·tag를 삭제하거나 추가 → `anchor:cross-boundary`
- overlap 판정: lane 쌍 사이에 다음 중 하나라도 있으면 overlap이다. 같은 파일이어도 hunk가 disjoint이고 owner가 다르면 허용한다.
  - 같은 파일에서 base 줄 범위가 교차하는 hunk
  - 변경 줄의 owner(삭제·추가 모두)가 같음
  - 출력: `overlap:<a>,<b>:<file>:<owner|lines>`
- `validate-lane`이 확인하는 것:
  - adopted attempt commit의 first parent가 attempt.baseSha여야 한다(`lane:bad-base`).
  - diff는 `git diff --binary --no-renames base commit`이고, 그 sha256을 기록한다.
  - 변경 파일 = fileRules 경로의 부분집합이어야 한다(`lane:files`).
  - 유형별 검사와 §C6 판정을 통과해야 한다(`fileRule:*`, `anchor:*`).
  - checkpoint 파일 `<evidence>/checkpoint-<step>.json` = `{lane, attempt, step, commands: [{cmd, exit}], result}`.
    - step 집합 = contract checkpointSteps(`lane:checkpoints`)
    - 각 commands의 cmd 목록 = requiredCommands[step] exact이고 모두 exit 0(`lane:commands:<step>`)
    - result는 `pass`

## C7. worker 실행·retry 모델

- `run-workers --apply` 동작(Node `child_process.spawn`):
  1. lane마다 `cwd = worktree`, env = 현재 env + `PW_PORT=<port>`로 띄운다. stdout은 `<evidence>/result.json`, stderr는 `<evidence>/stderr.log`로 보낸다. `detached: false`.
  2. 띄우자마자 PID와 startedAt을 run JSON에 쓴다.
  3. 30초마다 checkpoint 파일의 수와 mtime을 poll한다.
  4. 마지막 진전 뒤 1200초 동안 변화가 없으면 그 자식 PID에만 SIGTERM을 보내고, 10초 뒤에도 살아 있으면 SIGKILL을 보낸다. 상태는 `stalled`.
  5. 모든 자식이 끝날 때까지 기다린다. 결과 판정:
     - exit 0이고 result.json이 JSON이며 `is_error !== true`이면 `finished`
     - 그 밖은 `failed`
  6. sessionId는 result.json의 `session_id`에서 기록한다.
  7. 전부 `finished`면 exit 0, 아니면 lane 목록을 내고 exit 1.
- run JSON `<r>/run-<w>.json` 형식:
  - 최상위: `{schemaVersion: 1, wave, runId, runRoot, lanes: {<id>: {attempts: [...], adoptedAttemptId}}}`
  - attempt: `{attemptId, worktree, branch, baseSha, port, evidence, argvSha256, pid, sessionId, startedAt, endedAt, exitCode, status, laneCommit}`
- `plan-retry --overlap --apply`:
  - overlap 쌍 중 importOrder상 뒤 lane 하나를 고른다.
  - 새 base = 앞선 lane들의 adopted 패치를 parallelBase에 쌓은 composite tree로 `git commit-tree <tree> -p <parallelBase>`를 만든 commit이다.
  - 그 lane에 attempt `r1`을 추가하고 stdout에 `<lane> r1 <baseSha>`를 출력한다.
  - r1이 다시 overlap이거나 실패하면 `retry:exhausted:<lane>`. 그 lane을 block하고 보존한다.
- `plan-retry --spec <file> --apply`(Harness step 6이 실패했을 때):
  - owner lane = fileRules에 그 spec 경로나 spec이 import하는 lane 파일을 가진 lane.
  - 정확히 1개면 그 lane만 attempt `r1`으로 재시도한다. base = 현재 integration commit.
  - 0개나 2개 이상이면 `retry:ambiguous-owner`. GS·DI·FULL·VS 같은 공통 gate 실패는 `retry:common-gate`. 둘 다 coordinator blocker이고 자동 재시도하지 않는다.
- adopted 규칙: `validate-lane`이 PASS한 가장 마지막 attempt를 adopt한다.

## C8. record envelope와 current pointer

- `canon(v)` = 객체 키를 코드 단위 순서로 재귀 정렬한 값.
- `payloadSha256` = sha256(`JSON.stringify(canon(payload), null, 2) + '\n'`).
- 파일 bytes = `JSON.stringify({schemaVersion: 1, payload: canon(payload), payloadSha256}, null, 2) + '\n'`. envelope 자체는 hash하지 않는다.
- payload 형식:
  - 최상위: `{wave, phase, runId, runRoot, waveBase, parallelBase, integrationCommit, integrationTree, compositeTree, importOrder, manifestSha256|null, lanes: [...]}`
  - lane: `{id, steps, checkpointSteps, port, adoptedAttemptId, finalBaseSha, finalLaneCommit, attempts: [{attemptId, baseSha, laneCommit, diffSha256, files, owners, commands, checkpoints, result, status, pid, sessionId, worktree, branch}]}`
  - 빈 wave 2: `lanes: []`, `importOrder: []`, `integrationCommit = parallelBase`.
- `record --apply`가 쓰는 파일:
  - runtime `tests/.tmp/parallel/wave-<w>.json`
  - external `<r>/record-wave-<w>.json`(같은 bytes)
  - pointer `tests/.tmp/parallel/current-wave-<w>.json` = `{schemaVersion: 1, wave, runId, runRoot, runtime, external}`
- `verify-record`가 확인하는 것:
  - `--current`면 pointer를 읽고 runRoot가 `SCR_PREFIX` + runId인지 확인한다.
  - 두 파일이 byte 단위로 같다(`record:mismatch`).
  - envelope 키가 정확하다(`record:envelope`).
  - payload hash가 맞다(`record:hash`).
  - phase와 wave가 맞다(`record:phase`).
  - integrationCommit = HEAD(`record:head`).
  - waveBase·parallelBase가 HEAD의 조상이다(`record:ancestry`).
  - lane id·steps·checkpointSteps·port가 contract와 같다(`record:lanes`).
  - adoptedAttemptId가 attempts 안에 있고, finalBaseSha·finalLaneCommit이 그 attempt와 같다(`record:adopt`).
  - 각 attempt를 git object에서 다시 validate-lane 한다.
  - retry attempt의 baseSha를 importOrder에 따라 재구성한 composite commit의 tree와 대조한다(`record:attempt-base`).
  - composite 재구성 결과가 맞다(`record:composite`).
    - wave 1: `waveBase` + P 패치 = `parallelBase` tree, 그리고 `parallelBase` + A→E adopted 패치 = `integrationCommit` tree
    - wave 2: `parallelBase` + shard 패치 = `integrationCommit` tree
  - `--manifest`를 주면 manifestSha256이 맞아야 한다.

## C9. wave 2 manifest와 색 범위

- `tests/.tmp/a11y-wave/components.json` 형식: `{schemaVersion: 1, collectedSha256, rules, shards: [{id, files, anchors, targets: [{key, target}]}], changes: [...]}`
- `changes`는 tagged union이다.
  - `{type: 'color-declaration', shard, file: 'css/style.css', anchor: '<chain>|<selectors>|<prop>', selectors, prop, base, to, token, proof, targets}`
    - `proof` = `{path: 'tests/.tmp/axe-final/proof-<shard>-<n>.json', sha256}`. 6 project 각각에 대해 `to`를 주입한 상태의 axe color-contrast 통과 증거다.
  - `{type: 'nested-interactive', shard, file: 'js/main.js', anchor, before, after, interaction, targets, requiredCommands}`
    - `before`·`after`는 카드 article과 `button.project-more`의 role·tabindex·aria·data-project 구조 계약이다.
    - `interaction`은 card click 위임으로 모달이 열리는 것, keyboard로 모달에 진입하는 것, 닫은 뒤 트리거로 돌아오는 것에 대한 계약이다.
    - `requiredCommands`는 정확히 [`T modal-regression.spec.js featured.spec.js focus-modal.spec.js focus-lightbox.spec.js component-hit.spec.js`]다.
- 색 후보 규칙:
  - 6 project 모두에서 통과하는 기존 token 중, 양 테마에서 base 계산색과의 sRGB 거리 합이 가장 작은 것을 고른다. 동률이면 token 이름의 코드 포인트 순서로 정한다.
  - 해결이 안 되면 `color-scope-themes-required:{target}`로 중단한다.
- 다른 rule이 나오면 `a11y: out-of-scope-rule:{ruleId}`로 중단한다.
- shard 구성: change.anchor를 기준으로 한 연결 성분이다. 5개를 넘으면 anchor가 처음 등장한 순서로 인접 성분을 병합한다. id는 `s1`부터 순서대로 붙인다.
- `HOO81_COLOR_V52_ALLOW`(`tests/helpers/design-guard-color-rules.js`에서 export)에는 color-declaration만 `{file, selectors, prop, base, to}` 형태로 정렬해 투영한다. nested 항목은 절대 넣지 않는다.
  - guard는 그 정확한 위치에서 값이 `base`이거나 정확히 `to`일 때만 색 규칙에서 제외한다.
  - `component-hover.spec.js`는 상수에 대응하는 측정 id·prop만 BASE fixture 비교에서 제외한다.
- `validate-manifest` 검사 항목(어긋나면 각각 `manifest:<code>`):
  - collected bytes sha256과 schemaVersion
  - rules ⊆ {color-contrast, nested-interactive}이고 collected의 실제 rule 집합과 같음
  - 모든 collected (key, target)가 정확히 shard 1개에 배정됨(중복·누락 0)
  - shard 수 5 이하, id `s1..sn` 순서
  - change 필드 집합이 정확함(type은 두 종류만)
  - change.targets ⊆ 해당 shard.targets
  - change.file ∈ shard.files, change.anchor ∈ shard.anchors
  - shard.files·anchors가 그 shard의 changes에서 도출한 최소 집합과 exact equality
  - color change:
    - 대상이 color-contrast target이다
    - `css/style.css`의 base 선언이 실제로 존재하고 selector·prop·값이 일치한다
    - `to` = `var(<token>)`이고, token은 `css/style.css` 또는 `css/themes.css`에 정의된 기존 token이다
    - proof 파일 sha256이 일치하고 6 project 모두 통과다
  - nested change:
    - 대상이 nested-interactive target이다
    - anchor가 `js/main.js` owner map에 실제로 존재한다
    - `before`가 현재 렌더 결과와 일치한다
    - `after`·`interaction` 필드가 있다
    - requiredCommands가 승인된 exact 목록과 같다
  - 모든 target이 정확히 change 1개에 배정됨
  - `HOO81_COLOR_V52_ALLOW`를 import한 값이 color 투영과 같음
  - 위반 0이면 `rules: []`, `shards: []`, `changes: []`만 허용하고, 상수도 `[]`여야 함

## C10. coordinator 실행 블록 (Ryan/Hermes, canonical repo 루트, 순서 고정)

```
# COORD_WAVE1 (Harness step 5 완료 후)
set -eu
cd /Volumes/P9/dev/hoonlabs/work/HOO-81-portfolio
RUN=$(date +%Y%m%d%H%M%S)
SCR=/Users/hoon/.hermes/profiles/ryan/cache/scratch/HOO-81-parallel-$RUN
PW='sh tests/scripts/with-env.sh node tests/scripts/parallel-wave.mjs'
$PW doctor
WB=$(git rev-parse HEAD)
$PW prepare --wave 1 --run-root "$SCR" --base "$WB" --lanes P
$PW prepare --wave 1 --run-root "$SCR" --base "$WB" --lanes P --apply
$PW run-workers --wave 1 --run-root "$SCR" --lanes P --apply
$PW commit-lane --wave 1 --run-root "$SCR" --lane P --apply
$PW validate-lane --wave 1 --run-root "$SCR" --lane P
$PW fan-in --wave 1 --run-root "$SCR" --canonical "$PWD" --lanes P --stage prologue
$PW fan-in --wave 1 --run-root "$SCR" --canonical "$PWD" --lanes P --stage prologue --apply
$PW commit-integration --wave 1 --run-root "$SCR" --stage prologue --apply
PB=$(git rev-parse HEAD)
$PW prepare --wave 1 --run-root "$SCR" --base "$PB" --lanes A,B,C,D,E
$PW prepare --wave 1 --run-root "$SCR" --base "$PB" --lanes A,B,C,D,E --apply
$PW run-workers --wave 1 --run-root "$SCR" --lanes A,B,C,D,E --apply
for L in A B C D E; do
  $PW commit-lane --wave 1 --run-root "$SCR" --lane "$L" --apply
  $PW validate-lane --wave 1 --run-root "$SCR" --lane "$L"
done
if ! $PW check-overlap --wave 1 --run-root "$SCR" --lanes A,B,C,D,E; then
  set -- $($PW plan-retry --wave 1 --run-root "$SCR" --overlap --apply)
  $PW prepare --wave 1 --run-root "$SCR" --base "$3" --lanes "$1" --attempt "$2" --apply
  $PW run-workers --wave 1 --run-root "$SCR" --lanes "$1" --attempt "$2" --apply
  $PW commit-lane --wave 1 --run-root "$SCR" --lane "$1" --attempt "$2" --apply
  $PW validate-lane --wave 1 --run-root "$SCR" --lane "$1" --attempt "$2"
  $PW check-overlap --wave 1 --run-root "$SCR" --lanes A,B,C,D,E
fi
$PW fan-in --wave 1 --run-root "$SCR" --canonical "$PWD" --lanes A,B,C,D,E --stage wave
$PW fan-in --wave 1 --run-root "$SCR" --canonical "$PWD" --lanes A,B,C,D,E --stage wave --apply
$PW commit-integration --wave 1 --run-root "$SCR" --stage wave --apply
$PW record --wave 1 --run-root "$SCR"
$PW record --wave 1 --run-root "$SCR" --apply
$PW verify-record --wave 1 --current
# → Harness step 6. 실패 spec이 있으면: $PW plan-retry --wave 1 --run-root "$SCR" --spec <실패 spec 경로> --apply (owner 1개일 때만, 이후 위 prepare~record 같은 순서로 그 lane만)
# COORD_CLEANUP 1 (Harness step 6 PASS 후)
$PW cleanup --wave 1 --run-root "$SCR"
$PW cleanup --wave 1 --run-root "$SCR" --apply
```

```
# COORD_WAVE2 (Harness step 7 완료 후)
set -eu
cd /Volumes/P9/dev/hoonlabs/work/HOO-81-portfolio
RUN=$(date +%Y%m%d%H%M%S)
SCR=/Users/hoon/.hermes/profiles/ryan/cache/scratch/HOO-81-parallel-$RUN
PW='sh tests/scripts/with-env.sh node tests/scripts/parallel-wave.mjs'
M=tests/.tmp/a11y-wave/components.json
$PW doctor
$PW validate-manifest --collected tests/.tmp/axe-final/collected.json --manifest "$M"
PB=$(git rev-parse HEAD)
S=$(node -e "process.stdout.write(JSON.parse(require('fs').readFileSync('$M','utf8')).shards.map(s=>s.id).join(','))")
if [ -n "$S" ]; then
  $PW prepare --wave 2 --run-root "$SCR" --base "$PB" --lanes "$S" --manifest "$M"
  $PW prepare --wave 2 --run-root "$SCR" --base "$PB" --lanes "$S" --manifest "$M" --apply
  $PW run-workers --wave 2 --run-root "$SCR" --lanes "$S" --apply
  for L in $(echo "$S" | tr ',' ' '); do
    $PW commit-lane --wave 2 --run-root "$SCR" --lane "$L" --apply
    $PW validate-lane --wave 2 --run-root "$SCR" --lane "$L"
  done
  $PW check-overlap --wave 2 --run-root "$SCR" --lanes "$S"
  $PW fan-in --wave 2 --run-root "$SCR" --canonical "$PWD" --lanes "$S" --stage wave
  $PW fan-in --wave 2 --run-root "$SCR" --canonical "$PWD" --lanes "$S" --stage wave --apply
  $PW commit-integration --wave 2 --run-root "$SCR" --stage wave --apply
fi
$PW record --wave 2 --run-root "$SCR" --manifest "$M"
$PW record --wave 2 --run-root "$SCR" --manifest "$M" --apply
$PW verify-record --wave 2 --current --manifest "$M"
# → Harness step 8. PASS 후 COORD_CLEANUP 2
$PW cleanup --wave 2 --run-root "$SCR"
$PW cleanup --wave 2 --run-root "$SCR" --apply
```

- 어느 명령이든 실패하면 `set -e`로 멈춘다. 실패 lane과 worktree는 보존하고 blocker로 보고한다. 수동 보완은 금지다.

## C11. Astra v59 major 대응표

| # | 지적 | 반영 위치 |
|---|---|---|
| 1 | coordinator 분할 | step 1~5 |
| 2 | fileRules tagged union | §C5, step 1·2 |
| 3 | 모든 줄 경계 검증 | §C6, step 2 |
| 4 | `--apply` 일관성 | §C4, step 1·3·4 |
| 5 | retry record 모델 | §C7·§C8, step 3·4 |
| 6 | 실행 절차와 placeholder 제거 | §C10, step 3·6·8 |
| 7 | manifest 최소 권한 | §C9, step 5 |
| 8 | wave 2 checkpoint 통일 | §C5·§C8, step 4·5 |
