// step 10 — 저장소 상대 경로 계약 위반 parity (vi): inline C·runCheck·CLI 모두 외부 파일 접근 없이 exit 1
// (node 전용, desktop-dark에서만 실행. 코드 추가 없음, 테스트만)
import { test, expect } from '@playwright/test';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import {
  BASE, HARNESS_IDENTITY, STATUS_ARGS, parseStatusZ, computeIdentity, takeCurrent, writeAfterZ, runCheck,
} from '../scripts/scope-snapshot.mjs';
import {
  makeSyntheticRepo, designBlock, isolatedGitEnv, runHarness, TESTS_DIR,
} from '../helpers/synthetic-repo.js';

const TIMEOUT = 10000;
const STEP = 'parity-1';
const SNAP_REL = 'tests/.tmp/start-snapshot-parity-1.json';
const AFTER_REL = 'tests/.tmp/start-snapshot-parity-1-after.z';
const GITIGNORE = 'tests/.tmp/\n';
const COMMIT = ['-c', 'user.name=t', '-c', 'user.email=t@example.invalid', 'commit', '-q', '-m', 'init'];
const BASE_VERIFY = JSON.stringify(['rev-parse', '--verify', `${BASE}^{commit}`]);
const EXPECTED = `bad start snapshot: paths: ${SNAP_REL}`;
const AFTER_BYTES = Buffer.from('fixed-after-z\0bytes\n');
const CLI = path.join(TESTS_DIR, 'scripts/scope-snapshot.mjs');

const sha256 = (buf) => createHash('sha256').update(buf).digest('hex');
const lines = (s) => s.split('\n').filter((l) => l !== '');

function write(dir, rel, data) {
  fs.mkdirSync(path.dirname(path.join(dir, rel)), { recursive: true });
  fs.writeFileSync(path.join(dir, rel), data);
}

// 합성 저장소 읽기 전용 git (부모 GIT_* 제거, timeout 10초)
function realGit(dir, args) {
  const r = spawnSync('git', ['-C', dir, ...args], { env: isolatedGitEnv(), timeout: TIMEOUT, maxBuffer: 64 * 1024 * 1024 });
  if (r.error) throw r.error;
  if (r.status !== 0) throw new Error(`git ${args.join(' ')} failed: ${r.stderr}`);
  return r.stdout;
}

// rev-parse --verify BASE^{commit}만 성공으로 대체, 나머지는 실제 git (호출 기록)
function gitWrapper(dir, calls = []) {
  return (args) => {
    calls.push([...args]);
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

// 외부 경로 판정: secret.txt 또는 <pid>-outside를 포함하는 대상
function isOutside(repo, target) {
  const s = String(target);
  return s.includes('secret.txt') || s.includes(`${process.pid}-outside`) || s.includes(repo.outside);
}

// 변형 하나: 새 합성 저장소 → 정상 snapshot → files에 key 하나 추가 → C·runCheck·CLI 실행·비교
function runVariant(makeKey) {
  const repo = makeSyntheticRepo();
  const sentinel = `SENTINEL-step10-${process.pid}-${Date.now()}-${Math.random().toString(36).slice(2)}`;
  try {
    prepareRepo(repo);
    const { dir } = repo;
    const secret = path.join(repo.outside, 'secret.txt');
    fs.writeFileSync(secret, `${sentinel}\n`);

    const snap = makeStartSnapshot(repo);
    const key = makeKey(repo);
    expect(Object.hasOwn(snap.files, key)).toBe(false);
    const bad = JSON.parse(fs.readFileSync(path.join(dir, SNAP_REL), 'utf8'));
    for (const f of ['projectRoot', 'head', 'base', 'harness', 'stepId']) expect(bad[f]).toEqual(snap[f]);
    bad.files[key] = null;
    write(dir, SNAP_REL, `${JSON.stringify(bad, null, 1)}\n`);
    write(dir, AFTER_REL, AFTER_BYTES);
    expectRuntimeHidden(dir);

    const targets = { snap: path.join(dir, SNAP_REL), after: path.join(dir, AFTER_REL), secret };
    const before = Object.fromEntries(Object.entries(targets).map(([k, p]) => [k, stamp(p)]));
    expect(before.after.sha256).toBe(sha256(AFTER_BYTES));
    const outputs = [];

    // --- C: exec harness (기록된 lstat·open·walk 대상, git 호출) ---
    const body = designBlock('inline 범위 검사 C');
    const h = runHarness(body, { cwd: dir, toplevel: dir, argv: [STEP, '', ''] });
    outputs.push(JSON.stringify(h));
    expect(h.error).toBeNull();
    expect(h.exit).toBe(EXPECTED);
    for (const [name, args] of h.calls) {
      if (['os.lstat', 'os.open', 'open', 'os.walk'].includes(name)) {
        for (const a of args) expect(isOutside(repo, a), `${name} ${a}`).toBe(false);
      }
    }
    const osOpens = h.calls.filter(([n]) => n === 'os.open');
    expect(osOpens.length).toBe(1);
    expect(path.resolve(dir, osOpens[0][1][0])).toBe(targets.snap);
    expect(h.calls.filter(([n]) => n === 'git-other')).toEqual([]);
    expect(h.calls.filter(([n]) => n.startsWith('git-')).every(([n]) => n === 'git-toplevel')).toBe(true);

    // --- C: subprocess ---
    const c = spawnSync('python3', ['-I', '-', STEP, '', ''], {
      cwd: dir, input: body, env: isolatedGitEnv(), encoding: 'utf8', timeout: TIMEOUT,
    });
    expect(c.error, 'C subprocess error/timeout').toBeUndefined();
    outputs.push(c.stdout, c.stderr);
    expect(c.status).toBe(1);
    expect(lines(c.stderr)).toEqual([EXPECTED]);
    expect(c.stdout).toBe('');

    // --- runCheck: 기록 fs·spy deps ---
    const rec = recordingFs();
    const called = [];
    const spy = (name, fn) => (...a) => { called.push(name); return fn(...a); };
    const gitCalls = [];
    const js = runCheck({ startFile: SNAP_REL, allow: [] }, {
      git: gitWrapper(dir, gitCalls),
      fs: rec.fake,
      root: dir,
      deps: {
        computeIdentity: spy('computeIdentity', computeIdentity),
        takeCurrent: spy('takeCurrent', takeCurrent),
        writeAfterZ: spy('writeAfterZ', writeAfterZ),
      },
    });
    outputs.push(js.stdout, js.stderr);
    expect(js.code).toBe(1);
    expect(js.stderr).toBe(EXPECTED);
    expect(called).toEqual([]);
    expect(gitCalls).toEqual([]);
    const watched = ['lstatSync', 'statSync', 'openSync', 'readFileSync', 'readSync', 'readlinkSync', 'realpathSync'];
    for (const [name, a] of rec.calls) {
      if (watched.includes(name)) expect(isOutside(repo, a), `${name} ${a}`).toBe(false);
    }
    expect(rec.calls.some(([n]) => ['writeSync', 'writeFileSync', 'mkdirSync'].includes(n))).toBe(false);

    // --- CLI subprocess ---
    const cli = spawnSync(process.execPath, [CLI, '--check', SNAP_REL, '--allow', ''], {
      cwd: dir, env: isolatedGitEnv(), encoding: 'utf8', timeout: TIMEOUT,
    });
    expect(cli.error, 'CLI subprocess error/timeout').toBeUndefined();
    outputs.push(cli.stdout, cli.stderr);
    expect(cli.status).toBe(1);
    expect(lines(cli.stderr)).toEqual([EXPECTED]);

    // --- parity·불변 ---
    expect(js.code).toBe(c.status);
    expect(cli.status).toBe(c.status);
    expect(lines(js.stderr)).toEqual(lines(c.stderr));
    expect(lines(cli.stderr)).toEqual(lines(c.stderr));
    for (const [k, p] of Object.entries(targets)) expect(stamp(p), k).toEqual(before[k]);
    for (const o of outputs) expect(o.includes(sentinel)).toBe(false);
    expectRuntimeHidden(dir);
  } finally {
    repo.cleanup();
  }
  expect(fs.existsSync(repo.dir)).toBe(false);
  expect(fs.existsSync(repo.outside)).toBe(false);
}

test.describe('step 10 scope-snapshot parity paths (vi)', () => {
  test.beforeEach(({}, testInfo) => {
    test.skip(testInfo.project.name !== 'desktop-dark', 'node 전용 검사는 desktop-dark에서만 실행');
  });

  test('(vi-A) files key ../<pid>-outside/secret.txt → C·runCheck·CLI bad start snapshot: paths', () => {
    runVariant(() => `../${process.pid}-outside/secret.txt`);
  });

  test('(vi-B) files key 외부 secret.txt 절대 경로 → C·runCheck·CLI bad start snapshot: paths', () => {
    runVariant((repo) => {
      const abs = path.resolve(repo.outside, 'secret.txt');
      expect(path.isAbsolute(abs)).toBe(true);
      return abs;
    });
  });
});
