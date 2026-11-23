// step 6 — 특수 파일(FIFO·디렉터리)·조상 symlink 거부를 S·C·JS loader·takeCurrent로 실행 검증
// (node 전용, desktop-dark에서만 실행. 코드 추가 없음, 테스트만)
import { test, expect } from '@playwright/test';
import { spawnSync } from 'node:child_process';
import { createHash, randomBytes } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import {
  STATUS_ARGS, LS_FILES_ARGS, BASE, HARNESS_IDENTITY, takeCurrent, loadStartSnapshot,
} from '../scripts/scope-snapshot.mjs';
import { REPO_ROOT, makeSyntheticRepo, designBlock, isolatedGitEnv } from '../helpers/synthetic-repo.js';

const TIMEOUT = 10000;
const S_SCRIPT = path.join(REPO_ROOT, 'tests/scripts/start-snapshot.py');
const SNAP_REL = 'tests/.tmp/start-snapshot-parity-1.json';
const AFTER_REL = 'tests/.tmp/start-snapshot-parity-1-after.z';
const COMMIT = ['-c', 'user.name=t', '-c', 'user.email=t@example.invalid', 'commit', '-q', '-m', 'init'];

const sha256 = (buf) => createHash('sha256').update(buf).digest('hex');

// subprocess: 부모 GIT_* 변수를 지운 환경, timeout 10초(timeout·spawn 오류는 실패)
function py(args, { cwd, input, env = isolatedGitEnv() } = {}) {
  const r = spawnSync('python3', args, { cwd, input, env, encoding: 'utf8', timeout: TIMEOUT });
  expect(r.error, 'python subprocess error/timeout').toBeUndefined();
  expect(r.signal, 'python subprocess signal').toBeNull();
  return { code: r.status, stdout: r.stdout, stderr: r.stderr };
}

const runS = (dir, stepId = 'parity-1') => py(['-I', S_SCRIPT, stepId], { cwd: dir });
const runC = (dir) => py(['-I', '-', 'parity-1', '', ''], { cwd: dir, input: designBlock('inline 범위 검사 C') });

function mkfifo(abs) {
  fs.mkdirSync(path.dirname(abs), { recursive: true });
  const r = spawnSync('python3', ['-I', '-c', 'import os, sys; os.mkfifo(sys.argv[1])', abs], { timeout: TIMEOUT });
  expect(r.error).toBeUndefined();
  expect(r.status, String(r.stderr)).toBe(0);
  expect(fs.lstatSync(abs).isFIFO()).toBe(true);
}

// 합성 저장소용 Git 읽기 전용 주입 함수 (status·ls-files만)
function gitReader(dir) {
  return (args) => {
    const a = JSON.stringify([...args]);
    if (a !== JSON.stringify(STATUS_ARGS) && a !== JSON.stringify(LS_FILES_ARGS)) throw new Error(`git read not allowed: ${a}`);
    const r = spawnSync('git', ['-C', dir, ...args], { env: isolatedGitEnv(), timeout: TIMEOUT });
    if (r.error) throw r.error;
    if (r.status !== 0) throw new Error(`git failed: ${r.stderr}`);
    return r.stdout;
  };
}

// 실제 fs를 감싸 호출(이름, 경로 또는 fd)을 기록한다
function recordingFs() {
  const calls = [];
  const wrap = (name) => (...args) => {
    calls.push([name, typeof args[0] === 'number' ? args[0] : String(args[0])]);
    return fs[name](...args);
  };
  const names = ['lstatSync', 'readdirSync', 'openSync', 'fstatSync', 'readFileSync', 'closeSync',
    'statSync', 'readlinkSync', 'realpathSync', 'existsSync', 'opendirSync', 'accessSync'];
  const fake = { constants: fs.constants };
  for (const n of names) fake[n] = wrap(n);
  return { fake, calls };
}

function write(dir, rel, data) {
  fs.mkdirSync(path.dirname(path.join(dir, rel)), { recursive: true });
  fs.writeFileSync(path.join(dir, rel), data);
}

// 디렉터리 상태 기록: 파일 목록·유형(file/dir/fifo/symlink)·regular sha256·mtime (링크는 따라가지 않음, FIFO는 열지 않음)
function inventory(root, { skip = [] } = {}) {
  const out = {};
  const walk = (rel) => {
    const abs = rel ? path.join(root, rel) : root;
    for (const name of fs.readdirSync(abs).sort()) {
      const r = rel ? `${rel}/${name}` : name;
      if (skip.includes(r)) continue;
      const p = path.join(root, r);
      const st = fs.lstatSync(p);
      if (st.isSymbolicLink()) out[r] = { type: 'symlink', target: fs.readlinkSync(p) };
      else if (st.isDirectory()) {
        out[r] = { type: 'dir' };
        walk(r);
      } else if (st.isFile()) out[r] = { type: 'file', sha: sha256(fs.readFileSync(p)), mtimeMs: st.mtimeMs };
      else if (st.isFIFO()) out[r] = { type: 'fifo' };
      else out[r] = { type: 'other' };
    }
  };
  walk('');
  return out;
}

// 정상 형식(strict schema) snapshot bytes
function normalSnapshot(dir) {
  const obj = {
    base: BASE,
    files: {},
    harness: { ...HARNESS_IDENTITY, lockSha256: sha256('{}\n') },
    head: '0'.repeat(40),
    projectRoot: fs.realpathSync(dir),
    schemaVersion: 1,
    statusZHex: '',
    stepId: 'parity-1',
    xy: {},
  };
  return Buffer.from(JSON.stringify(obj, null, 1), 'utf8');
}

// 합성 저장소 골격: lock·.gitignore(runtime)·추적 파일(tracked.txt, lib/x.txt) commit, 고유 sentinel
function setup(repo) {
  const sentinel = `SENTINEL-${process.pid}-${randomBytes(8).toString('hex')}`;
  repo.git(['init', '-q']);
  write(repo.dir, '.gitignore', 'tests/.tmp/\n');
  write(repo.dir, '.harness/harness.lock.json', '{}\n');
  write(repo.dir, 'tracked.txt', 'tracked\n');
  write(repo.dir, 'lib/x.txt', 'lib\n');
  write(repo.dir, 'tests/specs/x.spec.js', 'x\n');
  repo.git(['add', '-A']);
  repo.git(COMMIT);
  return sentinel;
}

// 실행 전후 대상 디렉터리(.git 제외)와 외부 디렉터리 상태가 같아야 한다
function snapshotDirs(repo) {
  return { dir: inventory(repo.dir, { skip: ['.git'] }), outside: inventory(repo.outside) };
}

function withRepo(fn) {
  const repo = makeSyntheticRepo();
  try {
    fn(repo, setup(repo));
  } finally {
    repo.cleanup();
  }
  expect(fs.existsSync(repo.dir)).toBe(false);
  expect(fs.existsSync(repo.outside)).toBe(false);
}

// S(합성, BASE 없음): 유형 검사 실패가 BASE 오류보다 먼저, 상태 불변
function expectSRejects(repo, item, sentinel) {
  const before = snapshotDirs(repo);
  const s = runS(repo.dir);
  expect(s.code).not.toBe(0);
  expect(s.stderr.trim()).toBe(`unsafe path: ${item}`);
  expect(s.stdout).toBe('');
  if (sentinel) expect(s.stdout + s.stderr).not.toContain(sentinel);
  expect(snapshotDirs(repo)).toEqual(before);
}

// C(합성): exit 1, 정확한 unsafe 한 줄, 상태 불변
function expectCRejects(repo, item, sentinel) {
  const before = snapshotDirs(repo);
  const c = runC(repo.dir);
  expect(c.code).toBe(1);
  expect(c.stderr.trim()).toBe(`unsafe path: ${item}`);
  expect(c.stdout).not.toContain('scope-snapshot: OK');
  if (sentinel) expect(c.stdout + c.stderr).not.toContain(sentinel);
  expect(snapshotDirs(repo)).toEqual(before);
}

// JS takeCurrent: unsafe [item], files {}, open·read 없음, 상태 불변
function expectTakeCurrentRejects(repo, item, forbidden) {
  const before = snapshotDirs(repo);
  const rec = recordingFs();
  const cur = takeCurrent(null, { root: repo.dir, fs: rec.fake, git: gitReader(repo.dir) });
  expect(cur.unsafe).toEqual([item]);
  expect(cur.files).toEqual({});
  const names = rec.calls.map((c) => c[0]);
  for (const n of ['openSync', 'readFileSync', 'statSync', 'readlinkSync', 'realpathSync']) expect(names, n).not.toContain(n);
  for (const [name, p] of rec.calls) {
    if (typeof p !== 'string') continue;
    expect(p === repo.outside || p.startsWith(`${repo.outside}/`), `${name} ${p}`).toBe(false);
    if (forbidden) expect(p.startsWith(`${forbidden}/`), `${name} ${p}`).toBe(false);
  }
  expect(snapshotDirs(repo)).toEqual(before);
}

// (f)·(g) 공통: tests/.tmp → <outside>/tmpdir (sentinel + 정상 형식 snapshot 사본)
function linkTmpOutside(repo, sentinel) {
  const tmpdir = path.join(repo.outside, 'tmpdir');
  write(tmpdir, 'secret.txt', `${sentinel}\n`);
  write(tmpdir, 'start-snapshot-parity-1.json', normalSnapshot(repo.dir));
  fs.mkdirSync(path.join(repo.dir, 'tests'), { recursive: true });
  fs.symlinkSync(tmpdir, path.join(repo.dir, 'tests/.tmp'));
  return tmpdir;
}

test.describe('step 6 scope-snapshot special files', () => {
  test.beforeEach(({}, testInfo) => {
    test.skip(testInfo.project.name !== 'desktop-dark', 'node 전용 검사는 desktop-dark에서만 실행');
  });

  test('S (a) snapshot FIFO → non-regular, FIFO 유지·새 파일 없음', () => {
    withRepo((repo) => {
      const abs = path.join(repo.dir, SNAP_REL);
      mkfifo(abs);
      expectSRejects(repo, `non-regular:${SNAP_REL}`);
      expect(fs.lstatSync(abs).isFIFO()).toBe(true);
      expect(fs.readdirSync(path.dirname(abs))).toEqual([path.basename(abs)]);
    });
  });

  test('S (b) snapshot 디렉터리 → non-regular, 내용 불변', () => {
    withRepo((repo) => {
      write(repo.dir, `${SNAP_REL}/inner.txt`, 'inner\n');
      expectSRejects(repo, `non-regular:${SNAP_REL}`);
      expect(fs.readFileSync(path.join(repo.dir, SNAP_REL, 'inner.txt'), 'utf8')).toBe('inner\n');
    });
  });

  test('S·takeCurrent (c) 기록 대상 FIFO tests/specs/p.fifo → non-regular, tests/.tmp 미생성', () => {
    withRepo((repo) => {
      const abs = path.join(repo.dir, 'tests/specs/p.fifo');
      mkfifo(abs);
      expect(fs.existsSync(path.join(repo.dir, 'tests/.tmp'))).toBe(false);
      expectSRejects(repo, 'non-regular:tests/specs/p.fifo');
      expectTakeCurrentRejects(repo, 'non-regular:tests/specs/p.fifo');
      expect(fs.existsSync(path.join(repo.dir, 'tests/.tmp'))).toBe(false);
      expect(fs.lstatSync(abs).isFIFO()).toBe(true);
    });
  });

  test('S·takeCurrent (d) commit된 tracked.txt → 디렉터리 → non-regular:tracked.txt', () => {
    withRepo((repo) => {
      fs.rmSync(path.join(repo.dir, 'tracked.txt'));
      write(repo.dir, 'tracked.txt/x', 'x\n');
      expectSRejects(repo, 'non-regular:tracked.txt');
      expectTakeCurrentRejects(repo, 'non-regular:tracked.txt');
      expect(fs.existsSync(path.join(repo.dir, 'tests/.tmp'))).toBe(false);
    });
  });

  test('S·takeCurrent (e) 조상 symlink lib → outside → symlink:lib, sentinel 미출력', () => {
    withRepo((repo, sentinel) => {
      write(repo.outside, 'x.txt', `${sentinel}\n`);
      fs.rmSync(path.join(repo.dir, 'lib'), { recursive: true });
      fs.symlinkSync(repo.outside, path.join(repo.dir, 'lib'));
      expectSRejects(repo, 'symlink:lib', sentinel);
      expectTakeCurrentRejects(repo, 'symlink:lib', path.join(repo.dir, 'lib'));
      expect(fs.readFileSync(path.join(repo.outside, 'x.txt'), 'utf8')).toBe(`${sentinel}\n`);
    });
  });

  test('S (f) tests/.tmp → 외부 디렉터리 symlink → symlink:tests/.tmp, 외부 불변', () => {
    withRepo((repo, sentinel) => {
      const tmpdir = linkTmpOutside(repo, sentinel);
      const ext = inventory(tmpdir);
      expectSRejects(repo, 'symlink:tests/.tmp', sentinel);
      expect(inventory(tmpdir)).toEqual(ext);
      expect(Object.keys(ext).sort()).toEqual(['secret.txt', 'start-snapshot-parity-1.json']);
    });
  });

  test('C (g) tests/.tmp 외부 링크 → symlink:tests/.tmp, 외부에 after.z 미생성', () => {
    withRepo((repo, sentinel) => {
      const tmpdir = linkTmpOutside(repo, sentinel);
      const ext = inventory(tmpdir);
      expectCRejects(repo, 'symlink:tests/.tmp', sentinel);
      expect(inventory(tmpdir)).toEqual(ext);
      expect(fs.existsSync(path.join(tmpdir, 'start-snapshot-parity-1-after.z'))).toBe(false);
    });
  });

  test('C (h) 정상 start + after.z FIFO → non-regular:…-after.z, FIFO 유지', () => {
    withRepo((repo) => {
      write(repo.dir, SNAP_REL, normalSnapshot(repo.dir));
      const after = path.join(repo.dir, AFTER_REL);
      mkfifo(after);
      expectCRejects(repo, `non-regular:${AFTER_REL}`);
      expect(fs.lstatSync(after).isFIFO()).toBe(true);
    });
  });

  test('C (i) after.z → 외부 파일 symlink → symlink:…-after.z, 외부 bytes 불변', () => {
    withRepo((repo, sentinel) => {
      write(repo.dir, SNAP_REL, normalSnapshot(repo.dir));
      write(repo.outside, 'ext.txt', `${sentinel}\n`);
      const extBytes = fs.readFileSync(path.join(repo.outside, 'ext.txt'));
      fs.symlinkSync(path.join(repo.outside, 'ext.txt'), path.join(repo.dir, AFTER_REL));
      expectCRejects(repo, `symlink:${AFTER_REL}`, sentinel);
      expect(fs.readFileSync(path.join(repo.outside, 'ext.txt')).equals(extBytes)).toBe(true);
    });
  });

  test('C (j) snapshot 자체 FIFO → non-regular, 멈추지 않음', () => {
    withRepo((repo) => {
      mkfifo(path.join(repo.dir, SNAP_REL));
      expectCRejects(repo, `non-regular:${SNAP_REL}`);
      expect(fs.lstatSync(path.join(repo.dir, SNAP_REL)).isFIFO()).toBe(true);
    });
  });

  test('JS loader: tests/.tmp 외부 링크 → lstat 3회만, FIFO·디렉터리 snapshot → open 없음', () => {
    withRepo((repo, sentinel) => {
      const tmpdir = linkTmpOutside(repo, sentinel);
      const before = snapshotDirs(repo);
      const rec = recordingFs();
      expect(() => loadStartSnapshot(SNAP_REL, { root: repo.dir, fs: rec.fake })).toThrow('unsafe path: symlink:tests/.tmp');
      expect(rec.calls).toEqual([
        ['lstatSync', repo.dir],
        ['lstatSync', path.join(repo.dir, 'tests')],
        ['lstatSync', path.join(repo.dir, 'tests/.tmp')],
      ]);
      expect(snapshotDirs(repo)).toEqual(before);
      fs.rmSync(path.join(repo.dir, 'tests/.tmp'));
      expect(fs.existsSync(tmpdir)).toBe(true);

      const abs = path.join(repo.dir, SNAP_REL);
      mkfifo(abs);
      const recFifo = recordingFs();
      expect(() => loadStartSnapshot(SNAP_REL, { root: repo.dir, fs: recFifo.fake })).toThrow(`unsafe path: non-regular:${SNAP_REL}`);
      expect(recFifo.calls.every(([n]) => n === 'lstatSync')).toBe(true);
      expect(fs.lstatSync(abs).isFIFO()).toBe(true);
      fs.rmSync(abs);

      write(repo.dir, `${SNAP_REL}/inner.txt`, 'inner\n');
      const recDir = recordingFs();
      expect(() => loadStartSnapshot(SNAP_REL, { root: repo.dir, fs: recDir.fake })).toThrow(`unsafe path: non-regular:${SNAP_REL}`);
      expect(recDir.calls.every(([n]) => n === 'lstatSync')).toBe(true);
      expect(fs.readFileSync(path.join(abs, 'inner.txt'), 'utf8')).toBe('inner\n');
    });
  });

  test('S 실제 저장소: parity snapshot 위치 FIFO·디렉터리 → non-regular, 다른 parity 불변', () => {
    const n = process.pid * 1000;
    const [A, m] = [n + 601, n + 602];
    const rel = (x) => `tests/.tmp/start-snapshot-parity-${x}.json`;
    const abs = (x) => path.join(REPO_ROOT, rel(x));
    const tmp = path.join(REPO_ROOT, 'tests/.tmp');
    const parityFiles = () => Object.fromEntries(fs.readdirSync(tmp)
      .filter((f) => /^start-snapshot-.*\.json$/.test(f) && fs.lstatSync(path.join(tmp, f)).isFile())
      .map((f) => [f, { sha: sha256(fs.readFileSync(path.join(tmp, f))), mtimeMs: fs.lstatSync(path.join(tmp, f)).mtimeMs }]));
    const realS = (x) => py(['-I', 'tests/scripts/start-snapshot.py', `parity-${x}`], { cwd: REPO_ROOT, env: process.env });
    const clean = () => { for (const x of [m, A]) fs.rmSync(abs(x), { recursive: true, force: true }); };
    clean();
    try {
      const s = realS(A);
      expect(s.code, s.stderr).toBe(0);
      expect(s.stdout.trim()).toBe(`start-snapshot: created ${rel(A)}`);

      // FIFO
      mkfifo(abs(m));
      let before = parityFiles();
      const r1 = realS(m);
      expect(r1.code).not.toBe(0);
      expect(r1.stderr.trim()).toBe(`unsafe path: non-regular:${rel(m)}`);
      expect(fs.lstatSync(abs(m)).isFIFO()).toBe(true);
      expect(parityFiles()).toEqual(before);
      fs.rmSync(abs(m));

      // 디렉터리
      fs.mkdirSync(abs(m));
      fs.writeFileSync(path.join(abs(m), 'inner.txt'), 'inner\n');
      before = parityFiles();
      const r2 = realS(m);
      expect(r2.code).not.toBe(0);
      expect(r2.stderr.trim()).toBe(`unsafe path: non-regular:${rel(m)}`);
      expect(fs.readdirSync(abs(m))).toEqual(['inner.txt']);
      expect(fs.readFileSync(path.join(abs(m), 'inner.txt'), 'utf8')).toBe('inner\n');
      expect(parityFiles()).toEqual(before);
    } finally {
      clean();
    }
    for (const x of [m, A]) expect(() => fs.lstatSync(abs(x))).toThrow(/ENOENT/);
  });
});
