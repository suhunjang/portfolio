// step 1 — scope-snapshot.mjs 경로 유형·안전 읽기와 projectRoot 유형 거부 parity (node 전용, desktop-dark에서만 실행)
import { test, expect } from '@playwright/test';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  RUNTIME_PREFIXES, SKIP_PREFIXES, EXEMPT_PREFIXES, GUARDED_PATHS, LOCK_PATH, SNAPSHOT_KEYS,
  STEP_ID_RE, HEX64_RE, BASE, HARNESS_IDENTITY, STATUS_ARGS, LS_FILES_ARGS,
  UnsafePathError, checkRoot, pathKind, checkPath, readRegular,
} from '../scripts/scope-snapshot.mjs';

const TESTS_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const REPO_ROOT = path.resolve(TESTS_DIR, '..');
const DESIGN_DOC = path.join(REPO_ROOT, 'docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md');
const S_SCRIPT = path.join(REPO_ROOT, 'tests/scripts/start-snapshot.py');
const SYN_BASE = path.join(REPO_ROOT, 'tests/.tmp/synthetic-repos');
const SNAP_REL = 'tests/.tmp/start-snapshot-parity-1.json';
const AFTER_REL = 'tests/.tmp/start-snapshot-parity-1-after.z';

const sha256 = (buf) => createHash('sha256').update(buf).digest('hex');

// 설계 블록 추출 규칙: 지정 접두어로 시작하는 줄 다음 첫 fenced code block 본문 + 끝 개행 1개
function designBlock(prefix) {
  const lines = fs.readFileSync(DESIGN_DOC, 'utf8').split('\n');
  const i = lines.findIndex((l) => l.startsWith(prefix));
  expect(i, `design marker ${prefix}`).toBeGreaterThanOrEqual(0);
  const open = lines.findIndex((l, n) => n > i && l.startsWith('```'));
  const close = lines.findIndex((l, n) => n > open && l.startsWith('```'));
  expect(open).toBeGreaterThan(i);
  expect(close).toBeGreaterThan(open);
  return `${lines.slice(open + 1, close).join('\n')}\n`;
}

// ---- 가짜 fs: abs 경로 → { kind, data } -------------------------------------------------
function fakeStats(kind) {
  return {
    isFile: () => kind === 'file',
    isDirectory: () => kind === 'dir',
    isSymbolicLink: () => kind === 'symlink',
    isFIFO: () => kind === 'fifo',
    isSocket: () => kind === 'socket',
    isBlockDevice: () => false,
    isCharacterDevice: () => false,
  };
}
function makeFakeFs(entries) {
  const calls = [];
  const fds = new Map();
  let next = 10;
  const enoent = (p) => Object.assign(new Error(`ENOENT: ${p}`), { code: 'ENOENT' });
  const fake = {
    constants: fs.constants,
    lstatSync(p) {
      calls.push(['lstatSync', p]);
      if (!(p in entries)) throw enoent(p);
      return fakeStats(entries[p].kind);
    },
    statSync(p) { calls.push(['statSync', p]); throw new Error('statSync not allowed'); },
    readdirSync(p) { calls.push(['readdirSync', p]); throw new Error('readdirSync not allowed'); },
    realpathSync(p) { calls.push(['realpathSync', p]); throw new Error('realpathSync not allowed'); },
    openSync(p, flags, mode) {
      calls.push(['openSync', p, flags, mode]);
      if (!(p in entries)) throw enoent(p);
      const fd = next++;
      fds.set(fd, p);
      return fd;
    },
    fstatSync(fd) {
      calls.push(['fstatSync', fd]);
      return fakeStats(entries[fds.get(fd)].kind);
    },
    readFileSync(fd) {
      calls.push(['readFileSync', fd]);
      return Buffer.from(entries[fds.get(fd)].data ?? '');
    },
    readSync(fd) { calls.push(['readSync', fd]); throw new Error('readSync not expected'); },
    closeSync(fd) { calls.push(['closeSync', fd]); fds.delete(fd); },
  };
  return { fake, calls };
}

// 실제 fs를 감싸 모든 함수 호출을 기록한다
function recordingFs(calls) {
  return new Proxy(fs, {
    get(target, key) {
      const v = target[key];
      if (typeof v !== 'function') return v;
      return (...args) => {
        calls.push([String(key), ...args.map(String)]);
        return v.apply(target, args);
      };
    },
  });
}

function errorOf(fn) {
  try { fn(); } catch (e) { return e; }
  return null;
}

// ---- S·C exec harness (설계 §11.7, 테스트 전용) -------------------------------------------
const EXEC_HARNESS = String.raw`
import builtins, json, os, subprocess, sys
import hashlib, re, stat
cfg = json.loads(sys.stdin.read())
calls = []
real = {'lstat': os.lstat, 'walk': os.walk, 'open': os.open, 'makedirs': os.makedirs, 'bopen': builtins.open, 'run': subprocess.run}
def rec(name, fn):
    def w(*a, **k):
        calls.append([name, [os.fsdecode(x) if isinstance(x, (str, bytes)) else repr(x) for x in a]])
        return fn(*a, **k)
    return w
def fake_run(args, *a, **k):
    args = list(args)
    if args == ['git', 'rev-parse', '--show-toplevel']:
        calls.append(['git-toplevel', args])
        return subprocess.CompletedProcess(args, 0, (cfg['top'] + '\n').encode(), b'')
    calls.append(['git-other', [str(x) for x in args]])
    raise RuntimeError('unexpected subprocess: ' + repr(args))
os.lstat = rec('os.lstat', real['lstat'])
os.walk = rec('os.walk', real['walk'])
os.open = rec('os.open', real['open'])
os.makedirs = rec('os.makedirs', real['makedirs'])
builtins.open = rec('open', real['bopen'])
subprocess.run = fake_run
sys.argv = ['-'] + cfg['argv']
result = {'exit': None, 'error': None}
try:
    exec(compile(cfg['body'], '<body>', 'exec'), {'__name__': '__main__'})
except SystemExit as e:
    result['exit'] = e.code if isinstance(e.code, (str, int)) or e.code is None else repr(e.code)
except BaseException as e:
    result['error'] = repr(e)
finally:
    os.lstat, os.walk, os.open, os.makedirs = real['lstat'], real['walk'], real['open'], real['makedirs']
    builtins.open, subprocess.run = real['bopen'], real['run']
result['calls'] = calls
sys.stdout.write(json.dumps(result))
`;

function execBody(body, argv, top, cwd) {
  const r = spawnSync('python3', ['-I', '-c', EXEC_HARNESS], {
    cwd, input: JSON.stringify({ body, argv, top }), encoding: 'utf8', timeout: 10000,
  });
  if (r.error) throw r.error;
  expect(r.status, r.stderr).toBe(0);
  return JSON.parse(r.stdout);
}

// 합성 디렉터리 상태(목록·bytes·mtime), 링크를 따라가지 않는다
function treeState(dir) {
  const out = [];
  const walk = (rel) => {
    const abs = rel ? path.join(dir, rel) : dir;
    const st = fs.lstatSync(abs);
    const rec = { rel, mode: st.mode, size: st.size, mtimeMs: st.mtimeMs };
    if (st.isFile()) rec.sha = sha256(fs.readFileSync(abs));
    out.push(rec);
    if (st.isDirectory()) {
      for (const n of fs.readdirSync(abs).sort()) walk(rel ? `${rel}/${n}` : n);
    }
  };
  walk('');
  return JSON.stringify(out);
}

test.describe('step 1 scope-snapshot paths', () => {
  test.beforeEach(({}, testInfo) => {
    test.skip(testInfo.project.name !== 'desktop-dark', 'node 전용 검사는 desktop-dark에서만 실행');
  });

  test('상수는 설계 값과 같고 고정되어 있다', () => {
    expect(RUNTIME_PREFIXES).toEqual(['tests/node_modules/', 'tests/.npm-cache/', 'tests/.pw-browsers/', 'tests/.tmp/', 'tests/test-results/', 'tests/playwright-report/', 'tests/screenshots/']);
    expect(SKIP_PREFIXES).toEqual([...RUNTIME_PREFIXES, '.git/', '.venv/']);
    expect(EXEMPT_PREFIXES).toEqual(['.harness/', '.venv/', 'phases/HOO-81-portfolio-redesign/']);
    expect(GUARDED_PATHS).toEqual(['.harness/harness.lock.json', '.harness/policy.json']);
    expect(LOCK_PATH).toBe('.harness/harness.lock.json');
    expect([...SNAPSHOT_KEYS].sort()).toEqual(['base', 'files', 'harness', 'head', 'projectRoot', 'schemaVersion', 'statusZHex', 'stepId', 'xy']);
    for (const ok of ['step0', 'step12', 'axe-remediation-a1', 'axe-remediation-a-b2', 'parity-17']) expect(STEP_ID_RE.test(ok), ok).toBe(true);
    for (const bad of ['step', 'Step1', '../x', 'parity-x', 'axe-remediation-', 'step1x', 'xstep1']) expect(STEP_ID_RE.test(bad), bad).toBe(false);
    expect(HEX64_RE.test('a'.repeat(64))).toBe(true);
    for (const bad of ['A'.repeat(64), 'a'.repeat(63), 'a'.repeat(65), `${'a'.repeat(64)}\n`]) expect(HEX64_RE.test(bad)).toBe(false);
    expect(STATUS_ARGS).toEqual(['status', '--porcelain=v1', '-z', '--untracked-files=all']);
    expect(LS_FILES_ARGS).toEqual(['ls-files', '-z']);
    // S 본문의 BASE·HARNESS와 같은 값
    const s = fs.readFileSync(S_SCRIPT, 'utf8');
    expect(s).toContain(`BASE = '${BASE}'`);
    expect(Object.keys(HARNESS_IDENTITY).sort()).toEqual(['distributionVersion', 'manifestHash', 'sourceCommit']);
    for (const [k, v] of Object.entries(HARNESS_IDENTITY)) expect(s).toContain(`'${k}': '${v}'`);
    for (const c of [RUNTIME_PREFIXES, SKIP_PREFIXES, EXEMPT_PREFIXES, GUARDED_PATHS, SNAPSHOT_KEYS, HARNESS_IDENTITY, STATUS_ARGS, LS_FILES_ARGS]) {
      expect(Object.isFrozen(c)).toBe(true);
    }
  });

  test('UnsafePathError는 item과 unsafe path 메시지를 가진다', () => {
    const e = new UnsafePathError('symlink:a/b');
    expect(e).toBeInstanceOf(Error);
    expect(e.item).toBe('symlink:a/b');
    expect(e.message).toBe('unsafe path: symlink:a/b');
  });

  test('checkRoot(가짜 fs): root lstat 1회로 유형 판정', () => {
    const cases = [
      ['symlink', 'symlink:/r'],
      ['file', 'non-regular:/r'],
      ['fifo', 'non-regular:/r'],
      [null, 'missing:/r'],
    ];
    for (const [kind, item] of cases) {
      const { fake, calls } = makeFakeFs(kind ? { '/r': { kind } } : {});
      const opts = Object.freeze({ fs: fake, root: '/r' });
      const e = errorOf(() => checkRoot(opts));
      expect(e, String(kind)).toBeInstanceOf(UnsafePathError);
      expect(e.item).toBe(item);
      expect(calls).toEqual([['lstatSync', '/r']]);
    }
    const { fake, calls } = makeFakeFs({ '/r': { kind: 'dir' } });
    expect(errorOf(() => checkRoot({ fs: fake, root: '/r' }))).toBeNull();
    expect(calls).toEqual([['lstatSync', '/r']]);
  });

  test('pathKind(가짜 fs): lstat만으로 유형', () => {
    const { fake, calls } = makeFakeFs({
      '/r': { kind: 'dir' }, '/r/f': { kind: 'file' }, '/r/d': { kind: 'dir' }, '/r/l': { kind: 'symlink' },
      '/r/p': { kind: 'fifo' }, '/r/s': { kind: 'socket' },
    });
    const opts = Object.freeze({ fs: fake, root: '/r' });
    expect(['f', 'd', 'l', 'p', 's', 'none'].map((p) => pathKind(p, opts))).toEqual(['file', 'dir', 'symlink', 'other', 'other', 'missing']);
    expect(calls.every(([name]) => name === 'lstatSync')).toBe(true);
    expect(calls.map((c) => c[1])).toEqual(['/r/f', '/r/d', '/r/l', '/r/p', '/r/s', '/r/none']);
  });

  test('checkPath(가짜 fs): root 오류 전파·조상·leaf 규칙, lstat만', () => {
    // root 오류는 그대로 전파되고 하위 접근이 없다
    for (const [kind, item] of [['symlink', 'symlink:/r'], ['file', 'non-regular:/r'], [null, 'missing:/r']]) {
      const { fake, calls } = makeFakeFs(kind ? { '/r': { kind }, '/r/a': { kind: 'file' } } : { '/r/a': { kind: 'file' } });
      const e = errorOf(() => checkPath('a', ['file'], { fs: fake, root: '/r' }));
      expect(e, String(kind)).toBeInstanceOf(UnsafePathError);
      expect(e.item).toBe(item);
      expect(calls).toEqual([['lstatSync', '/r']]);
    }

    const entries = {
      '/r': { kind: 'dir' },
      '/r/a': { kind: 'symlink' },
      '/r/f': { kind: 'file' },
      '/r/d': { kind: 'dir' },
      '/r/d/file': { kind: 'file' },
      '/r/d/sub': { kind: 'dir' },
      '/r/d/fifo': { kind: 'fifo' },
      '/r/d/sock': { kind: 'socket' },
      '/r/d/ln': { kind: 'symlink' },
      '/r/d/e': { kind: 'dir' },
      '/r/d/e/p': { kind: 'fifo' },
    };
    const MF = Object.freeze(['missing', 'file']);
    const F = Object.freeze(['file']);
    const cases = [
      ['a/b/c', MF, 'symlink:a', ['/r', '/r/a']],
      ['f/x', MF, 'non-regular:f', ['/r', '/r/f']],
      ['d/e/p/x', MF, 'non-regular:d/e/p', ['/r', '/r/d', '/r/d/e', '/r/d/e/p']],
      ['nope/x/y', MF, null, ['/r', '/r/nope']],
      ['nope/x', F, 'missing:nope/x', ['/r', '/r/nope']],
      ['d/none', F, 'missing:d/none', ['/r', '/r/d', '/r/d/none']],
      ['d/none', MF, null, ['/r', '/r/d', '/r/d/none']],
      ['d/file', F, null, ['/r', '/r/d', '/r/d/file']],
      ['d/sub', MF, 'non-regular:d/sub', ['/r', '/r/d', '/r/d/sub']],
      ['d/sub', Object.freeze(['missing', 'dir']), null, ['/r', '/r/d', '/r/d/sub']],
      ['d/fifo', MF, 'non-regular:d/fifo', ['/r', '/r/d', '/r/d/fifo']],
      ['d/sock', MF, 'non-regular:d/sock', ['/r', '/r/d', '/r/d/sock']],
      ['d/ln', MF, 'symlink:d/ln', ['/r', '/r/d', '/r/d/ln']],
      ['f', F, null, ['/r', '/r/f']],
    ];
    for (const [p, leaf, want, lstats] of cases) {
      const { fake, calls } = makeFakeFs(entries);
      const opts = Object.freeze({ fs: fake, root: '/r' });
      expect(checkPath(p, leaf, opts), `${p} ${leaf}`).toBe(want);
      expect(calls, p).toEqual(lstats.map((x) => ['lstatSync', x]));
    }
  });

  test('readRegular(가짜 fs): O_NOFOLLOW·O_NONBLOCK, FIFO는 read 없이 거부', () => {
    const { O_RDONLY, O_NOFOLLOW, O_NONBLOCK } = fs.constants;
    const entries = { '/r/ok.txt': { kind: 'file', data: 'hello' }, '/r/p': { kind: 'fifo' } };

    const ok = makeFakeFs(entries);
    const buf = readRegular('ok.txt', Object.freeze({ fs: ok.fake, root: '/r' }));
    expect(Buffer.from(buf).toString()).toBe('hello');
    const openCall = ok.calls.find((c) => c[0] === 'openSync');
    expect(openCall[1]).toBe('/r/ok.txt');
    expect(openCall[2]).toBe(O_RDONLY | O_NOFOLLOW | O_NONBLOCK);
    expect(openCall[2] & O_NOFOLLOW).toBe(O_NOFOLLOW);
    expect(openCall[2] & O_NONBLOCK).toBe(O_NONBLOCK);
    expect(ok.calls.map((c) => c[0])).toEqual(['openSync', 'fstatSync', 'readFileSync', 'closeSync']);

    const bad = makeFakeFs(entries);
    const e = errorOf(() => readRegular('p', Object.freeze({ fs: bad.fake, root: '/r' })));
    expect(e).toBeInstanceOf(UnsafePathError);
    expect(e.item).toBe('non-regular:p');
    expect(e.message).toBe('unsafe path: non-regular:p');
    const names = bad.calls.map((c) => c[0]);
    expect(names).not.toContain('readFileSync');
    expect(names).not.toContain('readSync');
    expect(names.slice(0, 2)).toEqual(['openSync', 'fstatSync']);
    expect(names).toContain('closeSync');
  });

  test('합성 projectRoot symlink·non-directory: JS·S·C 모두 하위 접근 없이 거부', () => {
    const pid = String(process.pid);
    const dir = path.join(SYN_BASE, pid);
    const link = path.join(SYN_BASE, `${pid}-link`);
    const file = path.join(SYN_BASE, `${pid}-file`);
    const cleanup = () => {
      fs.rmSync(dir, { recursive: true, force: true });
      fs.rmSync(link, { force: true });
      fs.rmSync(file, { force: true });
    };
    cleanup();
    try {
      fs.mkdirSync(dir, { recursive: true });
      const g = spawnSync('git', ['-C', dir, 'init', '-q'], { encoding: 'utf8', timeout: 10000 });
      expect(g.status, g.stderr).toBe(0);
      fs.mkdirSync(path.join(dir, 'tests/.tmp'), { recursive: true });
      const snap = {
        base: BASE,
        files: {},
        harness: { ...HARNESS_IDENTITY, lockSha256: '0'.repeat(64) },
        head: '0'.repeat(40),
        projectRoot: fs.realpathSync(dir),
        schemaVersion: 1,
        statusZHex: '',
        stepId: 'parity-1',
        xy: {},
      };
      fs.writeFileSync(path.join(dir, SNAP_REL), JSON.stringify(snap, null, 1));
      fs.symlinkSync(pid, link);
      fs.writeFileSync(file, 'not a directory\n');

      const realTmp = path.join(REPO_ROOT, 'tests/.tmp');
      const realListing = () => JSON.stringify(fs.readdirSync(realTmp).filter((n) => n.startsWith('start-snapshot-parity-1')).sort());
      const before = treeState(dir);
      const siblings = () => JSON.stringify([fs.lstatSync(link), fs.lstatSync(file)].map((s) => [s.mode, s.size, s.mtimeMs]));
      const sibBefore = siblings();
      const realBefore = realListing();

      // JS
      for (const [root, item] of [[link, `symlink:${link}`], [file, `non-regular:${file}`]]) {
        const calls = [];
        const leaf = Object.freeze(['file']);
        const e = errorOf(() => checkPath(SNAP_REL, leaf, Object.freeze({ root, fs: recordingFs(calls) })));
        expect(e).toBeInstanceOf(UnsafePathError);
        expect(e.item).toBe(item);
        expect(calls).toEqual([['lstatSync', root]]);
      }

      // S·C (설계 S·C exec harness)
      const bodies = [
        ['S', fs.readFileSync(S_SCRIPT, 'utf8'), ['parity-1']],
        ['C', designBlock('inline 범위 검사 C'), ['parity-1', '', '']],
      ];
      for (const [name, body, argv] of bodies) {
        for (const [top, item] of [[link, `symlink:${link}`], [file, `non-regular:${file}`]]) {
          const r = execBody(body, argv, top, dir);
          const tag = `${name} ${item}`;
          expect(r.error, tag).toBeNull();
          expect(r.exit, tag).toBe(`unsafe path: ${item}`);
          const by = (n) => r.calls.filter((c) => c[0] === n);
          expect(by('os.lstat'), tag).toEqual([['os.lstat', [top]]]);
          for (const n of ['os.walk', 'os.open', 'os.makedirs', 'open', 'git-other']) expect(by(n), `${tag} ${n}`).toEqual([]);
          expect(by('git-toplevel').length, tag).toBe(1);
        }
      }

      expect(treeState(dir)).toBe(before);
      expect(siblings()).toBe(sibBefore);
      expect(fs.existsSync(path.join(dir, AFTER_REL))).toBe(false);
      expect(fs.readdirSync(path.join(dir, 'tests/.tmp'))).toEqual(['start-snapshot-parity-1.json']);
      expect(realListing()).toBe(realBefore);
    } finally {
      cleanup();
    }
    expect(fs.existsSync(dir)).toBe(false);
    expect(errorOf(() => fs.lstatSync(link))?.code).toBe('ENOENT');
    expect(errorOf(() => fs.lstatSync(file))?.code).toBe('ENOENT');
  });
});
