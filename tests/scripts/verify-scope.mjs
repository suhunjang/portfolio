// 범위 검사 (설계 §8.4).
// step 22: 경로 정책. diff 인자 상수 분리(경로 = name-only, 내용 = js/data.js patch만), 읽기 전용 수집,
//          순수 판정 evaluatePaths. CLI 인자 없음 → `verify-scope: OK (paths)`, `--self-test`.
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
  return 'verify-scope: self-test OK';
}

export function main(argv, { git = runGit } = {}) {
  if (argv.length === 1 && argv[0] === '--self-test') {
    return { code: 0, stdout: selfTest() };
  }
  if (argv.length !== 0) return { code: 2, stderr: 'usage: verify-scope.mjs [--self-test]' };
  const violations = evaluatePaths(collectInput({ git }));
  if (violations.length) return { code: 1, stderr: violations.map((v) => `verify-scope: ${v}`).join('\n') };
  return { code: 0, stdout: 'verify-scope: OK (paths)' };
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
