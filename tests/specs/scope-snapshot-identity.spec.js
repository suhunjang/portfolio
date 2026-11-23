// step 7 — computeIdentity·checkIdentity, 순수 변경·정책 판정(diffAgainstStart·classifyChanges·
// checkRuntimeVisible·checkSnapshotFirst·evaluateGate, unsafe 우선) (node 전용, desktop-dark에서만 실행)
import { test, expect } from '@playwright/test';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import {
  UnsafePathError, BASE, HARNESS_IDENTITY, LOCK_PATH, loadStartSnapshot,
  computeIdentity, checkIdentity, diffAgainstStart, classifyChanges,
  checkRuntimeVisible, checkSnapshotFirst, evaluateGate,
} from '../scripts/scope-snapshot.mjs';
import { REPO_ROOT, runPython } from '../helpers/synthetic-repo.js';

const sha256 = (buf) => createHash('sha256').update(buf).digest('hex');
const h0 = '0'.repeat(64);
const h1 = '1'.repeat(64);
const h2 = '2'.repeat(64);

function errorOf(fn) {
  try { fn(); } catch (e) { return e; }
  return null;
}

function deepFreeze(o) {
  if (o && typeof o === 'object' && !Object.isFrozen(o)) {
    Object.freeze(o);
    for (const v of Object.values(o)) deepFreeze(v);
  }
  return o;
}
const clone = (o) => JSON.parse(JSON.stringify(o));

// ---- 가짜 fs·git (computeIdentity) ---------------------------------------------------------
function fakeStats(kind) {
  return {
    isFile: () => kind === 'file',
    isDirectory: () => kind === 'dir',
    isSymbolicLink: () => kind === 'symlink',
    isFIFO: () => kind === 'fifo',
    isSocket: () => false,
    isBlockDevice: () => false,
    isCharacterDevice: () => false,
  };
}
function makeFakeFs(entries) {
  const calls = [];
  const fds = new Map();
  let next = 10;
  const enoent = (p) => Object.assign(new Error(`ENOENT: ${p}`), { code: 'ENOENT' });
  const deny = (name) => (...args) => {
    calls.push([name, ...args.map(String)]);
    throw new Error(`${name} not allowed`);
  };
  const fake = {
    constants: fs.constants,
    lstatSync(p) {
      calls.push(['lstatSync', p]);
      if (!(p in entries)) throw enoent(p);
      return fakeStats(entries[p].kind);
    },
    realpathSync(p) {
      calls.push(['realpathSync', p]);
      return p;
    },
    openSync(p, flags) {
      calls.push(['openSync', p, flags]);
      if (!(p in entries)) throw enoent(p);
      const fd = next++;
      fds.set(fd, p);
      return fd;
    },
    fstatSync(fd) {
      calls.push(['fstatSync', fd]);
      return fakeStats(entries[fds.get(fd)].kind);
    },
    readFileSync(x) {
      calls.push(['readFileSync', x]);
      if (typeof x !== 'number') throw new Error('readFileSync by path not allowed');
      return Buffer.from(entries[fds.get(x)].data ?? '');
    },
    closeSync(fd) { calls.push(['closeSync', fd]); fds.delete(fd); },
    statSync: deny('statSync'),
    readlinkSync: deny('readlinkSync'),
    readdirSync: deny('readdirSync'),
    existsSync: deny('existsSync'),
    writeFileSync: deny('writeFileSync'),
    mkdirSync: deny('mkdirSync'),
  };
  return { fake, calls };
}
const HEAD = 'a'.repeat(40);
function makeFakeGit({ toplevel = '/r', baseOk = true } = {}) {
  const calls = [];
  const git = (args) => {
    const a = [...args];
    calls.push(a);
    const k = a.join(' ');
    if (k === 'rev-parse --show-toplevel') return Buffer.from(`${toplevel}\n`);
    if (k === 'rev-parse HEAD') return Buffer.from(`${HEAD}\n`);
    if (k === `rev-parse --verify ${BASE}^{commit}`) {
      if (!baseOk) throw new Error('fatal: Needed a single revision');
      return Buffer.from(`${BASE}\n`);
    }
    throw new Error(`git not allowed: ${k}`);
  };
  return { git, calls };
}
const LOCK_TEXT = `${JSON.stringify({ ...HARNESS_IDENTITY, schemaVersion: 1 }, null, 2)}\n`;
const okEntries = (over = {}) => deepFreeze({
  '/r': { kind: 'dir' },
  '/r/.harness': { kind: 'dir' },
  '/r/.harness/harness.lock.json': { kind: 'file', data: LOCK_TEXT },
  ...over,
});
const verifyCalled = (calls) => calls.some((a) => a[0] === 'rev-parse' && a[1] === '--verify');
const opened = (calls) => calls.some((c) => c[0] === 'openSync');

// ---- 변경 판정 기준 상태 ----------------------------------------------------------------------
const START = deepFreeze({
  files: {
    '.harness/harness.lock.json': h0,
    '.harness/policy.json': h0,
    'CLAUDE.md': h1,
    'README.md': h0,
    'phases/HOO-81-portfolio-redesign/step10.md': h0,
    'tests/fixtures/local.json': h1,
    'tests/helpers/theme.js': h0,
    'tests/playwright.config.js': h1,
    'tests/specs/wip.spec.js': h0,
  },
  xy: {
    'CLAUDE.md': ' M',
    'tests/playwright.config.js': ' M',
    'tests/specs/wip.spec.js': '??',
  },
});
function current(mut) {
  const cur = { ...clone(START), unsafe: [] };
  if (mut) mut(cur);
  return deepFreeze(cur);
}
const gate = (mut, { allow = [], requireAbsent = [] } = {}) => {
  const cur = current(mut);
  const before = JSON.stringify([START, cur, allow, requireAbsent]);
  const out = evaluateGate(START, cur, { allow, requireAbsent });
  expect(JSON.stringify([START, cur, allow, requireAbsent])).toBe(before);
  return out;
};

test.describe('step 7 scope-snapshot identity·gate', () => {
  test.beforeEach(({}, testInfo) => {
    test.skip(testInfo.project.name !== 'desktop-dark', 'node 전용 검사는 desktop-dark에서만 실행');
  });

  test('checkIdentity(순수): 같음 [], 필드별 identity-mismatch, 여러 필드는 지정 순서', () => {
    const base = deepFreeze({
      schemaVersion: 1,
      projectRoot: '/r',
      head: HEAD,
      base: BASE,
      harness: { ...HARNESS_IDENTITY, lockSha256: h1 },
    });
    expect(checkIdentity(base, clone(base))).toEqual([]);
    const cases = [
      ['schemaVersion', (o) => { o.schemaVersion = 2; }],
      ['projectRoot', (o) => { o.projectRoot = '/other'; }],
      ['head', (o) => { o.head = 'b'.repeat(40); }],
      ['base', (o) => { o.base = 'c'.repeat(40); }],
      ['harness.sourceCommit', (o) => { o.harness.sourceCommit = 'd'.repeat(40); }],
      ['harness.manifestHash', (o) => { o.harness.manifestHash = h2; }],
      ['harness.distributionVersion', (o) => { o.harness.distributionVersion = '9.9.9'; }],
      ['harness.lockSha256', (o) => { o.harness.lockSha256 = h2; }],
    ];
    for (const [field, mut] of cases) {
      const cur = clone(base);
      mut(cur);
      deepFreeze(cur);
      expect(checkIdentity(base, cur), field).toEqual([`identity-mismatch:${field}`]);
    }
    const all = clone(base);
    for (const [, mut] of cases) mut(all);
    deepFreeze(all);
    expect(checkIdentity(base, all)).toEqual(cases.map(([f]) => `identity-mismatch:${f}`));
    const some = clone(base);
    some.harness.lockSha256 = h2;
    some.head = 'e'.repeat(40);
    some.projectRoot = '/x';
    expect(checkIdentity(base, deepFreeze(some))).toEqual([
      'identity-mismatch:projectRoot', 'identity-mismatch:head', 'identity-mismatch:harness.lockSha256',
    ]);
  });

  test('computeIdentity(가짜 fs·git): 정상 값, root·.harness 조상 symlink·lock FIFO는 verify·open 전에 거부', () => {
    const ok = makeFakeFs(okEntries());
    const okGit = makeFakeGit();
    expect(computeIdentity({ git: okGit.git, fs: ok.fake, root: '/r' })).toEqual({
      schemaVersion: 1,
      projectRoot: '/r',
      head: HEAD,
      base: BASE,
      harness: { ...HARNESS_IDENTITY, lockSha256: sha256(LOCK_TEXT) },
    });
    expect(ok.calls.filter((c) => c[0] === 'openSync')).toEqual([
      ['openSync', '/r/.harness/harness.lock.json', (fs.constants.O_RDONLY | fs.constants.O_NOFOLLOW | fs.constants.O_NONBLOCK)],
    ]);
    expect(ok.calls.some((c) => ['writeFileSync', 'mkdirSync', 'readdirSync'].includes(c[0]))).toBe(false);

    const rejects = [
      ['symlink:/r', { '/r': { kind: 'symlink' } }],
      ['symlink:.harness', { '/r/.harness': { kind: 'symlink' } }],
      ['non-regular:.harness/harness.lock.json', { '/r/.harness/harness.lock.json': { kind: 'fifo' } }],
      ['missing:.harness/harness.lock.json', { '/r/.harness/harness.lock.json': undefined }],
    ];
    for (const [item, over] of rejects) {
      const ents = { ...okEntries() };
      for (const [k, v] of Object.entries(over)) {
        if (v === undefined) delete ents[k]; else ents[k] = v;
      }
      const f = makeFakeFs(deepFreeze(ents));
      const g = makeFakeGit();
      const e = errorOf(() => computeIdentity({ git: g.git, fs: f.fake, root: '/r' }));
      expect(e, item).toBeInstanceOf(UnsafePathError);
      expect(e.item).toBe(item);
      expect(e.message).toBe(`unsafe path: ${item}`);
      expect(verifyCalled(g.calls), item).toBe(false);
      expect(opened(f.calls), item).toBe(false);
      if (item === 'symlink:/r') {
        expect(g.calls).toEqual([]);
        expect(f.calls).toEqual([['lstatSync', '/r']]);
      }
    }

    // toplevel이 root와 다르면 lock 접근 전 throw
    const other = makeFakeFs(okEntries());
    const otherGit = makeFakeGit({ toplevel: '/elsewhere' });
    const e1 = errorOf(() => computeIdentity({ git: otherGit.git, fs: other.fake, root: '/r' }));
    expect(e1).toBeInstanceOf(Error);
    expect(e1).not.toBeInstanceOf(UnsafePathError);
    expect(opened(other.calls)).toBe(false);
    expect(verifyCalled(otherGit.calls)).toBe(false);

    // BASE가 없으면 lock open 전 throw
    const nb = makeFakeFs(okEntries());
    const nbGit = makeFakeGit({ baseOk: false });
    expect(errorOf(() => computeIdentity({ git: nbGit.git, fs: nb.fake, root: '/r' }))).toBeInstanceOf(Error);
    expect(opened(nb.calls)).toBe(false);

    // lock에 중앙 identity 값이 없으면 throw
    const bad = makeFakeFs(okEntries({ '/r/.harness/harness.lock.json': { kind: 'file', data: '{}\n' } }));
    const e2 = errorOf(() => computeIdentity({ git: makeFakeGit().git, fs: bad.fake, root: '/r' }));
    expect(e2?.message).toBe(`harness identity mismatch: ${LOCK_PATH}`);
  });

  test('computeIdentity(실제 저장소): parity snapshot identity와 같음, 다른 root(tests/.tmp)는 throw', () => {
    const id = `parity-${process.pid}`;
    const rel = `tests/.tmp/start-snapshot-${id}.json`;
    const abs = path.join(REPO_ROOT, rel);
    fs.rmSync(abs, { force: true });
    try {
      const s = runPython(['-I', 'tests/scripts/start-snapshot.py', id], { cwd: REPO_ROOT });
      expect(s.code, s.stderr).toBe(0);
      expect(s.stdout.trim()).toBe(`start-snapshot: created ${rel}`);
      const snap = loadStartSnapshot(rel, { root: REPO_ROOT });
      const cur = computeIdentity({ root: REPO_ROOT });
      expect(cur).toEqual(snap.identity);
      expect(checkIdentity(snap.identity, cur)).toEqual([]);
      const tmpRoot = path.join(REPO_ROOT, 'tests/.tmp');
      expect(errorOf(() => computeIdentity({ root: tmpRoot }))).toBeInstanceOf(Error);
    } finally {
      fs.rmSync(abs, { force: true });
    }
    expect(fs.existsSync(abs)).toBe(false);
  });

  test('변경 판정: CLAUDE.md 시작 M/h1 — 그대로·원복·삭제·내용만 변경', () => {
    expect(gate()).toEqual([]);
    const revert = current((c) => { delete c.xy['CLAUDE.md']; c.files['CLAUDE.md'] = h0; });
    expect(diffAgainstStart(START, revert)).toEqual([
      { path: 'CLAUDE.md', kind: 'content-changed', xyBefore: ' M', xyAfter: null },
    ]);
    expect(evaluateGate(START, revert, { allow: [], requireAbsent: [] })).toEqual(['outside-tests:CLAUDE.md']);
    const del = current((c) => { c.xy['CLAUDE.md'] = ' D'; c.files['CLAUDE.md'] = null; });
    expect(diffAgainstStart(START, del)).toEqual([
      { path: 'CLAUDE.md', kind: 'deleted', xyBefore: ' M', xyAfter: ' D' },
    ]);
    expect(classifyChanges(diffAgainstStart(START, del), { allow: [] })).toEqual(['outside-tests:CLAUDE.md']);
    expect(gate((c) => { c.files['CLAUDE.md'] = h2; })).toEqual(['outside-tests:CLAUDE.md']);
  });

  test('변경 판정: tests/playwright.config.js 시작 M/h1(allow 밖·안)', () => {
    const P = 'tests/playwright.config.js';
    expect(gate()).toEqual([]);
    expect(gate((c) => { c.files[P] = h2; })).toEqual([`tests-changed:${P}`]);
    expect(gate((c) => { c.files[P] = null; c.xy[P] = ' D'; })).toEqual([`tests-changed:${P}`]);
    expect(gate((c) => { c.files[P] = h0; delete c.xy[P]; })).toEqual([`tests-changed:${P}`]);
    expect(gate((c) => { c.files[P] = h2; }, { allow: [P] })).toEqual([]);
    expect(gate((c) => { c.files[P] = null; c.xy[P] = ' D'; }, { allow: new Set([P]) })).toEqual([]);
  });

  test('변경 판정: tests 수정·사라짐·walk 전용, status만 변경, 새 밖 파일', () => {
    expect(gate((c) => { c.files['tests/helpers/theme.js'] = h2; c.xy['tests/helpers/theme.js'] = ' M'; }))
      .toEqual(['tests-changed:tests/helpers/theme.js']);
    const gone = current((c) => { c.files['tests/specs/wip.spec.js'] = null; delete c.xy['tests/specs/wip.spec.js']; });
    expect(diffAgainstStart(START, gone)).toEqual([
      { path: 'tests/specs/wip.spec.js', kind: 'deleted', xyBefore: '??', xyAfter: null },
    ]);
    expect(evaluateGate(START, gone, { allow: [], requireAbsent: [] })).toEqual(['tests-changed:tests/specs/wip.spec.js']);
    expect(gate((c) => { c.files['tests/fixtures/local.json'] = h2; })).toEqual(['tests-changed:tests/fixtures/local.json']);
    const st = current((c) => { c.xy['README.md'] = 'M '; });
    expect(diffAgainstStart(START, st)).toEqual([
      { path: 'README.md', kind: 'status-changed', xyBefore: null, xyAfter: 'M ' },
    ]);
    expect(evaluateGate(START, st, { allow: [], requireAbsent: [] })).toEqual(['status-changed:README.md']);
    const nw = current((c) => { c.files['docs/x.md'] = h1; c.xy['docs/x.md'] = '??'; });
    expect(diffAgainstStart(START, nw)).toEqual([
      { path: 'docs/x.md', kind: 'new', xyBefore: null, xyAfter: '??' },
    ]);
    expect(evaluateGate(START, nw, { allow: [], requireAbsent: [] })).toEqual(['outside-tests:docs/x.md']);
  });

  test('변경 판정: 하네스 런타임 면제·GUARDED, runtime-visible, 새 tests 파일, rename', () => {
    expect(gate((c) => {
      c.files['.harness/runtime/a.json'] = h1;
      c.xy['.harness/runtime/a.json'] = '??';
      c.files['phases/HOO-81-portfolio-redesign/step10.md'] = h2;
      c.xy['phases/HOO-81-portfolio-redesign/step10.md'] = ' M';
    })).toEqual([]);
    expect(gate((c) => { c.files['.harness/policy.json'] = h2; c.xy['.harness/policy.json'] = ' M'; }))
      .toEqual(['outside-tests:.harness/policy.json']);
    expect(gate((c) => { c.files['.harness/harness.lock.json'] = h2; c.xy['.harness/harness.lock.json'] = ' M'; }))
      .toEqual(['outside-tests:.harness/harness.lock.json']);
    const rv = current((c) => { c.xy['tests/node_modules/x/index.js'] = '??'; });
    expect(checkRuntimeVisible(START, rv)).toEqual(['runtime-visible:tests/node_modules/x/index.js']);
    expect(evaluateGate(START, rv, { allow: [], requireAbsent: [] })).toEqual(['runtime-visible:tests/node_modules/x/index.js']);
    expect(gate((c) => { c.files['tests/specs/other.spec.js'] = h1; c.xy['tests/specs/other.spec.js'] = '??'; }))
      .toEqual(['tests-changed:tests/specs/other.spec.js']);
    expect(gate((c) => {
      c.xy['tests/x.js'] = 'R ';
      c.xy['README.md'] = 'R ';
      c.files['tests/x.js'] = h0;
      c.files['README.md'] = null;
    })).toEqual(['outside-tests:README.md', 'tests-changed:tests/x.js']);
  });

  test('unsafe 우선: snapshot-not-first 다음 정렬 unsafe만, 변경 판정 생략, allow도 면제 안 함', () => {
    const mut = (c) => {
      c.unsafe = ['symlink:b', 'non-regular:a'];
      c.files = {};
      c.xy['README.md'] = 'M ';
      c.xy['tests/node_modules/x/index.js'] = '??';
    };
    const expected = ['snapshot-not-first:CLAUDE.md', 'non-regular:a', 'symlink:b'];
    expect(gate(mut, { requireAbsent: ['CLAUDE.md'] })).toEqual(expected);
    expect(gate(mut, { requireAbsent: ['CLAUDE.md'], allow: ['a', 'b', 'README.md'] })).toEqual(expected);
    expect(gate((c) => { mut(c); c.unsafe = ['symlink:b', 'non-regular:a', 'symlink:b']; }))
      .toEqual(['non-regular:a', 'symlink:b']);
  });

  test('checkSnapshotFirst·evaluateGate 전체 순서, classifyChanges 입력 불변', () => {
    const paths = deepFreeze(['zzz/absent.md', 'tests/specs/wip.spec.js', 'CLAUDE.md', 'CLAUDE.md']);
    expect(checkSnapshotFirst(START, paths)).toEqual([
      'snapshot-not-first:CLAUDE.md', 'snapshot-not-first:tests/specs/wip.spec.js',
    ]);
    expect(checkSnapshotFirst(START, [])).toEqual([]);
    // xy에만 있는 시작 경로도 snapshot-not-first
    const s2 = deepFreeze({ files: {}, xy: { 'tests/.tmp/x.json': '??' } });
    expect(checkSnapshotFirst(s2, ['tests/.tmp/x.json'])).toEqual(['snapshot-not-first:tests/.tmp/x.json']);

    const out = gate((c) => {
      c.xy['tests/node_modules/b.js'] = '??';
      c.xy['tests/.tmp/a.json'] = '??';
      c.files['tests/helpers/theme.js'] = h2;
      c.xy['README.md'] = 'M ';
      c.files['CLAUDE.md'] = h2;
    }, { requireAbsent: ['tests/specs/wip.spec.js', 'CLAUDE.md'] });
    expect(out).toEqual([
      'snapshot-not-first:CLAUDE.md',
      'snapshot-not-first:tests/specs/wip.spec.js',
      'outside-tests:CLAUDE.md',
      'status-changed:README.md',
      'tests-changed:tests/helpers/theme.js',
      'runtime-visible:tests/.tmp/a.json',
      'runtime-visible:tests/node_modules/b.js',
    ]);

    const changes = deepFreeze(diffAgainstStart(START, current((c) => { c.files['CLAUDE.md'] = h2; })));
    const snap = JSON.stringify(changes);
    expect(classifyChanges(changes, { allow: deepFreeze([]) })).toEqual(['outside-tests:CLAUDE.md']);
    expect(classifyChanges(changes, { allow: ['CLAUDE.md'] })).toEqual([]);
    expect(JSON.stringify(changes)).toBe(snap);
  });
});
