// 범위 검사 (설계 §8.4).
// step 22: 경로 정책. diff 인자 상수 분리(경로 = name-only, 내용 = js/data.js patch만), 읽기 전용 수집,
//          순수 판정 evaluatePaths.
// step 23: 내용 판정 checkDataJsDiff·checkSpaceGrotesk·checkGitignore·evaluateContent, evaluateScope.
//          CLI 인자 없음 → `verify-scope: OK`, `--final` → `verify-scope: OK (final)`, `--self-test`.
import { spawnSync } from 'node:child_process';
import assert from 'node:assert/strict';
import nodeFs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { BASE, RUNTIME_PREFIXES } from './scope-snapshot.mjs';

export const GIT_DIFF_PATH_ARGS = Object.freeze(['--no-renames', '--name-only']);
export const GIT_DIFF_PATCH_ARGS = Object.freeze(['--no-renames', '--unified=0']);

export const DATA_JS = 'js/data.js';
export const THEMES_CSS = 'css/themes.css';
export const ROOT_PACKAGE_JSON = 'package.json';

// §8.1 tracked(빌더 허용)
export const BUILDER_FILES = Object.freeze([
  'index.html', 'css/style.css', 'js/main.js', 'js/data.js',
  'tests/package.json', 'tests/package-lock.json', 'tests/.gitignore', 'tests/playwright.config.js',
]);
export const BUILDER_PREFIXES = Object.freeze([
  'tests/helpers/', 'tests/specs/', 'tests/fixtures/', 'tests/scripts/',
]);

// 하네스 소유: committed 면제, 미커밋 위반. (설치 state의 seed 파일 포함)
export const HARNESS_OWNED_FILES = Object.freeze([
  'CLAUDE.md', 'pytest.ini', '.python-version', '.gitattributes', '.gitignore',
  '.harness/harness.lock.json', '.harness/policy.json',
  'docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md',
  'harness-manifest.json',
  'docs/PRD.md', 'docs/UI_GUIDE.md', 'phases/index.json',
]);
export const HARNESS_OWNED_PREFIXES = Object.freeze([
  '.claude/', '.codex/', 'scripts/', 'templates/',
]);

// 런타임 면제(어느 구간이든): lock·policy 외 .harness/**, .venv/**, phase 디렉터리
export const RUNTIME_EXEMPT_PREFIXES = Object.freeze([
  '.harness/', '.venv/', 'phases/HOO-81-portfolio-redesign/',
]);

// 경로 구간: committed = BASE→HEAD, staged = HEAD→index, worktree = index→worktree, untracked
export const PATH_LAYERS = Object.freeze(['committed', 'staged', 'worktree', 'untracked']);
const PATH_DIFF_REVS = Object.freeze({
  committed: [BASE, 'HEAD'],
  staged: ['--cached', 'HEAD'],
  worktree: [],
});
// data.js patch 4구간
export const DATA_JS_INTERVALS = Object.freeze(['baseHead', 'baseIndex', 'indexWorktree', 'baseWorktree']);
const PATCH_REVS = Object.freeze({
  baseHead: [BASE, 'HEAD'],
  baseIndex: ['--cached', BASE],
  indexWorktree: [],
  baseWorktree: [BASE],
});

export const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');

export function runGit(args, { root = REPO_ROOT } = {}) {
  const r = spawnSync('git', args, { cwd: root, maxBuffer: 256 * 1024 * 1024, encoding: 'utf8' });
  if (r.error) throw r.error;
  if (r.status !== 0) throw new Error(`git ${args.join(' ')} failed: ${String(r.stderr).trim()}`);
  return r.stdout;
}

function splitZ(out) {
  return String(out).split('\0').filter((s) => s !== '');
}

// Git 읽기만. 경로 diff는 GIT_DIFF_PATH_ARGS, 내용 diff는 GIT_DIFF_PATCH_ARGS + `-- js/data.js`만.
export function collectInput({ git = runGit } = {}) {
  const paths = {};
  for (const layer of ['committed', 'staged', 'worktree']) {
    paths[layer] = splitZ(git(['diff', ...GIT_DIFF_PATH_ARGS, '-z', ...PATH_DIFF_REVS[layer]]));
  }
  paths.untracked = splitZ(git(['ls-files', '-z', '--others', '--exclude-standard']));
  const tracked = splitZ(git(['ls-files', '-z']));
  const dataJs = {};
  for (const k of DATA_JS_INTERVALS) {
    dataJs[k] = String(git(['diff', ...GIT_DIFF_PATCH_ARGS, ...PATCH_REVS[k], '--', DATA_JS]));
  }
  return { paths, tracked, dataJs };
}

const startsWithAny = (p, prefixes) => prefixes.some((x) => p.startsWith(x));

export function isRuntimePath(p) {
  return startsWithAny(p, RUNTIME_PREFIXES);
}
export function isBuilderPath(p) {
  return BUILDER_FILES.includes(p) || startsWithAny(p, BUILDER_PREFIXES);
}
export function isHarnessOwned(p) {
  return HARNESS_OWNED_FILES.includes(p) || startsWithAny(p, HARNESS_OWNED_PREFIXES);
}
export function isRuntimeExempt(p) {
  if (p === '.harness/harness.lock.json' || p === '.harness/policy.json') return false;
  return startsWithAny(p, RUNTIME_EXEMPT_PREFIXES);
}

// 순수 판정. 위반 문자열 목록(입력 순서, 중복 제거).
//   runtime-tracked:{p}            런타임 경로 추적(ls-files 또는 diff 구간)
//   root-package-json:{layer}      루트 package.json
//   themes-changed:{layer}         css/themes.css 변경
//   harness-uncommitted:{layer}:{p} 하네스 소유 미커밋 변경
//   outside-scope:{layer}:{p}      허용 밖 경로
export function evaluatePaths(input) {
  const out = [];
  const seen = new Set();
  const add = (v) => {
    if (!seen.has(v)) {
      seen.add(v);
      out.push(v);
    }
  };
  for (const p of input.tracked ?? []) {
    if (isRuntimePath(p)) add(`runtime-tracked:${p}`);
  }
  for (const layer of PATH_LAYERS) {
    for (const p of input.paths?.[layer] ?? []) {
      if (isRuntimePath(p)) {
        if (layer !== 'untracked') add(`runtime-tracked:${p}`);
      } else if (p === ROOT_PACKAGE_JSON) {
        add(`root-package-json:${layer}`);
      } else if (p === THEMES_CSS) {
        add(`themes-changed:${layer}`);
      } else if (isBuilderPath(p) || isRuntimeExempt(p)) {
        // 허용
      } else if (isHarnessOwned(p)) {
        if (layer !== 'committed') add(`harness-uncommitted:${layer}:${p}`);
      } else {
        add(`outside-scope:${layer}:${p}`);
      }
    }
  }
  return out;
}

// ---------------------------------------------------------------- step 23 내용

export const INDEX_HTML = 'index.html';
export const TESTS_GITIGNORE = 'tests/.gitignore';
export const SPACE_GROTESK = 'Space+Grotesk';
// §8.1 tests/.gitignore 정확히 7줄(끝 개행만 정규화)
export const GITIGNORE_LINES = Object.freeze([
  'node_modules/', '.npm-cache/', '.pw-browsers/', '.tmp/', 'test-results/', 'playwright-report/', 'screenshots/',
]);
export const FEATURED_LINE = 'featured: true,';
export const MAX_FEATURED = 3;
// index.html Space+Grotesk 3종 상태, gitignore 2종 상태
export const HTML_STATES = Object.freeze(['head', 'index', 'worktree']);
export const GITIGNORE_STATES = Object.freeze(['index', 'worktree']);
const SHOW_SPECS = Object.freeze({
  html: { head: `HEAD:${INDEX_HTML}`, index: `:${INDEX_HTML}` },
  gitignore: { index: `:${TESTS_GITIGNORE}` },
});
// final이면 BASE 기준 3구간은 정확히 3줄. index→worktree는 featured만·≤3줄.
const FINAL_EXACT = Object.freeze(['baseHead', 'baseIndex', 'baseWorktree']);

// 끝 개행 하나만 정규화. 추가·중복·빈 줄·순서·주석·CRLF는 모두 불일치.
export function checkGitignore(text) {
  if (typeof text !== 'string') return false;
  const body = text.endsWith('\n') ? text.slice(0, -1) : text;
  return body === GITIGNORE_LINES.join('\n');
}

export function checkSpaceGrotesk(html) {
  return typeof html === 'string' && html.includes(SPACE_GROTESK);
}

// `git diff --no-renames --unified=0 ... -- js/data.js` patch 판정.
// hunk(@@) 안의 `-` 줄 = 삭제, `+` 줄 = 추가. 헤더·`\` 줄 무시. 이름만(name-only) 출력은 추가 0줄.
// 위반(순서 고정): binary, deleted:N, added-non-featured:N, featured-count:N(>3 또는 requireExactly3이면 ≠3).
export function checkDataJsDiff(patch, { requireExactly3 = false } = {}) {
  let inHunk = false;
  let deleted = 0;
  let nonFeatured = 0;
  let featured = 0;
  let binary = false;
  for (const line of String(patch ?? '').split('\n')) {
    if (line.startsWith('diff --git ')) {
      inHunk = false;
    } else if (line.startsWith('@@')) {
      inHunk = true;
    } else if (!inHunk) {
      if (line.startsWith('Binary files ') || line.startsWith('GIT binary patch')) binary = true;
    } else if (line.startsWith('+')) {
      if (line.slice(1).trim() === FEATURED_LINE) featured += 1;
      else nonFeatured += 1;
    } else if (line.startsWith('-')) {
      deleted += 1;
    }
  }
  const out = [];
  if (binary) out.push('binary');
  if (deleted) out.push(`deleted:${deleted}`);
  if (nonFeatured) out.push(`added-non-featured:${nonFeatured}`);
  if (featured > MAX_FEATURED || (requireExactly3 && featured !== MAX_FEATURED)) out.push(`featured-count:${featured}`);
  return out;
}

function gitShowOrNull(git, spec) {
  try {
    return String(git(['show', spec]));
  } catch {
    return null;
  }
}
function readOrNull(fs, root, rel) {
  try {
    return fs.readFileSync(path.join(root, rel), 'utf8');
  } catch (e) {
    if (e && e.code === 'ENOENT') return null;
    throw e;
  }
}

// 읽기만: `git show HEAD:index.html`, `git show :index.html`, `git show :tests/.gitignore` + worktree 파일.
export function collectContentInput({ git = runGit, fs = nodeFs, root = REPO_ROOT } = {}) {
  return {
    html: {
      head: gitShowOrNull(git, SHOW_SPECS.html.head),
      index: gitShowOrNull(git, SHOW_SPECS.html.index),
      worktree: readOrNull(fs, root, INDEX_HTML),
    },
    gitignore: {
      index: gitShowOrNull(git, SHOW_SPECS.gitignore.index),
      worktree: readOrNull(fs, root, TESTS_GITIGNORE),
    },
  };
}

export function collectScopeInput({ git = runGit, fs = nodeFs, root = REPO_ROOT } = {}) {
  return { ...collectInput({ git }), content: collectContentInput({ git, fs, root }) };
}

// 순수 판정. 위반 문자열(고정 순서):
//   data-js:{interval}:{reason}   DATA_JS_INTERVALS 순
//   space-grotesk-missing:{state} head, index, worktree
//   gitignore:{state}             index, worktree
export function evaluateContent(input, { final = false } = {}) {
  const out = [];
  for (const k of DATA_JS_INTERVALS) {
    const requireExactly3 = final && FINAL_EXACT.includes(k);
    for (const v of checkDataJsDiff(input.dataJs?.[k] ?? '', { requireExactly3 })) out.push(`data-js:${k}:${v}`);
  }
  for (const s of HTML_STATES) {
    if (!checkSpaceGrotesk(input.content?.html?.[s])) out.push(`space-grotesk-missing:${s}`);
  }
  for (const s of GITIGNORE_STATES) {
    if (!checkGitignore(input.content?.gitignore?.[s])) out.push(`gitignore:${s}`);
  }
  return out;
}

export function evaluateScope(input, { final = false } = {}) {
  return [...evaluatePaths(input), ...evaluateContent(input, { final })];
}

// ---------------------------------------------------------------- self-test

const EMPTY = Object.freeze({ committed: [], staged: [], worktree: [], untracked: [], tracked: [] });

// 가짜 git: 시나리오 경로를 구간별로 돌려준다. renames = [{from, to, layer}]는
// --no-renames가 있으면 삭제+추가 두 경로, 없으면 새 경로만(rename 감지 흉내).
function fakeGit(scenario, calls = []) {
  const s = { ...EMPTY, renames: [], ...scenario };
  return (args) => {
    calls.push([...args]);
    if (args[0] === 'ls-files') {
      if (args.includes('--others')) return s.untracked.map((p) => `${p}\0`).join('');
      return s.tracked.map((p) => `${p}\0`).join('');
    }
    assert.equal(args[0], 'diff');
    if (args.includes('--unified=0')) return '';
    let layer = 'worktree';
    if (args.includes(BASE) && args.includes('HEAD')) layer = 'committed';
    else if (args.includes('--cached')) layer = 'staged';
    const list = [...s[layer]];
    for (const r of s.renames.filter((x) => x.layer === layer)) {
      if (args.includes('--no-renames')) list.push(r.from, r.to);
      else list.push(r.to);
    }
    return list.map((p) => `${p}\0`).join('');
  };
}

const evalScenario = (scenario) => evaluatePaths(collectInput({ git: fakeGit(scenario) }));

export function selfTest() {
  // 상수
  assert.deepEqual([...GIT_DIFF_PATH_ARGS], ['--no-renames', '--name-only']);
  assert.deepEqual([...GIT_DIFF_PATCH_ARGS], ['--no-renames', '--unified=0']);
  assert.ok(Object.isFrozen(GIT_DIFF_PATH_ARGS) && Object.isFrozen(GIT_DIFF_PATCH_ARGS));

  // 가짜 git 호출 기록: 경로 diff는 PATH 인자만, patch는 PATCH 인자 + data.js만
  const calls = [];
  const input = collectInput({ git: fakeGit({}, calls) });
  const diffs = calls.filter((c) => c[0] === 'diff');
  const pathCalls = diffs.filter((c) => c.includes('--name-only'));
  const patchCalls = diffs.filter((c) => c.includes('--unified=0'));
  assert.equal(pathCalls.length, 3);
  assert.equal(patchCalls.length, 4);
  assert.equal(pathCalls.length + patchCalls.length, diffs.length);
  for (const c of pathCalls) {
    assert.deepEqual(c.slice(1, 3), [...GIT_DIFF_PATH_ARGS]);
    assert.ok(!c.includes('--unified=0') && !c.includes('--'));
  }
  for (const c of patchCalls) {
    assert.deepEqual(c.slice(1, 3), [...GIT_DIFF_PATCH_ARGS]);
    assert.ok(!c.includes('--name-only'));
    assert.deepEqual(c.slice(-2), ['--', DATA_JS]);
  }
  for (const c of calls) {
    assert.ok(['diff', 'ls-files'].includes(c[0]), `read-only git: ${c.join(' ')}`);
  }
  assert.deepEqual(Object.keys(input.dataJs), [...DATA_JS_INTERVALS]);

  // 정상 0
  assert.deepEqual(evalScenario({}), []);
  assert.deepEqual(evalScenario({
    committed: ['index.html', 'tests/specs/a.spec.js', 'CLAUDE.md', '.claude/settings.json', 'docs/PRD.md'],
    staged: ['css/style.css', 'js/data.js'],
    worktree: ['js/main.js', 'tests/scripts/verify-scope.mjs'],
    untracked: ['tests/helpers/new.js'],
    tracked: ['index.html', 'tests/package.json'],
  }), []);

  // 위반
  const cases = [
    [{ worktree: ['docs/other.md'] }, ['outside-scope:worktree:docs/other.md']],
    [{ staged: ['README.md'], worktree: ['README.md'] },
      ['outside-scope:staged:README.md', 'outside-scope:worktree:README.md']],
    [{ untracked: ['assets/new.png'] }, ['outside-scope:untracked:assets/new.png']],
    [{ committed: ['assets/projects/new.jpg'] }, ['outside-scope:committed:assets/projects/new.jpg']],
    [{ untracked: ['package.json'] }, ['root-package-json:untracked']],
    [{ committed: ['package.json'] }, ['root-package-json:committed']],
    [{ worktree: ['CLAUDE.md'] }, ['harness-uncommitted:worktree:CLAUDE.md']],
    [{ staged: ['CLAUDE.md'] }, ['harness-uncommitted:staged:CLAUDE.md']],
    [{ tracked: ['tests/node_modules/x'], committed: ['tests/node_modules/x'] },
      ['runtime-tracked:tests/node_modules/x']],
    [{ tracked: ['tests/node_modules/x'] }, ['runtime-tracked:tests/node_modules/x']],
    [{ worktree: ['.harness/harness.lock.json'] }, ['harness-uncommitted:worktree:.harness/harness.lock.json']],
    [{ staged: ['.harness/policy.json'] }, ['harness-uncommitted:staged:.harness/policy.json']],
    [{ worktree: ['css/themes.css'] }, ['themes-changed:worktree']],
    [{ committed: ['css/themes.css'] }, ['themes-changed:committed']],
  ];
  for (const [scenario, expected] of cases) {
    assert.deepEqual(evalScenario(scenario), expected, JSON.stringify(scenario));
  }

  // 허용
  assert.deepEqual(evalScenario({ committed: ['scripts/harness.py'] }), []);
  assert.deepEqual(evalScenario({ untracked: ['.harness/runtime/x.json'] }), []);
  assert.deepEqual(evalScenario({ worktree: ['phases/HOO-81-portfolio-redesign/index.json'] }), []);
  assert.deepEqual(evalScenario({ worktree: ['scripts/harness.py'] }),
    ['harness-uncommitted:worktree:scripts/harness.py']);

  // rename 우회: --no-renames가 삭제 경로를 드러낸다
  const renames = [
    ['README.md', 'tests/fixtures/x.md'],
    ['assets/favicon.svg', 'tests/fixtures/f.svg'],
    ['docs/superpowers/plans/2026-07-29-quiet-executive-redesign.md', 'tests/fixtures/p.md'],
    ['.claude/settings.json', 'tests/fixtures/s.json'],
  ];
  for (const [from, to] of renames) {
    const layer = 'staged';
    const expected = from.startsWith('.claude/')
      ? [`harness-uncommitted:${layer}:${from}`]
      : [`outside-scope:${layer}:${from}`];
    assert.deepEqual(evalScenario({ renames: [{ from, to, layer }] }), expected, `${from}->${to}`);
    // 대조: rename 감지가 켜진 diff였다면 새 경로만 보여 위반이 숨는다
    const hidden = fakeGit({ renames: [{ from, to, layer }] })(['diff', '--name-only', '-z', '--cached', 'HEAD']);
    assert.equal(hidden, `${to}\0`);
    assert.deepEqual(evaluatePaths({ paths: { staged: splitZ(hidden) }, tracked: [] }), []);
  }
  for (const [from, to] of renames.slice(0, 3)) {
    assert.deepEqual(evalScenario({ renames: [{ from, to, layer: 'committed' }] }),
      [`outside-scope:committed:${from}`]);
  }
  selfTestContent();
  return 'verify-scope: self-test OK';
}

// ---------------------------------------------------------------- self-test (step 23 내용)

const GOOD_GITIGNORE = `${GITIGNORE_LINES.join('\n')}\n`;
const GOOD_HTML = '<link href="https://fonts.googleapis.com/css2?family=Inter&family=Space+Grotesk:wght@500&display=swap" />\n';
const NO_SG_HTML = '<link href="https://fonts.googleapis.com/css2?family=Inter&display=swap" />\n';

function dataPatch(added = [], deleted = []) {
  if (!added.length && !deleted.length) return '';
  const lines = [
    `diff --git a/${DATA_JS} b/${DATA_JS}`,
    'index 1111111..2222222 100644',
    `--- a/${DATA_JS}`,
    `+++ b/${DATA_JS}`,
  ];
  for (const d of deleted) lines.push('@@ -10 +9,0 @@', `-${d}`);
  added.forEach((a, i) => lines.push(`@@ -${20 + i * 10},0 +${20 + i * 10} @@`, `+${a}`));
  return `${lines.join('\n')}\n`;
}
const FEATURED = '    featured: true,';
const PATCH3 = dataPatch([FEATURED, FEATURED, FEATURED]);

// 가짜 git(내용): PATCH 인자 + `-- js/data.js`면 구간별 patch, `--name-only`면 이름만,
// `show <rev>:<path>`면 해당 상태 내용. fs는 worktree 내용.
function fakeContentGit(sc = {}, calls = []) {
  const s = {
    names: { committed: [], staged: [], worktree: [] },
    untracked: [],
    tracked: [],
    dataJs: { baseHead: PATCH3, baseIndex: PATCH3, indexWorktree: '', baseWorktree: PATCH3 },
    show: { 'HEAD:index.html': GOOD_HTML, ':index.html': GOOD_HTML, ':tests/.gitignore': GOOD_GITIGNORE },
    ...sc,
  };
  return (args) => {
    calls.push([...args]);
    if (args[0] === 'ls-files') {
      return (args.includes('--others') ? s.untracked : s.tracked).map((p) => `${p}\0`).join('');
    }
    if (args[0] === 'show') {
      assert.equal(args.length, 2);
      if (!(args[1] in s.show)) throw new Error(`missing ${args[1]}`);
      return s.show[args[1]];
    }
    assert.equal(args[0], 'diff');
    if (args.includes('--name-only')) {
      let layer = 'worktree';
      if (args.includes(BASE) && args.includes('HEAD')) layer = 'committed';
      else if (args.includes('--cached')) layer = 'staged';
      return s.names[layer].map((p) => `${p}\0`).join('');
    }
    if (args.includes('--unified=0') && args.at(-1) === DATA_JS) {
      let k = 'indexWorktree';
      if (args.includes(BASE) && args.includes('HEAD')) k = 'baseHead';
      else if (args.includes('--cached')) k = 'baseIndex';
      else if (args.includes(BASE)) k = 'baseWorktree';
      return s.dataJs[k];
    }
    throw new Error(`unexpected git ${args.join(' ')}`);
  };
}
function fakeFs(files = {}) {
  const f = { 'index.html': GOOD_HTML, 'tests/.gitignore': GOOD_GITIGNORE, ...files };
  return {
    readFileSync(p, enc) {
      assert.equal(enc, 'utf8');
      const rel = path.relative('/fake-root', p);
      if (f[rel] == null) {
        const e = new Error(`ENOENT ${rel}`);
        e.code = 'ENOENT';
        throw e;
      }
      return f[rel];
    },
  };
}
const scopeOf = (sc = {}, files = {}, opts = {}) => evaluateScope(
  collectScopeInput({ git: fakeContentGit(sc), fs: fakeFs(files), root: '/fake-root' }), opts,
);

function selfTestContent() {
  // 상수 불변
  assert.deepEqual([...GIT_DIFF_PATH_ARGS], ['--no-renames', '--name-only']);
  assert.deepEqual([...GIT_DIFF_PATCH_ARGS], ['--no-renames', '--unified=0']);

  // 수집: 읽기 전용, patch는 PATCH 인자 + data.js만, show는 HEAD/index 상태만
  const calls = [];
  const input = collectScopeInput({ git: fakeContentGit({}, calls), fs: fakeFs(), root: '/fake-root' });
  for (const c of calls) assert.ok(['diff', 'ls-files', 'show'].includes(c[0]), `read-only git: ${c.join(' ')}`);
  assert.deepEqual(calls.filter((c) => c[0] === 'show').map((c) => c[1]),
    ['HEAD:index.html', ':index.html', ':tests/.gitignore']);
  assert.deepEqual(Object.keys(input.dataJs), [...DATA_JS_INTERVALS]);
  assert.equal(input.dataJs.baseHead, PATCH3);

  // 정상: final 0, 기본 0
  assert.deepEqual(scopeOf({}, {}, { final: true }), []);
  assert.deepEqual(scopeOf(), []);
  // 기본(non-final): featured 0줄도 통과
  const none = { baseHead: '', baseIndex: '', indexWorktree: '', baseWorktree: '' };
  assert.deepEqual(scopeOf({ dataJs: none }), []);

  // checkDataJsDiff 단위
  assert.deepEqual(checkDataJsDiff(PATCH3, { requireExactly3: true }), []);
  assert.deepEqual(checkDataJsDiff(PATCH3), []);
  assert.deepEqual(checkDataJsDiff(''), []);
  assert.deepEqual(checkDataJsDiff(dataPatch(['featured: true,'])), []);
  assert.deepEqual(checkDataJsDiff(dataPatch(["    title: 'x',"])), ['added-non-featured:1']);
  assert.deepEqual(checkDataJsDiff(dataPatch([FEATURED, "    title: 'x',", FEATURED])),
    ['added-non-featured:1']);
  assert.deepEqual(checkDataJsDiff(dataPatch([FEATURED, FEATURED, FEATURED], ["    title: 'y',"])),
    ['deleted:1']);
  assert.deepEqual(checkDataJsDiff(dataPatch([FEATURED, FEATURED, FEATURED, FEATURED])), ['featured-count:4']);
  assert.deepEqual(checkDataJsDiff(dataPatch([FEATURED, FEATURED]), { requireExactly3: true }),
    ['featured-count:2']);
  assert.deepEqual(checkDataJsDiff('', { requireExactly3: true }), ['featured-count:0']);
  assert.deepEqual(checkDataJsDiff(dataPatch(['    featured: false,'])), ['added-non-featured:1']);
  // name-only 출력(이름만)은 patch가 아니다 → 3줄 미달
  assert.deepEqual(checkDataJsDiff(`${DATA_JS}\n`, { requireExactly3: true }), ['featured-count:0']);
  assert.deepEqual(scopeOf({ dataJs: { ...none, baseHead: `${DATA_JS}\n`, baseIndex: `${DATA_JS}\n`, baseWorktree: `${DATA_JS}\n` } },
    {}, { final: true }), [
    'data-js:baseHead:featured-count:0',
    'data-js:baseIndex:featured-count:0',
    'data-js:baseWorktree:featured-count:0',
  ]);

  // `+    title: 'x',` 위반(worktree)
  const titleX = dataPatch([FEATURED, FEATURED, FEATURED, "    title: 'x',"]);
  assert.deepEqual(scopeOf({ dataJs: { ...none, indexWorktree: dataPatch(["    title: 'x',"]), baseWorktree: dataPatch(["    title: 'x',"]) } }), [
    'data-js:indexWorktree:added-non-featured:1',
    'data-js:baseWorktree:added-non-featured:1',
  ]);
  assert.deepEqual(checkDataJsDiff(titleX, { requireExactly3: true }), ['added-non-featured:1']);

  // data.js 위반: 삭제, featured 외, 4줄
  const del = dataPatch([], ["    title: 'y',"]);
  assert.deepEqual(scopeOf({ dataJs: { ...none, baseHead: del } }), ['data-js:baseHead:deleted:1']);
  const four = dataPatch([FEATURED, FEATURED, FEATURED, FEATURED]);
  assert.deepEqual(scopeOf({ dataJs: { ...none, baseIndex: four } }), ['data-js:baseIndex:featured-count:4']);
  // stage 후 원복: BASE→index 위반, index→worktree는 되돌림(삭제), BASE→worktree 0
  assert.deepEqual(scopeOf({ dataJs: { ...none, baseIndex: dataPatch(["    title: 'x',"]), indexWorktree: dataPatch([], ["    title: 'x',"]) } }), [
    'data-js:baseIndex:added-non-featured:1',
    'data-js:indexWorktree:deleted:1',
  ]);

  // final 위반
  assert.deepEqual(scopeOf({ dataJs: { baseHead: '', baseIndex: PATCH3, indexWorktree: '', baseWorktree: PATCH3 } },
    {}, { final: true }), ['data-js:baseHead:featured-count:0']);
  assert.deepEqual(scopeOf({ dataJs: { baseHead: PATCH3, baseIndex: dataPatch([FEATURED, FEATURED]), indexWorktree: dataPatch([FEATURED]), baseWorktree: PATCH3 } },
    {}, { final: true }), ['data-js:baseIndex:featured-count:2']);
  assert.deepEqual(scopeOf({ dataJs: { baseHead: PATCH3, baseIndex: PATCH3, indexWorktree: dataPatch(['    blurb: 1,']), baseWorktree: dataPatch([FEATURED, FEATURED, FEATURED, '    blurb: 1,']) } },
    {}, { final: true }), [
    'data-js:indexWorktree:added-non-featured:1',
    'data-js:baseWorktree:added-non-featured:1',
  ]);
  // 같은 입력이 non-final이면 0줄·2줄은 통과
  assert.deepEqual(scopeOf({ dataJs: { baseHead: '', baseIndex: dataPatch([FEATURED, FEATURED]), indexWorktree: dataPatch([FEATURED]), baseWorktree: PATCH3 } }), []);

  // Space Grotesk 제거 stage 후 원복 → index 위반, worktree 통과
  assert.deepEqual(scopeOf({ show: { 'HEAD:index.html': GOOD_HTML, ':index.html': NO_SG_HTML, ':tests/.gitignore': GOOD_GITIGNORE } }),
    ['space-grotesk-missing:index']);
  assert.deepEqual(scopeOf({ show: { 'HEAD:index.html': NO_SG_HTML, ':index.html': GOOD_HTML, ':tests/.gitignore': GOOD_GITIGNORE } }),
    ['space-grotesk-missing:head']);
  assert.deepEqual(scopeOf({}, { 'index.html': NO_SG_HTML }), ['space-grotesk-missing:worktree']);
  assert.deepEqual(checkSpaceGrotesk(GOOD_HTML), true);
  assert.deepEqual(checkSpaceGrotesk('Space Grotesk'), false);

  // gitignore
  assert.equal(checkGitignore(GOOD_GITIGNORE), true);
  assert.equal(checkGitignore(GITIGNORE_LINES.join('\n')), true, '끝 개행 없음 통과');
  const bad = {
    added: `${GOOD_GITIGNORE}extra/\n`,
    duplicate: `${GOOD_GITIGNORE}node_modules/\n`,
    blank: `${GITIGNORE_LINES.slice(0, 3).join('\n')}\n\n${GITIGNORE_LINES.slice(3).join('\n')}\n`,
    trailingBlank: `${GOOD_GITIGNORE}\n`,
    order: `${[...GITIGNORE_LINES].reverse().join('\n')}\n`,
    comment: `# runtime\n${GOOD_GITIGNORE}`,
    crlf: `${GITIGNORE_LINES.join('\r\n')}\r\n`,
    missing: `${GITIGNORE_LINES.slice(0, 6).join('\n')}\n`,
  };
  for (const [name, text] of Object.entries(bad)) {
    assert.equal(checkGitignore(text), false, name);
    assert.deepEqual(scopeOf({}, { 'tests/.gitignore': text }), ['gitignore:worktree'], name);
  }
  assert.equal(checkGitignore(null), false);
  // index만 위반
  assert.deepEqual(scopeOf({ show: { 'HEAD:index.html': GOOD_HTML, ':index.html': GOOD_HTML, ':tests/.gitignore': bad.added } }),
    ['gitignore:index']);
  // worktree 파일 없음
  assert.deepEqual(scopeOf({}, { 'tests/.gitignore': null }), ['gitignore:worktree']);

  // evaluateScope = 경로 + 내용
  assert.deepEqual(scopeOf({ names: { committed: [], staged: [], worktree: ['README.md'] } }, { 'tests/.gitignore': bad.crlf }),
    ['outside-scope:worktree:README.md', 'gitignore:worktree']);

  // CLI
  const okGit = fakeContentGit();
  assert.deepEqual(main([], { git: okGit, fs: fakeFs(), root: '/fake-root' }), { code: 0, stdout: 'verify-scope: OK' });
  assert.deepEqual(main(['--final'], { git: okGit, fs: fakeFs(), root: '/fake-root' }),
    { code: 0, stdout: 'verify-scope: OK (final)' });
  const r = main(['--final'], { git: fakeContentGit({ dataJs: none }), fs: fakeFs(), root: '/fake-root' });
  assert.equal(r.code, 1);
  assert.match(r.stderr, /^verify-scope: data-js:baseHead:featured-count:0$/m);
  assert.equal(main(['--bogus']).code, 2);
}

export function main(argv, { git = runGit, fs = nodeFs, root = REPO_ROOT } = {}) {
  if (argv.length === 1 && argv[0] === '--self-test') {
    return { code: 0, stdout: selfTest() };
  }
  const final = argv.length === 1 && argv[0] === '--final';
  if (argv.length !== 0 && !final) return { code: 2, stderr: 'usage: verify-scope.mjs [--final | --self-test]' };
  const violations = evaluateScope(collectScopeInput({ git, fs, root }), { final });
  if (violations.length) return { code: 1, stderr: violations.map((v) => `verify-scope: ${v}`).join('\n') };
  return { code: 0, stdout: final ? 'verify-scope: OK (final)' : 'verify-scope: OK' };
}

function isMain() {
  if (!process.argv[1]) return false;
  try {
    return nodeFs.realpathSync(process.argv[1]) === nodeFs.realpathSync(new URL(import.meta.url));
  } catch {
    return false;
  }
}

if (isMain()) {
  let r;
  try {
    r = main(process.argv.slice(2));
  } catch (e) {
    r = { code: 1, stderr: `verify-scope: ${e && e.stack ? e.stack : e}` };
  }
  if (r.stdout) process.stdout.write(`${r.stdout}\n`);
  if (r.stderr) process.stderr.write(`${r.stderr}\n`);
  process.exitCode = r.code;
}
