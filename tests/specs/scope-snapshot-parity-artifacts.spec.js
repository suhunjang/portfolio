// step 11 — 기록 대상 unsafe 시 after.z 보존(C·runCheck 4조합), CLI tests/.tmp 조상 링크 거부,
// 실제 저장소 after.z FIFO·identity 변형 거부 (node 전용, desktop-dark에서만 실행. 코드 추가 없음, 테스트만)
import { test, expect } from '@playwright/test';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import {
  BASE, HARNESS_IDENTITY, STATUS_ARGS, parseStatusZ, computeIdentity, takeCurrent, runCheck,
} from '../scripts/scope-snapshot.mjs';
import {
  makeSyntheticRepo, designBlock, isolatedGitEnv, REPO_ROOT, TESTS_DIR,
} from '../helpers/synthetic-repo.js';

const TIMEOUT = 10000;
const STEP = 'parity-1';
const SNAP_REL = 'tests/.tmp/start-snapshot-parity-1.json';
const AFTER_REL = 'tests/.tmp/start-snapshot-parity-1-after.z';
const GITIGNORE = 'tests/.tmp/\n';
const COMMIT = ['-c', 'user.name=t', '-c', 'user.email=t@example.invalid', 'commit', '-q', '-m', 'init'];
const BASE_VERIFY = JSON.stringify(['rev-parse', '--verify', `${BASE}^{commit}`]);
const AFTER_BYTES = Buffer.from('fixed-after-z\0step11\n');
const CLI = path.join(TESTS_DIR, 'scripts/scope-snapshot.mjs');

const sha256 = (buf) => createHash('sha256').update(buf).digest('hex');
const lines = (s) => s.split('\n').filter((l) => l !== '');

function write(dir, rel, data) {
  fs.mkdirSync(path.dirname(path.join(dir, rel)), { recursive: true });
  fs.writeFileSync(path.join(dir, rel), data);
}

function mkfifo(abs) {
  fs.mkdirSync(path.dirname(abs), { recursive: true });
  const r = spawnSync('python3', ['-I', '-c', 'import os, sys; os.mkfifo(sys.argv[1])', abs], { timeout: TIMEOUT });
  expect(r.error, 'mkfifo error/timeout').toBeUndefined();
  expect(r.status, String(r.stderr)).toBe(0);
  expect(fs.lstatSync(abs).isFIFO()).toBe(true);
}

// 읽기 전용 git (부모 GIT_* 제거, timeout 10초)
function realGit(dir, args) {
  const r = spawnSync('git', ['-C', dir, ...args], { env: isolatedGitEnv(), timeout: TIMEOUT, maxBuffer: 64 * 1024 * 1024 });
  if (r.error) throw r.error;
  if (r.status !== 0) throw new Error(`git ${args.join(' ')} failed: ${r.stderr}`);
  return r.stdout;
}

// rev-parse --verify BASE^{commit}만 성공으로 대체, 나머지는 실제 git
function gitWrapper(dir) {
  return (args) => {
    if (JSON.stringify([...args]) === BASE_VERIFY) return Buffer.from(`${BASE}\n`);
    return realGit(dir, [...args]);
  };
}

// 실제 fs를 감싸 호출(이름, 경로 또는 fd)을 기록한다
function recordingFs() {
  const calls = [];
  const wrap = (name) => (...args) => {
    calls.push([name, typeof args[0] === 'number' ? args[0] : String(args[0])]);
    return fs[name](...args);
  };
  const names = ['lstatSync', 'readdirSync', 'openSync', 'fstatSync', 'readFileSync', 'readSync', 'closeSync',
    'statSync', 'readlinkSync', 'realpathSync', 'existsSync', 'opendirSync', 'accessSync', 'writeSync',
    'writeFileSync', 'mkdirSync'];
  const fake = { constants: fs.constants };
  for (const n of names) fake[n] = wrap(n);
  return { fake, calls };
}

// 대상 디렉터리 inventory: 상대 경로 → 유형·sha256·mtime (링크를 따라가지 않음, FIFO는 열지 않음)
function inventory(root, skip = []) {
  const out = {};
  const walk = (rel) => {
    for (const ent of fs.readdirSync(path.join(root, rel), { withFileTypes: true })) {
      const r = rel ? `${rel}/${ent.name}` : ent.name;
      if (skip.includes(r)) continue;
      const st = fs.lstatSync(path.join(root, r));
      if (st.isDirectory()) {
        out[r] = { type: 'dir', mtime: st.mtimeMs };
        walk(r);
      } else if (st.isFile()) {
        out[r] = { type: 'file', sha256: sha256(fs.readFileSync(path.join(root, r))), mtime: st.mtimeMs };
      } else {
        out[r] = { type: st.isSymbolicLink() ? 'symlink' : st.isFIFO() ? 'fifo' : 'other', mtime: st.mtimeMs };
      }
    }
  };
  walk('');
  return out;
}

// status에 snapshot·after.z가 path·origPath 어디에도 없음
function expectRuntimeHidden(dir) {
  const entries = parseStatusZ(realGit(dir, [...STATUS_ARGS]));
  for (const e of entries) {
    for (const p of [SNAP_REL, AFTER_REL]) {
      expect(e.path, JSON.stringify(e)).not.toBe(p);
      expect(e.origPath ?? null, JSON.stringify(e)).not.toBe(p);
    }
  }
}

// 초기 commit: .gitignore(정확히 tests/.tmp/ 한 줄)·lock(identity 3값)·tracked.txt·tests/specs/a.spec.js
function prepareRepo(repo) {
  repo.git(['init', '-q']);
  fs.writeFileSync(path.join(repo.dir, '.gitignore'), GITIGNORE);
  write(repo.dir, '.harness/harness.lock.json', `${JSON.stringify(HARNESS_IDENTITY, null, 2)}\n`);
  write(repo.dir, 'tracked.txt', 'tracked\n');
  write(repo.dir, 'tests/specs/a.spec.js', 'a\n');
  repo.git(['add', '-A']);
  repo.git(COMMIT);
  expect(fs.readFileSync(path.join(repo.dir, '.gitignore'), 'utf8')).toBe(GITIGNORE);
  expect(realGit(repo.dir, ['show', 'HEAD:.gitignore']).toString('utf8')).toBe(GITIGNORE);
}

// computeIdentity·takeCurrent로 정상 시작 snapshot 작성 후 runtime 비노출 확인
function makeStartSnapshot(repo) {
  const git = gitWrapper(repo.dir);
  const ident = computeIdentity({ git, root: repo.dir });
  const status = realGit(repo.dir, [...STATUS_ARGS]);
  const cur = takeCurrent(null, { git, root: repo.dir });
  expect(cur.unsafe).toEqual([]);
  const snap = {
    base: ident.base,
    files: cur.files,
    harness: ident.harness,
    head: ident.head,
    projectRoot: ident.projectRoot,
    schemaVersion: 1,
    statusZHex: Buffer.from(status).toString('hex'),
    stepId: STEP,
    xy: cur.xy,
  };
  write(repo.dir, SNAP_REL, `${JSON.stringify(snap, null, 1)}\n`);
  expectRuntimeHidden(repo.dir);
  return snap;
}

const stamp = (p) => {
  const st = fs.lstatSync(p);
  return { file: st.isFile(), sha256: sha256(fs.readFileSync(p)), mtime: st.mtimeMs };
};

// 합성 사례: 새 저장소·정상 snapshot·외부 sentinel, 전후 저장소(.git 제외)·외부 inventory 불변, finally cleanup
function withRepo(fn) {
  const repo = makeSyntheticRepo();
  const sentinel = `SENTINEL-step11-${process.pid}-${Date.now()}-${Math.random().toString(36).slice(2)}`;
  try {
    prepareRepo(repo);
    const secret = path.join(repo.outside, 'secret.txt');
    fs.writeFileSync(secret, `${sentinel}\n`);
    makeStartSnapshot(repo);
    fn(repo, { sentinel, secret });
  } finally {
    repo.cleanup();
  }
  expect(fs.existsSync(repo.dir)).toBe(false);
  expect(fs.existsSync(repo.outside)).toBe(false);
}

// 기록 대상 unsafe 사례: after.z 있음/없음 × FIFO/symlink → runCheck·C 모두 code 1, after.z 보존·미생성
function runPreserveCase({ hasAfter, kind }) {
  withRepo((repo, { sentinel, secret }) => {
    const { dir } = repo;
    const snapAbs = path.join(dir, SNAP_REL);
    const afterAbs = path.join(dir, AFTER_REL);
    if (hasAfter) write(dir, AFTER_REL, AFTER_BYTES);
    const afterBefore = hasAfter ? stamp(afterAbs) : null;
    if (hasAfter) expect(afterBefore.sha256).toBe(sha256(AFTER_BYTES));
    else expect(fs.existsSync(afterAbs)).toBe(false);

    let rel;
    if (kind === 'fifo') {
      rel = 'tests/specs/p.fifo';
      mkfifo(path.join(dir, rel));
    } else {
      rel = 'link-x';
      fs.symlinkSync(secret, path.join(dir, rel));
      expect(fs.lstatSync(path.join(dir, rel)).isSymbolicLink()).toBe(true);
    }
    const item = `${kind === 'fifo' ? 'non-regular:' : 'symlink:'}${rel}`;
    expectRuntimeHidden(dir);

    const snapBefore = stamp(snapAbs);
    const before = { repo: inventory(dir, ['.git']), outside: inventory(repo.outside) };
    const outputs = [];
    const expectPreserved = () => {
      if (hasAfter) expect(stamp(afterAbs)).toEqual(afterBefore);
      else expect(fs.existsSync(afterAbs)).toBe(false);
      expect(stamp(snapAbs)).toEqual(snapBefore);
      expect(inventory(dir, ['.git'])).toEqual(before.repo);
      expect(inventory(repo.outside)).toEqual(before.outside);
    };

    // --- runCheck: 기록 fs, after.z open 없음 ---
    const rec = recordingFs();
    const js = runCheck({ startFile: SNAP_REL, allow: [rel] }, { git: gitWrapper(dir), fs: rec.fake, root: dir });
    outputs.push(js.stdout, js.stderr);
    expect(js.code).toBe(1);
    expect(lines(js.stderr)).toEqual([item]);
    expect(js.stdout).toBe('');
    expect(rec.calls.filter(([n, p]) => n === 'openSync' && p === afterAbs)).toEqual([]);
    expect(rec.calls.some(([n]) => ['writeSync', 'writeFileSync', 'mkdirSync'].includes(n))).toBe(false);
    expectPreserved();

    // --- C: subprocess (멈추지 않음) ---
    const c = spawnSync('python3', ['-I', '-', STEP, rel, ''], {
      cwd: dir, input: designBlock('inline 범위 검사 C'), env: isolatedGitEnv(), encoding: 'utf8', timeout: TIMEOUT,
    });
    expect(c.error, 'C subprocess error/timeout').toBeUndefined();
    outputs.push(c.stdout, c.stderr);
    expect(c.status).toBe(1);
    expect(lines(c.stderr)).toEqual([item]);
    expect(c.stdout).not.toContain('scope-snapshot: OK');
    expectPreserved();

    expect(lines(js.stderr)).toEqual(lines(c.stderr));
    for (const o of outputs) expect(o.includes(sentinel)).toBe(false);
  });
}

// 실제 저장소 상태: status 원문과 git ls-files의 tests 밖 파일 sha256
function realRepoState() {
  const status = realGit(REPO_ROOT, [...STATUS_ARGS]);
  const listed = realGit(REPO_ROOT, ['ls-files', '-z']).toString('utf8').split('\0')
    .filter((p) => p && !p.startsWith('tests/'));
  const files = {};
  for (const p of listed) {
    const abs = path.join(REPO_ROOT, p);
    const st = fs.lstatSync(abs, { throwIfNoEntry: false });
    files[p] = st && st.isFile() ? sha256(fs.readFileSync(abs)) : (st ? 'non-file' : null);
  }
  return { status: status.toString('hex'), files };
}

const realCli = (rel) => spawnSync(process.execPath, ['tests/scripts/scope-snapshot.mjs', '--check', rel, '--allow', ''], {
  cwd: REPO_ROOT, env: isolatedGitEnv(), encoding: 'utf8', timeout: TIMEOUT,
});

test.describe('step 11 scope-snapshot parity artifacts', () => {
  test.beforeEach(({}, testInfo) => {
    test.skip(testInfo.project.name !== 'desktop-dark', 'node 전용 검사는 desktop-dark에서만 실행');
  });

  for (const hasAfter of [true, false]) {
    for (const kind of ['fifo', 'symlink']) {
      test(`기록 대상 ${kind === 'fifo' ? 'FIFO tests/specs/p.fifo' : 'symlink link-x'} × 기존 after.z ${hasAfter ? '있음' : '없음'} → runCheck·C code 1, after.z ${hasAfter ? '보존' : '미생성'}`, () => {
        runPreserveCase({ hasAfter, kind });
      });
    }
  }

  test('CLI: tests/.tmp → <outside>/tmpdir 링크 → unsafe path: symlink:tests/.tmp, 외부 불변·sentinel 미출력', () => {
    withRepo((repo, { sentinel }) => {
      const { dir } = repo;
      const tmpdir = path.join(repo.outside, 'tmpdir');
      fs.mkdirSync(tmpdir, { recursive: true });
      fs.copyFileSync(path.join(dir, SNAP_REL), path.join(tmpdir, 'start-snapshot-parity-1.json'));
      fs.writeFileSync(path.join(tmpdir, 'secret.txt'), `${sentinel}\n`);
      fs.rmSync(path.join(dir, 'tests/.tmp'), { recursive: true, force: true });
      fs.symlinkSync(tmpdir, path.join(dir, 'tests/.tmp'));
      expect(fs.lstatSync(path.join(dir, 'tests/.tmp')).isSymbolicLink()).toBe(true);

      const before = { repo: inventory(dir, ['.git']), outside: inventory(repo.outside) };
      const cli = spawnSync(process.execPath, [CLI, '--check', SNAP_REL, '--allow', ''], {
        cwd: dir, env: isolatedGitEnv(), encoding: 'utf8', timeout: TIMEOUT,
      });
      expect(cli.error, 'CLI subprocess error/timeout').toBeUndefined();
      expect(cli.status).toBe(1);
      expect(lines(cli.stderr)).toEqual(['unsafe path: symlink:tests/.tmp']);
      expect(cli.stdout).toBe('');
      expect(cli.stdout + cli.stderr).not.toContain(sentinel);
      expect(fs.existsSync(path.join(tmpdir, 'start-snapshot-parity-1-after.z'))).toBe(false);
      expect(inventory(dir, ['.git'])).toEqual(before.repo);
      expect(inventory(repo.outside)).toEqual(before.outside);
    });
  });

  test('CLI 실제 저장소: after.z FIFO → non-regular:…-after.z, FIFO 유지', () => {
    const id = `parity-${process.pid * 1000 + 701}`;
    const rel = `tests/.tmp/start-snapshot-${id}.json`;
    const afterRel = rel.replace(/\.json$/, '-after.z');
    const abs = (p) => path.join(REPO_ROOT, p);
    const tmp = abs('tests/.tmp');
    const cleanup = () => { for (const p of [rel, afterRel]) fs.rmSync(abs(p), { force: true }); };
    cleanup();
    try {
      const s = spawnSync('python3', ['-I', 'tests/scripts/start-snapshot.py', id], { cwd: REPO_ROOT, encoding: 'utf8', timeout: TIMEOUT });
      expect(s.error).toBeUndefined();
      expect(s.status, s.stderr).toBe(0);
      expect(s.stdout.trim()).toBe(`start-snapshot: created ${rel}`);
      mkfifo(abs(afterRel));
      const snapSha = sha256(fs.readFileSync(abs(rel)));
      const before = inventory(tmp, ['synthetic-repos']);

      const r = realCli(rel);
      expect(r.error, 'CLI subprocess error/timeout').toBeUndefined();
      expect(r.status).toBe(1);
      expect(lines(r.stderr)).toEqual([`unsafe path: non-regular:${afterRel}`]);
      expect(r.stdout).toBe('');
      expect(fs.lstatSync(abs(afterRel)).isFIFO()).toBe(true);
      expect(sha256(fs.readFileSync(abs(rel)))).toBe(snapSha);
      expect(inventory(tmp, ['synthetic-repos'])).toEqual(before);
    } finally {
      cleanup();
    }
    for (const p of [rel, afterRel]) expect(fs.existsSync(abs(p))).toBe(false);
  });

  test('CLI 실제 저장소: identity 7개 변형 → start snapshot identity mismatch: {field}', () => {
    const base = process.pid * 1000 + 710;
    const rel = (n) => `tests/.tmp/start-snapshot-parity-${n}.json`;
    const afterOf = (p) => p.replace(/\.json$/, '-after.z');
    const abs = (p) => path.join(REPO_ROOT, p);
    const tmp = abs('tests/.tmp');
    const variants = [
      ['projectRoot', (o) => { o.projectRoot = '/tmp/other'; }],
      ['head', (o) => { o.head = '0'.repeat(40); }],
      ['base', (o) => { o.base = 'f'.repeat(40); }],
      ['harness.sourceCommit', (o) => { o.harness.sourceCommit = o.harness.sourceCommit === 'a'.repeat(40) ? 'b'.repeat(40) : 'a'.repeat(40); }],
      ['harness.manifestHash', (o) => { o.harness.manifestHash = o.harness.manifestHash === 'a'.repeat(64) ? 'b'.repeat(64) : 'a'.repeat(64); }],
      ['harness.distributionVersion', (o) => { o.harness.distributionVersion = '9.9.9'; }],
      ['harness.lockSha256', (o) => { o.harness.lockSha256 = '0'.repeat(64); }],
    ];
    const ids = [base, ...variants.map((_, k) => base + 1 + k)];
    const all = ids.flatMap((n) => [rel(n), afterOf(rel(n))]);
    const cleanup = () => { for (const p of all) fs.rmSync(abs(p), { force: true }); };
    cleanup();
    try {
      const s = spawnSync('python3', ['-I', 'tests/scripts/start-snapshot.py', `parity-${base}`], { cwd: REPO_ROOT, encoding: 'utf8', timeout: TIMEOUT });
      expect(s.error).toBeUndefined();
      expect(s.status, s.stderr).toBe(0);
      expect(s.stdout.trim()).toBe(`start-snapshot: created ${rel(base)}`);
      const orig = JSON.parse(fs.readFileSync(abs(rel(base)), 'utf8'));
      const origSha = sha256(fs.readFileSync(abs(rel(base))));
      expect(orig.schemaVersion).toBe(1);

      variants.forEach(([field, mutate], k) => {
        const n = base + 1 + k;
        const o = JSON.parse(JSON.stringify(orig));
        o.stepId = `parity-${n}`;
        mutate(o);
        const [top, sub] = field.split('.');
        expect(sub ? o[top][sub] : o[top], field).not.toEqual(sub ? orig[top][sub] : orig[top]);
        fs.writeFileSync(abs(rel(n)), `${JSON.stringify(o, null, 2)}\n`);
        const snapSha = sha256(fs.readFileSync(abs(rel(n))));
        const stateBefore = realRepoState();
        const tmpBefore = inventory(tmp, ['synthetic-repos']);

        const r = realCli(rel(n));
        expect(r.error, `${field}: CLI subprocess error/timeout`).toBeUndefined();
        expect(r.status, field).toBe(1);
        expect(lines(r.stderr), field).toEqual([`start snapshot identity mismatch: ${field}`]);
        expect(r.stdout).toBe('');
        expect(sha256(fs.readFileSync(abs(rel(n)))), field).toBe(snapSha);
        expect(fs.existsSync(abs(afterOf(rel(n)))), field).toBe(false);
        expect(realRepoState(), field).toEqual(stateBefore);
        expect(inventory(tmp, ['synthetic-repos']), field).toEqual(tmpBefore);
        expect(sha256(fs.readFileSync(abs(rel(base))))).toBe(origSha);
      });
    } finally {
      cleanup();
    }
    for (const p of all) expect(fs.existsSync(abs(p))).toBe(false);
  });
});
