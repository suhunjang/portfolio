// step 8 — writeAfterZ(after.z 안전 쓰기), runCheck 실행 순서, CLI --check (node 전용, desktop-dark에서만 실행)
import { test, expect } from '@playwright/test';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import {
  UnsafePathError, STATUS_ARGS, writeAfterZ, runCheck,
} from '../scripts/scope-snapshot.mjs';
import { REPO_ROOT, runPython, runNode } from '../helpers/synthetic-repo.js';

const { O_WRONLY, O_CREAT, O_TRUNC, O_NOFOLLOW, O_NONBLOCK } = fs.constants;
const sha256 = (buf) => createHash('sha256').update(buf).digest('hex');
const h0 = '0'.repeat(64);
const h1 = '1'.repeat(64);
const SNAP = 'tests/.tmp/start-snapshot-parity-1.json';
const AFTER = 'tests/.tmp/start-snapshot-parity-1-after.z';

function errorOf(fn) {
  try { fn(); } catch (e) { return e; }
  return null;
}

// ---- 가짜 fs: 모든 호출 기록, open하면 없던 경로는 regular file로 생긴다 ------------------------
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
const WRITE_CALLS = ['openSync', 'writeSync', 'writeFileSync', 'mkdirSync', 'renameSync', 'unlinkSync', 'rmSync', 'symlinkSync'];
function makeFakeFs(entries, { fstatKind } = {}) {
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
    openSync(p, flags, mode) {
      calls.push(['openSync', p, flags, mode]);
      if (!(p in entries)) entries[p] = { kind: 'file' };
      const fd = next++;
      fds.set(fd, p);
      return fd;
    },
    fstatSync(fd) {
      calls.push(['fstatSync', fd]);
      return fakeStats(fstatKind ?? entries[fds.get(fd)].kind);
    },
    writeFileSync(x, data) {
      calls.push(['writeFileSync', x, Buffer.from(data).toString('hex')]);
      if (typeof x !== 'number') throw new Error('writeFileSync by path not allowed');
    },
    closeSync(fd) { calls.push(['closeSync', fd]); fds.delete(fd); },
    readFileSync: deny('readFileSync'),
    statSync: deny('statSync'),
    realpathSync: deny('realpathSync'),
    readlinkSync: deny('readlinkSync'),
    readdirSync: deny('readdirSync'),
    writeSync: deny('writeSync'),
    mkdirSync: deny('mkdirSync'),
    renameSync: deny('renameSync'),
    unlinkSync: deny('unlinkSync'),
    rmSync: deny('rmSync'),
    symlinkSync: deny('symlinkSync'),
  };
  return { fake, calls };
}
const names = (calls) => calls.map((c) => c[0]);
const writes = (calls) => calls.filter((c) => WRITE_CALLS.includes(c[0]));

const dirs = (over = {}) => ({
  '/r': { kind: 'dir' },
  '/r/tests': { kind: 'dir' },
  '/r/tests/.tmp': { kind: 'dir' },
  ...over,
});

// ---- runCheck용 가짜 deps (각 단계 호출을 spy로 기록) ----------------------------------------
const IDENT = Object.freeze({
  schemaVersion: 1, projectRoot: '/r', head: 'a'.repeat(40), base: 'b'.repeat(40),
  harness: { sourceCommit: 's', manifestHash: 'm', distributionVersion: '2.0.0', lockSha256: h0 },
});
const START = Object.freeze({
  stepId: 'parity-1',
  identity: IDENT,
  entries: [],
  xy: {},
  files: { 'README.md': h0, 'tests/specs/x.spec.js': h0 },
});
const STATUS_BYTES = Buffer.from(' M README.md\0', 'utf8');

function makeDeps(over = {}) {
  const order = [];
  const args = {};
  const spy = (name, impl) => (...a) => {
    order.push(name);
    (args[name] ??= []).push(a);
    return impl(...a);
  };
  const base = {
    checkRoot: () => {},
    loadStartSnapshot: () => START,
    computeIdentity: () => IDENT,
    checkIdentity: (a, b) => (a === b || JSON.stringify(a) === JSON.stringify(b) ? [] : ['identity-mismatch:head']),
    takeCurrent: (start, { git }) => {
      git([...STATUS_ARGS]);
      return { entries: [], xy: {}, files: { ...start.files }, unsafe: [] };
    },
    writeAfterZ: () => {},
    evaluateGate: () => [],
    ...over,
  };
  const deps = Object.fromEntries(Object.entries(base).map(([k, f]) => [k, spy(k, f)]));
  const gitCalls = [];
  const git = (a) => {
    gitCalls.push([...a]);
    if (a.join(' ') === STATUS_ARGS.join(' ')) return STATUS_BYTES;
    throw new Error(`git not allowed: ${a.join(' ')}`);
  };
  return { deps, order, args, git, gitCalls };
}
const opts = (over = {}) => ({ startFile: SNAP, allow: [], requireAbsent: [], ...over });

test.describe('step 8 scope-snapshot CLI', () => {
  test.beforeEach(({}, testInfo) => {
    test.skip(testInfo.project.name !== 'desktop-dark', 'node 전용 검사는 desktop-dark에서만 실행');
  });

  test('writeAfterZ 정상: O_NOFOLLOW·O_NONBLOCK·O_TRUNC로 열고 fstat 확인 뒤 쓴다', () => {
    for (const leaf of [{}, { [`/r/${AFTER}`]: { kind: 'file' } }]) {
      const { fake, calls } = makeFakeFs(dirs(leaf));
      writeAfterZ(SNAP, STATUS_BYTES, { fs: fake, root: '/r' });
      const open = calls.find((c) => c[0] === 'openSync');
      expect(open[1]).toBe(`/r/${AFTER}`);
      const flags = open[2];
      for (const f of [O_WRONLY, O_CREAT, O_TRUNC, O_NOFOLLOW, O_NONBLOCK]) expect(flags & f).toBe(f);
      expect(open[3]).toBe(0o644);
      const n = names(calls);
      const iOpen = n.indexOf('openSync');
      expect(n.slice(iOpen)).toEqual(['openSync', 'fstatSync', 'writeFileSync', 'closeSync']);
      expect(calls.find((c) => c[0] === 'writeFileSync')[2]).toBe(STATUS_BYTES.toString('hex'));
      // open 전에는 lstat만
      expect(n.slice(0, iOpen).every((x) => x === 'lstatSync')).toBe(true);
    }
  });

  test('writeAfterZ 거부: leaf symlink·FIFO·디렉터리, 조상 tests/.tmp symlink → UnsafePathError, open 없음', () => {
    const cases = [
      [dirs({ [`/r/${AFTER}`]: { kind: 'symlink' } }), `symlink:${AFTER}`],
      [dirs({ [`/r/${AFTER}`]: { kind: 'fifo' } }), `non-regular:${AFTER}`],
      [dirs({ [`/r/${AFTER}`]: { kind: 'dir' } }), `non-regular:${AFTER}`],
      [dirs({ '/r/tests/.tmp': { kind: 'symlink' } }), 'symlink:tests/.tmp'],
      [{ '/r': { kind: 'symlink' } }, 'symlink:/r'],
    ];
    for (const [entries, item] of cases) {
      const { fake, calls } = makeFakeFs(entries);
      const e = errorOf(() => writeAfterZ(SNAP, STATUS_BYTES, { fs: fake, root: '/r' }));
      expect(e).toBeInstanceOf(UnsafePathError);
      expect(e.item).toBe(item);
      expect(e.message).toBe(`unsafe path: ${item}`);
      expect(writes(calls)).toEqual([]);
    }
    // 검사 뒤 경쟁 교체: 연 fd가 regular가 아니면 쓰지 않는다
    const race = makeFakeFs(dirs(), { fstatKind: 'fifo' });
    const e = errorOf(() => writeAfterZ(SNAP, STATUS_BYTES, { fs: race.fake, root: '/r' }));
    expect(e).toBeInstanceOf(UnsafePathError);
    expect(e.item).toBe(`non-regular:${AFTER}`);
    expect(names(race.calls)).not.toContain('writeFileSync');
    expect(names(race.calls)).toContain('closeSync');
  });

  test('runCheck (0) root symlink → code 1, unsafe path, 이후 단계·쓰기 없음', async () => {
    const { fake, calls } = makeFakeFs({ '/r': { kind: 'symlink' } });
    const { checkRoot } = await import('../scripts/scope-snapshot.mjs');
    const d = makeDeps({ checkRoot });
    const r = runCheck(opts(), { git: d.git, fs: fake, root: '/r', deps: d.deps });
    expect(r).toEqual({ code: 1, stdout: '', stderr: 'unsafe path: symlink:/r' });
    expect(d.order).toEqual(['checkRoot']);
    expect(d.args.checkRoot[0][0]).toMatchObject({ fs: fake, root: '/r' });
    expect(writes(calls)).toEqual([]);
    expect(d.gitCalls).toEqual([]);
  });

  test('runCheck (1) loader 오류(paths 포함) → code 1, 해당 stderr, 쓰기 없음', async () => {
    const { loadStartSnapshot } = await import('../scripts/scope-snapshot.mjs');
    const text = `${JSON.stringify({
      base: 'b', files: { '../outside.txt': null }, harness: {}, head: 'h', projectRoot: '/r',
      schemaVersion: 1, statusZHex: '', stepId: 'parity-1', xy: {},
    }, null, 1)}`;
    const entries = dirs({ [`/r/${SNAP}`]: { kind: 'file', data: text } });
    const { fake, calls } = makeFakeFs(entries);
    fake.readFileSync = (fd) => { calls.push(['readFileSync', fd]); return Buffer.from(text); };
    const d = makeDeps({ loadStartSnapshot });
    const r = runCheck(opts(), { git: d.git, fs: fake, root: '/r', deps: d.deps });
    expect(r).toEqual({ code: 1, stdout: '', stderr: `bad start snapshot: paths: ${SNAP}` });
    expect(d.order).toEqual(['checkRoot', 'loadStartSnapshot']);
    expect(writes(calls).filter((c) => c[0] !== 'openSync')).toEqual([]);
    expect(calls.filter((c) => c[0] === 'openSync').every((c) => c[1] === `/r/${SNAP}`)).toBe(true);

    // 다른 loader 오류도 메시지 그대로
    const d2 = makeDeps({ loadStartSnapshot: () => { throw new UnsafePathError(`missing:${SNAP}`); } });
    const r2 = runCheck(opts(), { git: d2.git, fs: makeFakeFs(dirs()).fake, root: '/r', deps: d2.deps });
    expect(r2).toEqual({ code: 1, stdout: '', stderr: `unsafe path: missing:${SNAP}` });
    expect(d2.order).toEqual(['checkRoot', 'loadStartSnapshot']);
  });

  test('runCheck (2) identity 불일치·identity 계산 실패 → code 1, 쓰기 없음', () => {
    const { fake, calls } = makeFakeFs(dirs());
    const other = { ...IDENT, head: 'c'.repeat(40) };
    const d = makeDeps({ computeIdentity: () => other });
    const r = runCheck(opts(), { git: d.git, fs: fake, root: '/r', deps: d.deps });
    expect(r).toEqual({ code: 1, stdout: '', stderr: 'start snapshot identity mismatch: head' });
    expect(d.order).toEqual(['checkRoot', 'loadStartSnapshot', 'computeIdentity', 'checkIdentity']);
    expect(d.args.checkIdentity[0]).toEqual([IDENT, other]);
    expect(writes(calls)).toEqual([]);

    const d2 = makeDeps({ computeIdentity: () => { throw new UnsafePathError('symlink:.harness'); } });
    const r2 = runCheck(opts(), { git: d2.git, fs: fake, root: '/r', deps: d2.deps });
    expect(r2).toEqual({ code: 1, stdout: '', stderr: 'unsafe path: symlink:.harness' });
    expect(d2.order).toEqual(['checkRoot', 'loadStartSnapshot', 'computeIdentity']);
    expect(writes(calls)).toEqual([]);
  });

  test('runCheck (3) takeCurrent unsafe → code 1, snapshot-not-first·unsafe만, writeAfterZ 없음', () => {
    const unsafeCur = (start, { git }) => {
      git([...STATUS_ARGS]);
      return { entries: [], xy: {}, files: {}, unsafe: ['non-regular:tests/specs/p.fifo'] };
    };
    const { fake, calls } = makeFakeFs(dirs());
    const d = makeDeps({ takeCurrent: unsafeCur });
    const r = runCheck(opts({ allow: ['tests/specs/p.fifo'] }), { git: d.git, fs: fake, root: '/r', deps: d.deps });
    expect(r).toEqual({ code: 1, stdout: '', stderr: 'non-regular:tests/specs/p.fifo' });
    expect(d.order).toEqual(['checkRoot', 'loadStartSnapshot', 'computeIdentity', 'checkIdentity', 'takeCurrent']);
    expect(d.args.takeCurrent[0][0]).toBe(START);
    expect(d.args.takeCurrent[0][1]).toMatchObject({ fs: fake, root: '/r' });
    expect(writes(calls)).toEqual([]);

    const d2 = makeDeps({ takeCurrent: unsafeCur });
    const r2 = runCheck(opts({ requireAbsent: ['tests/specs/x.spec.js', 'tests/specs/new.spec.js'] }),
      { git: d2.git, fs: fake, root: '/r', deps: d2.deps });
    expect(r2).toEqual({
      code: 1, stdout: '', stderr: 'snapshot-not-first:tests/specs/x.spec.js\nnon-regular:tests/specs/p.fifo',
    });
    expect(d2.order).not.toContain('writeAfterZ');
    expect(d2.order).not.toContain('evaluateGate');

    // takeCurrent 자체 오류(bad start snapshot: paths)도 code 1, 쓰기 없음
    const d3 = makeDeps({ takeCurrent: () => { throw new Error('bad start snapshot: paths'); } });
    const r3 = runCheck(opts(), { git: d3.git, fs: fake, root: '/r', deps: d3.deps });
    expect(r3).toEqual({ code: 1, stdout: '', stderr: 'bad start snapshot: paths' });
    expect(d3.order).not.toContain('writeAfterZ');
    expect(writes(calls)).toEqual([]);
  });

  test('runCheck (4) writeAfterZ 실패 → code 1, evaluateGate 호출 없음', () => {
    const d = makeDeps({ writeAfterZ: () => { throw new UnsafePathError('symlink:tests/.tmp'); } });
    const r = runCheck(opts(), { git: d.git, fs: makeFakeFs(dirs()).fake, root: '/r', deps: d.deps });
    expect(r).toEqual({ code: 1, stdout: '', stderr: 'unsafe path: symlink:tests/.tmp' });
    expect(d.order).toEqual([
      'checkRoot', 'loadStartSnapshot', 'computeIdentity', 'checkIdentity', 'takeCurrent', 'writeAfterZ',
    ]);
    expect(d.order).not.toContain('evaluateGate');
  });

  test('runCheck (5) after.z 쓴 뒤 판정: 위반 → code 1, 없음 → code 0·scope-snapshot: OK', async () => {
    const { evaluateGate } = await import('../scripts/scope-snapshot.mjs');
    const changed = (start, { git }) => {
      git([...STATUS_ARGS]);
      return { entries: [], xy: {}, files: { ...start.files, 'tests/specs/x.spec.js': h1 }, unsafe: [] };
    };
    const full = ['checkRoot', 'loadStartSnapshot', 'computeIdentity', 'checkIdentity', 'takeCurrent', 'writeAfterZ', 'evaluateGate'];

    const d = makeDeps({ takeCurrent: changed, evaluateGate });
    const r = runCheck(opts(), { git: d.git, fs: makeFakeFs(dirs()).fake, root: '/r', deps: d.deps });
    expect(r).toEqual({ code: 1, stdout: '', stderr: 'tests-changed:tests/specs/x.spec.js' });
    expect(d.order).toEqual(full);
    expect(d.args.writeAfterZ[0][0]).toBe(SNAP);
    expect(Buffer.from(d.args.writeAfterZ[0][1]).equals(STATUS_BYTES)).toBe(true);
    expect(d.args.evaluateGate[0][2]).toEqual({ allow: [], requireAbsent: [] });

    const d2 = makeDeps({ takeCurrent: changed, evaluateGate });
    const r2 = runCheck(opts({ allow: ['tests/specs/x.spec.js'] }),
      { git: d2.git, fs: makeFakeFs(dirs()).fake, root: '/r', deps: d2.deps });
    expect(r2).toEqual({ code: 0, stdout: 'scope-snapshot: OK', stderr: '' });
    expect(d2.order).toEqual(full);
  });

  test('CLI subprocess(실제 저장소): 정상·없는 snapshot·schemaVersion 1.0·인자 누락', () => {
    const pid = String(process.pid);
    const rel = (id) => `tests/.tmp/start-snapshot-${id}.json`;
    const abs = (p) => path.join(REPO_ROOT, p);
    const afterOf = (p) => p.replace(/\.json$/, '-after.z');
    const id = `parity-${pid}`;
    const missingId = `parity-${pid}0`;
    const v10Id = `parity-${pid}1`;
    const all = [rel(id), rel(missingId), rel(v10Id)].flatMap((p) => [p, afterOf(p)]);
    const cleanup = () => { for (const p of all) fs.rmSync(abs(p), { force: true }); };
    const cli = (args) => runNode(['tests/scripts/scope-snapshot.mjs', ...args], { cwd: REPO_ROOT });
    cleanup();
    try {
      const s = runPython(['-I', 'tests/scripts/start-snapshot.py', id], { cwd: REPO_ROOT });
      expect(s.code, s.stderr).toBe(0);
      expect(s.stdout.trim()).toBe(`start-snapshot: created ${rel(id)}`);
      const raw = fs.readFileSync(abs(rel(id)));
      const text = raw.toString('utf8');
      expect(text).toContain('"schemaVersion": 1,');
      fs.writeFileSync(abs(rel(v10Id)), text.replace('"schemaVersion": 1,', '"schemaVersion": 1.0,'));
      const shaOk = sha256(raw);
      const shaV10 = sha256(fs.readFileSync(abs(rel(v10Id))));
      const unchanged = () => {
        expect(sha256(fs.readFileSync(abs(rel(id))))).toBe(shaOk);
        expect(sha256(fs.readFileSync(abs(rel(v10Id))))).toBe(shaV10);
        expect(fs.existsSync(abs(rel(missingId)))).toBe(false);
      };

      const ok = cli(['--check', rel(id), '--allow', '']);
      expect(ok.code, ok.stderr).toBe(0);
      expect(ok.stdout).toBe('scope-snapshot: OK\n');
      expect(ok.stderr).toBe('');
      expect(fs.lstatSync(abs(afterOf(rel(id)))).isFile()).toBe(true);
      unchanged();

      const miss = cli(['--check', rel(missingId), '--allow', '']);
      expect(miss.code).toBe(1);
      expect(miss.stderr).toBe(`unsafe path: missing:${rel(missingId)}\n`);
      expect(fs.existsSync(abs(afterOf(rel(missingId))))).toBe(false);
      unchanged();

      const v10 = cli(['--check', rel(v10Id), '--allow', '']);
      expect(v10.code).toBe(1);
      expect(v10.stderr).toBe(`bad start snapshot: schemaVersion: ${rel(v10Id)}\n`);
      expect(fs.existsSync(abs(afterOf(rel(v10Id))))).toBe(false);
      unchanged();

      for (const args of [[], ['--check', rel(id)], ['--allow', ''], ['--check', rel(id), '--allow', '', '--bogus', 'x'],
        ['--check', rel(id), '--allow', '', '--require-absent']]) {
        const u = cli(args);
        expect(u.code, JSON.stringify(args)).toBe(2);
        expect(u.stderr).toMatch(/^usage: /);
        expect(u.stdout).toBe('');
        unchanged();
      }
    } finally {
      cleanup();
    }
    for (const p of all) expect(fs.existsSync(abs(p))).toBe(false);
  });
});
