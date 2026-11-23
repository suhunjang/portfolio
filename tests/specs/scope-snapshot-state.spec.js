// step 4 — scanProject·hashPath·takeCurrent 상태 수집, 합성 저장소 수집·rename, 실제 저장소 S parity
// (node 전용, desktop-dark에서만 실행)
import { test, expect } from '@playwright/test';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import {
  UnsafePathError, STATUS_ARGS, LS_FILES_ARGS, loadStartSnapshot,
  scanProject, hashPath, takeCurrent,
} from '../scripts/scope-snapshot.mjs';
import {
  REPO_ROOT, makeSyntheticRepo, designBlock, runPython, runNode, runHarness, isolatedGitEnv,
} from '../helpers/synthetic-repo.js';

const sha256 = (buf) => createHash('sha256').update(buf).digest('hex');
const NUL = String.fromCharCode(0);

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

// ---- 가짜 fs: abs 경로 → { kind, data } ---------------------------------------------------
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
    readdirSync(p, opts) {
      calls.push(['readdirSync', p]);
      if (!opts || opts.withFileTypes !== true) throw new Error('withFileTypes required');
      if (!(p in entries)) throw enoent(p);
      if (entries[p].kind !== 'dir') throw new Error(`ENOTDIR: ${p}`);
      return Object.keys(entries)
        .filter((k) => path.dirname(k) === p && k !== p)
        .map((k) => Object.assign(fakeStats(entries[k].kind), { name: path.basename(k) }));
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
    realpathSync: deny('realpathSync'),
    existsSync: deny('existsSync'),
    writeFileSync: deny('writeFileSync'),
    mkdirSync: deny('mkdirSync'),
  };
  return { fake, calls };
}

// 합성 저장소용 Git 읽기 전용 주입 함수 (status·ls-files만)
function gitReader(dir) {
  return (args) => {
    const a = [...args];
    const ok = JSON.stringify(a) === JSON.stringify(STATUS_ARGS) || JSON.stringify(a) === JSON.stringify(LS_FILES_ARGS);
    if (!ok) throw new Error(`git read not allowed: ${a.join(' ')}`);
    const r = spawnSync('git', ['-C', dir, ...a], { env: isolatedGitEnv(), timeout: 10000 });
    if (r.error) throw r.error;
    if (r.status !== 0) throw new Error(`git ${a.join(' ')} failed: ${r.stderr}`);
    return r.stdout;
  };
}

function write(dir, rel, text) {
  fs.mkdirSync(path.dirname(path.join(dir, rel)), { recursive: true });
  fs.writeFileSync(path.join(dir, rel), text);
}

test.describe('step 4 scope-snapshot state', () => {
  test.beforeEach(({}, testInfo) => {
    test.skip(testInfo.project.name !== 'desktop-dark', 'node 전용 검사는 desktop-dark에서만 실행');
  });

  test('hashPath(가짜 fs): file sha256, missing null, dir non-regular, symlink는 따라가지 않고 거부', () => {
    const entries = deepFreeze({
      '/r': { kind: 'dir' },
      '/r/a.txt': { kind: 'file', data: 'hello\n' },
      '/r/d': { kind: 'dir' },
      '/r/ln': { kind: 'symlink' },
      '/r/p': { kind: 'fifo' },
    });
    const opts = (fake) => Object.freeze({ fs: fake, root: '/r' });

    const ok = makeFakeFs(entries);
    expect(hashPath('a.txt', opts(ok.fake))).toBe(sha256('hello\n'));
    expect(ok.calls.map((c) => c[0])).toEqual(['lstatSync', 'openSync', 'fstatSync', 'readFileSync', 'closeSync']);

    const miss = makeFakeFs(entries);
    expect(hashPath('none', opts(miss.fake))).toBeNull();
    expect(miss.calls).toEqual([['lstatSync', '/r/none']]);

    for (const [p, item] of [['d', 'non-regular:d'], ['p', 'non-regular:p'], ['ln', 'symlink:ln']]) {
      const f = makeFakeFs(entries);
      const e = errorOf(() => hashPath(p, opts(f.fake)));
      expect(e, p).toBeInstanceOf(UnsafePathError);
      expect(e.item).toBe(item);
      expect(f.calls, p).toEqual([['lstatSync', `/r/${p}`]]);
      const names = f.calls.map((c) => c[0]);
      for (const n of ['readFileSync', 'statSync', 'readlinkSync', 'realpathSync', 'openSync']) expect(names, `${p} ${n}`).not.toContain(n);
    }
  });

  test('scanProject(가짜 fs): root 검사 먼저, SKIP 미진입, SKIP 엔트리 symlink 보고, 정렬', () => {
    for (const [kind, item] of [['symlink', 'symlink:/r'], ['file', 'non-regular:/r'], [null, 'missing:/r']]) {
      const f = makeFakeFs(kind ? { '/r': { kind }, '/r/tests': { kind: 'dir' } } : {});
      const e = errorOf(() => scanProject(Object.freeze({ fs: f.fake, root: '/r' })));
      expect(e, String(kind)).toBeInstanceOf(UnsafePathError);
      expect(e.item).toBe(item);
      expect(f.calls).toEqual([['lstatSync', '/r']]);
    }

    const entries = deepFreeze({
      '/r': { kind: 'dir' },
      '/r/z.txt': { kind: 'file' },
      '/r/a-link': { kind: 'symlink' },
      '/r/.git': { kind: 'dir' },
      '/r/.git/HEAD': { kind: 'file' },
      '/r/.git/evil': { kind: 'symlink' },
      '/r/.venv': { kind: 'symlink' },
      '/r/docs': { kind: 'dir' },
      '/r/docs/b.md': { kind: 'file' },
      '/r/docs/dlink': { kind: 'symlink' },
      '/r/tests': { kind: 'dir' },
      '/r/tests/z.js': { kind: 'file' },
      '/r/tests/b': { kind: 'dir' },
      '/r/tests/b/a.js': { kind: 'file' },
      '/r/tests/b/fifo': { kind: 'fifo' },
      '/r/tests/a.js': { kind: 'file' },
      '/r/tests/node_modules': { kind: 'dir' },
      '/r/tests/node_modules/.bin': { kind: 'dir' },
      '/r/tests/node_modules/.bin/x': { kind: 'symlink' },
      '/r/tests/.tmp': { kind: 'symlink' },
      '/r/tests/test-results': { kind: 'dir' },
      '/r/tests/test-results/r.txt': { kind: 'file' },
    });
    const f = makeFakeFs(entries);
    const r = scanProject(Object.freeze({ fs: f.fake, root: '/r' }));
    expect(r).toEqual({
      unsafe: ['symlink:.venv', 'symlink:a-link', 'symlink:docs/dlink', 'symlink:tests/.tmp'],
      testsFiles: ['tests/a.js', 'tests/b/a.js', 'tests/b/fifo', 'tests/z.js'],
    });
    const dirsRead = f.calls.filter((c) => c[0] === 'readdirSync').map((c) => c[1]).sort();
    expect(dirsRead).toEqual(['/r', '/r/docs', '/r/tests', '/r/tests/b']);
    const names = new Set(f.calls.map((c) => c[0]));
    expect([...names].sort()).toEqual(['lstatSync', 'readdirSync']);
    expect(f.calls.filter((c) => c[0] === 'lstatSync').every((c) => !c[1].includes('node_modules') && !c[1].includes('.git/'))).toBe(true);
  });

  test('takeCurrent(가짜 fs·git): start key 경로 계약 위반은 fs·git 호출 없이 거부', () => {
    const starts = [
      { files: { '../outside.txt': null }, xy: {} },
      { files: { 'ok.txt': null }, xy: { '/abs': ' M' } },
      { files: { 'a//b': null }, xy: {} },
      { files: { './x': null }, xy: {} },
    ];
    for (const s of starts) {
      const start = deepFreeze(s);
      const f = makeFakeFs({ '/r': { kind: 'dir' } });
      const gitCalls = [];
      const git = (args) => { gitCalls.push(args); return Buffer.alloc(0); };
      const e = errorOf(() => takeCurrent(start, Object.freeze({ git, fs: f.fake, root: '/r' })));
      expect(e).not.toBeNull();
      expect(e.message).toBe('bad start snapshot: paths');
      expect(f.calls).toEqual([]);
      expect(gitCalls).toEqual([]);
    }
  });

  test('takeCurrent(가짜 fs·git): 현재 status 경로 위반은 bad git status, unsafe면 hash 없이 files {}', () => {
    const entries = deepFreeze({
      '/r': { kind: 'dir' },
      '/r/a.txt': { kind: 'file', data: 'a' },
      '/r/ln': { kind: 'symlink' },
      '/r/tests': { kind: 'dir' },
      '/r/tests/t.js': { kind: 'file', data: 't' },
    });
    const gitOf = (status, listed) => (args) => {
      if (JSON.stringify(args) === JSON.stringify(STATUS_ARGS)) return Buffer.from(status, 'utf8');
      if (JSON.stringify(args) === JSON.stringify(LS_FILES_ARGS)) return Buffer.from(listed, 'utf8');
      throw new Error(`unexpected git ${args}`);
    };

    const bad = makeFakeFs(entries);
    const e = errorOf(() => takeCurrent(null, { git: gitOf(`?? ../x${NUL}`, ''), fs: bad.fake, root: '/r' }));
    expect(e?.message).toBe('bad git status');
    expect(bad.calls.map((c) => c[0])).not.toContain('openSync');

    const uns = makeFakeFs(entries);
    const r = takeCurrent(null, { git: gitOf(` M a.txt${NUL}`, `a.txt${NUL}ln${NUL}`), fs: uns.fake, root: '/r' });
    expect(r.unsafe).toEqual(['symlink:ln']);
    expect(r.files).toEqual({});
    expect(r.xy).toEqual({ 'a.txt': ' M' });
    expect(uns.calls.map((c) => c[0])).not.toContain('openSync');

    const clean = { ...entries };
    delete clean['/r/ln'];
    const ok = makeFakeFs(clean);
    const start = deepFreeze({ files: { 'gone.txt': sha256('x') }, xy: {} });
    const r2 = takeCurrent(start, { git: gitOf(` M a.txt${NUL}`, `a.txt${NUL}`), fs: ok.fake, root: '/r' });
    expect(r2).toEqual({
      entries: [{ xy: ' M', path: 'a.txt', origPath: null }],
      xy: { 'a.txt': ' M' },
      files: { 'a.txt': sha256('a'), 'gone.txt': null, 'tests/t.js': sha256('t') },
      unsafe: [],
    });
  });

  test('helper: 합성 git 허용 인자만, 설계 블록 추출, subprocess·exec harness', () => {
    const repo = makeSyntheticRepo();
    try {
      for (const args of [['mv', 'a', 'b'], ['status'], ['add', '-f', 'x'], ['commit', '-m', 'x'], ['init'], ['reset', '--hard'], ['add']]) {
        expect(() => repo.git(args), JSON.stringify(args)).toThrow(/not allowed/);
      }
      repo.git(['init', '-q']);
      expect(fs.statSync(path.join(repo.dir, '.git')).isDirectory()).toBe(true);
      expect(fs.statSync(repo.outside).isDirectory()).toBe(true);

      const sBody = designBlock('스크립트 S');
      expect(sBody).toBe(fs.readFileSync(path.join(REPO_ROOT, 'tests/scripts/start-snapshot.py'), 'utf8'));
      expect(designBlock('inline 범위 검사 C')).toMatch(/^import hashlib, json, os, stat, subprocess, sys\n[\s\S]*print\('scope-snapshot: OK'\)\n$/);
      expect(() => designBlock('없는 marker 문자열')).toThrow();

      expect(runPython(['-I', '-c', 'import sys; print(sys.stdin.read().upper())'], { input: 'abc' }).stdout).toBe('ABC\n');
      const n = runNode(['-e', 'process.stdout.write(process.cwd())'], { cwd: repo.dir });
      expect(n.code).toBe(0);
      expect(fs.realpathSync(n.stdout)).toBe(fs.realpathSync(repo.dir));

      fs.symlinkSync(path.basename(repo.dir), repo.link);
      const h = runHarness(sBody, { cwd: repo.dir, toplevel: repo.link, argv: ['parity-1'] });
      expect(h.error).toBeNull();
      expect(h.exit).toBe(`unsafe path: symlink:${repo.link}`);
      expect(h.calls.filter((c) => c[0] === 'os.lstat')).toEqual([['os.lstat', [repo.link]]]);
    } finally {
      repo.cleanup();
    }
    expect(fs.existsSync(repo.dir)).toBe(false);
    expect(fs.existsSync(repo.outside)).toBe(false);
    expect(errorOf(() => fs.lstatSync(repo.link))?.code).toBe('ENOENT');
  });

  test('합성 저장소: 추적·수정·ignore 파일 hash 수집, runtime 제외, rename, runtime 내부 링크', () => {
    const repo = makeSyntheticRepo();
    try {
      const { dir } = repo;
      const git = gitReader(dir);
      repo.git(['init', '-q']);
      write(dir, '.gitignore', 'tests/fixtures/local.json\ntests/.tmp/\n');
      write(dir, 'tracked.txt', 'v1\n');
      write(dir, 'tests/specs/a.spec.js', 'spec a\n');
      repo.git(['add', '-A']);
      repo.git(['-c', 'user.name=t', '-c', 'user.email=t@example.invalid', 'commit', '-q', '-m', 'init']);

      write(dir, 'tracked.txt', 'v2\n');
      write(dir, 'tests/fixtures/local.json', '{"local":true}\n');
      write(dir, 'tests/.tmp/x', 'runtime\n');

      const opts = Object.freeze({ root: dir, git });
      const cur = takeCurrent(null, opts);
      expect(cur.unsafe).toEqual([]);
      expect(cur.xy).toEqual({ 'tracked.txt': ' M' });
      expect(cur.files).toEqual({
        '.gitignore': sha256('tests/fixtures/local.json\ntests/.tmp/\n'),
        'tests/fixtures/local.json': sha256('{"local":true}\n'),
        'tests/specs/a.spec.js': sha256('spec a\n'),
        'tracked.txt': sha256('v2\n'),
      });
      expect(Object.keys(cur.files)).toEqual([...Object.keys(cur.files)].sort());

      // rename: git mv 없이 fs 이동 후 add -A
      const start = deepFreeze(structuredClone({ files: cur.files, xy: cur.xy }));
      fs.renameSync(path.join(dir, 'tests/specs/a.spec.js'), path.join(dir, 'tests/specs/b.spec.js'));
      repo.git(['add', '-A']);
      const after = takeCurrent(start, opts);
      expect(after.unsafe).toEqual([]);
      expect(after.entries).toContainEqual({ xy: 'R ', path: 'tests/specs/b.spec.js', origPath: 'tests/specs/a.spec.js' });
      expect(after.xy['tests/specs/b.spec.js']).toBe('R ');
      expect(after.xy['tests/specs/a.spec.js']).toBe('R ');
      expect(after.files['tests/specs/b.spec.js']).toBe(sha256('spec a\n'));
      expect(after.files['tests/specs/a.spec.js']).toBeNull();
      expect(fs.existsSync(path.join(dir, 'tests/specs/a.spec.js'))).toBe(false);
      expect(start.files['tests/specs/a.spec.js']).toBe(sha256('spec a\n'));

      // runtime 내부 링크는 걷지 않으므로 unsafe가 아니다
      fs.mkdirSync(path.join(dir, 'tests/node_modules/.bin'), { recursive: true });
      fs.symlinkSync('../pkg/x.js', path.join(dir, 'tests/node_modules/.bin/x'));
      const rt = takeCurrent(start, opts);
      expect(rt.unsafe).toEqual([]);
      expect(Object.keys(rt.files).some((p) => p.startsWith('tests/node_modules/'))).toBe(false);
      expect(scanProject({ root: dir }).unsafe).toEqual([]);
    } finally {
      repo.cleanup();
    }
    expect(fs.existsSync(repo.dir)).toBe(false);
  });

  test('parity(실제 저장소 읽기 전용): S 생성 snapshot의 xy·files = takeCurrent(null)', () => {
    const id = `parity-${process.pid}`;
    const rel = `tests/.tmp/start-snapshot-${id}.json`;
    const abs = path.join(REPO_ROOT, rel);
    fs.rmSync(abs, { force: true });
    try {
      const s = runPython(['-I', 'tests/scripts/start-snapshot.py', id], { cwd: REPO_ROOT });
      expect(s.code, s.stderr).toBe(0);
      expect(s.stdout.trim()).toBe(`start-snapshot: created ${rel}`);
      const snap = loadStartSnapshot(rel, { root: REPO_ROOT });
      const cur = takeCurrent(null, { root: REPO_ROOT });
      expect(cur.unsafe).toEqual([]);
      expect(cur.xy).toEqual(snap.xy);
      expect(cur.files).toEqual(snap.files);
    } finally {
      fs.rmSync(abs, { force: true });
    }
    expect(fs.existsSync(abs)).toBe(false);
  });
});
