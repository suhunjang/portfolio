// step 5 — 비runtime symlink·snapshot 파일 자체 symlink 거부를 S·C·takeCurrent·loader로 실행 검증
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
const CHANGE_LINE = /^(tests-changed|outside-tests|status-changed):/m;
const COMMIT = ['-c', 'user.name=t', '-c', 'user.email=t@example.invalid', 'commit', '-q', '-m', 'init'];

const sha256 = (buf) => createHash('sha256').update(buf).digest('hex');

// 합성 저장소 subprocess: 부모 GIT_* 변수를 지운 환경, timeout 10초
function py(args, { cwd, input } = {}) {
  const r = spawnSync('python3', args, { cwd, input, env: isolatedGitEnv(), encoding: 'utf8', timeout: TIMEOUT });
  expect(r.error, 'python subprocess error/timeout').toBeUndefined();
  return { code: r.status, stdout: r.stdout, stderr: r.stderr };
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

function write(dir, rel, text) {
  fs.mkdirSync(path.dirname(path.join(dir, rel)), { recursive: true });
  fs.writeFileSync(path.join(dir, rel), text);
}

// 저장소 아래 모든 regular file 내용을 이어 붙인다(.git 제외, 링크는 따라가지 않음)
function generatedText(dir) {
  let out = '';
  const walk = (abs) => {
    for (const ent of fs.readdirSync(abs, { withFileTypes: true })) {
      const p = path.join(abs, ent.name);
      if (ent.isDirectory() && !ent.isSymbolicLink()) {
        if (ent.name !== '.git') walk(p);
      } else if (ent.isFile()) {
        out += fs.readFileSync(p, 'utf8');
      }
    }
  };
  walk(dir);
  return out;
}

// 합성 저장소 공통 골격: lock(정확한 S 출력용)·.gitignore(runtime)·추적 파일, outside/secret.txt sentinel
function setup(repo, ignoreExtra = '') {
  const sentinel = `SENTINEL-${process.pid}-${randomBytes(8).toString('hex')}`;
  write(repo.outside, 'secret.txt', `${sentinel}\n`);
  repo.git(['init', '-q']);
  write(repo.dir, '.gitignore', `tests/.tmp/\n${ignoreExtra}`);
  write(repo.dir, '.harness/harness.lock.json', '{}\n');
  write(repo.dir, 'a.txt', 'a\n');
  write(repo.dir, 'b.txt', 'b\n');
  write(repo.dir, 'c.txt', 'c\n');
  write(repo.dir, 'tests/specs/x.spec.js', 'x\n');
  return { sentinel, secret: path.join(repo.outside, 'secret.txt') };
}

// 정상 형식(strict schema) snapshot bytes — S 재사용 분기 대상
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

// 세 실행 경로(JS·S·C)에서 같은 거부를 확인한다
function expectRejectedEverywhere(repo, { item, linkAbs, sentinel, secret }) {
  const { dir, outside } = repo;
  const snapAbs = path.join(dir, SNAP_REL);
  const afterAbs = path.join(dir, AFTER_REL);
  const secretBefore = fs.readFileSync(secret);
  const outputs = [];

  // JS: takeCurrent + 기록용 fs
  const rec = recordingFs();
  const cur = takeCurrent(null, { root: dir, fs: rec.fake, git: gitReader(dir) });
  expect(cur.unsafe).toEqual([item]);
  expect(cur.files).toEqual({});
  outputs.push(JSON.stringify(cur));
  for (const [name, p] of rec.calls) {
    if (typeof p !== 'string') continue;
    if (p === linkAbs) expect(name, `${name} ${p}`).toBe('lstatSync');
    expect(p.startsWith(`${linkAbs}/`), `${name} ${p}`).toBe(false);
    expect(p === outside || p.startsWith(`${outside}/`), `${name} ${p}`).toBe(false);
  }
  const names = rec.calls.map((c) => c[0]);
  for (const n of ['openSync', 'readFileSync', 'statSync', 'readlinkSync', 'realpathSync']) expect(names, n).not.toContain(n);

  // S 생성 분기: snapshot 없음 → 거부, 생성 없음
  fs.rmSync(snapAbs, { force: true });
  const s1 = py(['-I', S_SCRIPT, 'parity-1'], { cwd: dir });
  expect(s1.code).not.toBe(0);
  expect(s1.stderr.trim()).toBe(`unsafe path: ${item}`);
  expect(fs.existsSync(snapAbs)).toBe(false);
  outputs.push(s1.stdout, s1.stderr);

  // S 재사용 분기: 정상 형식 snapshot이 있어도 거부, bytes 불변
  const normal = normalSnapshot(dir);
  write(dir, SNAP_REL, normal);
  const s2 = py(['-I', S_SCRIPT, 'parity-1'], { cwd: dir });
  expect(s2.code).not.toBe(0);
  expect(s2.stderr.trim()).toBe(`unsafe path: ${item}`);
  expect(fs.readFileSync(snapAbs).equals(normal)).toBe(true);
  outputs.push(s2.stdout, s2.stderr);

  // C: 키 집합만 맞춘 start, allow 비움·링크 경로 포함 모두 같은 결과
  const cStart = { schemaVersion: 1, stepId: 'parity-1', projectRoot: '', head: '', base: '', harness: {}, statusZHex: '', xy: {}, files: {} };
  write(dir, SNAP_REL, `${JSON.stringify(cStart)}\n`);
  const cStartBytes = fs.readFileSync(snapAbs);
  const body = designBlock('inline 범위 검사 C');
  const linkRel = item.slice('symlink:'.length);
  for (const allow of ['', linkRel]) {
    const c = py(['-I', '-', 'parity-1', allow, ''], { cwd: dir, input: body });
    expect(c.code, `allow=${allow}`).toBe(1);
    expect(c.stderr.trim().split('\n')).toContain(item);
    expect(c.stderr).not.toMatch(CHANGE_LINE);
    expect(c.stdout).not.toContain('scope-snapshot: OK');
    expect(fs.existsSync(afterAbs)).toBe(false);
    expect(fs.readFileSync(snapAbs).equals(cStartBytes)).toBe(true);
    outputs.push(c.stdout, c.stderr);
  }

  // sentinel: 어떤 출력·생성 파일에도 없음, 외부 대상 불변
  for (const o of outputs) expect(o).not.toContain(sentinel);
  expect(generatedText(dir)).not.toContain(sentinel);
  expect(fs.readFileSync(secret).equals(secretBefore)).toBe(true);
  return outputs;
}

test.describe('step 5 scope-snapshot symlink', () => {
  test.beforeEach(({}, testInfo) => {
    test.skip(testInfo.project.name !== 'desktop-dark', 'node 전용 검사는 desktop-dark에서만 실행');
  });

  test('(a) allow 밖 ignored symlink → symlink:link-ignored', () => {
    const repo = makeSyntheticRepo();
    try {
      const { sentinel, secret } = setup(repo, 'link-ignored\n');
      repo.git(['add', '-A']);
      repo.git(COMMIT);
      const linkAbs = path.join(repo.dir, 'link-ignored');
      fs.symlinkSync(secret, linkAbs);
      expect(fs.lstatSync(linkAbs).isSymbolicLink()).toBe(true);
      expectRejectedEverywhere(repo, { item: 'symlink:link-ignored', linkAbs, sentinel, secret });
    } finally {
      repo.cleanup();
    }
    expect(fs.existsSync(repo.dir)).toBe(false);
    expect(fs.existsSync(repo.outside)).toBe(false);
  });

  test('(b) 이미 수정된 tracked symlink의 target 변경 → symlink:tracked-link (b.txt, c.txt 모두)', () => {
    const repo = makeSyntheticRepo();
    try {
      const { sentinel, secret } = setup(repo);
      const linkAbs = path.join(repo.dir, 'tracked-link');
      fs.symlinkSync('a.txt', linkAbs);
      repo.git(['add', '-A']);
      repo.git(COMMIT);
      const git = gitReader(repo.dir);
      for (const target of ['b.txt', 'c.txt']) {
        fs.rmSync(linkAbs);
        fs.symlinkSync(target, linkAbs);
        const status = git(STATUS_ARGS).toString('utf8');
        expect(status, target).toContain(` M tracked-link${String.fromCharCode(0)}`);
        expectRejectedEverywhere(repo, { item: 'symlink:tracked-link', linkAbs, sentinel, secret });
      }
    } finally {
      repo.cleanup();
    }
    expect(fs.existsSync(repo.dir)).toBe(false);
  });

  test('(c) symlink 디렉터리 docs-link → outside: symlink:docs-link, 내부 미진입', () => {
    const repo = makeSyntheticRepo();
    try {
      const { sentinel, secret } = setup(repo);
      repo.git(['add', '-A']);
      repo.git(COMMIT);
      const linkAbs = path.join(repo.dir, 'docs-link');
      fs.symlinkSync(repo.outside, linkAbs);
      const outputs = expectRejectedEverywhere(repo, { item: 'symlink:docs-link', linkAbs, sentinel, secret });
      for (const o of outputs) expect(o).not.toContain('docs-link/secret.txt');
    } finally {
      repo.cleanup();
    }
    expect(fs.existsSync(repo.dir)).toBe(false);
  });

  test('(d) 대조: 링크 없는 같은 구조에서 JS unsafe [], C symlink 항목 없음', () => {
    const repo = makeSyntheticRepo();
    try {
      const { sentinel } = setup(repo, 'link-ignored\n');
      write(repo.dir, 'tracked-link', 'plain\n');
      write(repo.dir, 'docs-link/readme.md', 'docs\n');
      repo.git(['add', '-A']);
      repo.git(COMMIT);
      write(repo.dir, 'link-ignored', 'ignored\n');
      write(repo.dir, 'tracked-link', 'plain2\n');

      const cur = takeCurrent(null, { root: repo.dir, git: gitReader(repo.dir) });
      expect(cur.unsafe).toEqual([]);
      expect(cur.xy).toEqual({ 'tracked-link': ' M' });
      expect(cur.files['tracked-link']).toBe(sha256('plain2\n'));

      const cStart = { schemaVersion: 1, stepId: 'parity-1', projectRoot: '', head: '', base: '', harness: {}, statusZHex: '', xy: {}, files: {} };
      write(repo.dir, SNAP_REL, `${JSON.stringify(cStart)}\n`);
      const c = py(['-I', '-', 'parity-1', '', ''], { cwd: repo.dir, input: designBlock('inline 범위 검사 C') });
      expect(c.code).toBe(1);
      expect(c.stderr).not.toContain('symlink:');
      expect(c.stderr).not.toContain('unsafe path');
      expect(c.stderr).toMatch(/^outside-tests:tracked-link$/m);
      expect(c.stderr + c.stdout).not.toContain(sentinel);
    } finally {
      repo.cleanup();
    }
    expect(fs.existsSync(repo.dir)).toBe(false);
  });

  test('(e) 실제 저장소 runtime: snapshot 파일 자체 symlink는 S·loader 모두 거부, 사본 불변', () => {
    const n = process.pid * 1000;
    const [A, k, m] = [n + 501, n + 502, n + 503];
    const rel = (x) => `tests/.tmp/start-snapshot-parity-${x}.json`;
    const abs = (x) => path.join(REPO_ROOT, rel(x));
    for (const x of [m, k, A]) fs.rmSync(abs(x), { force: true });
    try {
      const s = spawnSync('python3', ['-I', 'tests/scripts/start-snapshot.py', `parity-${A}`], { cwd: REPO_ROOT, encoding: 'utf8', timeout: TIMEOUT });
      expect(s.error).toBeUndefined();
      expect(s.status, s.stderr).toBe(0);
      expect(s.stdout.trim()).toBe(`start-snapshot: created ${rel(A)}`);
      const origBytes = fs.readFileSync(abs(A));
      fs.writeFileSync(abs(k), origBytes, { flag: 'wx' });
      const copySha = sha256(fs.readFileSync(abs(k)));
      fs.symlinkSync(path.basename(abs(k)), abs(m));
      expect(fs.lstatSync(abs(m)).isSymbolicLink()).toBe(true);

      const r = spawnSync('python3', ['-I', 'tests/scripts/start-snapshot.py', `parity-${m}`], { cwd: REPO_ROOT, encoding: 'utf8', timeout: TIMEOUT });
      expect(r.error).toBeUndefined();
      expect(r.status).not.toBe(0);
      expect(r.stderr.trim()).toBe(`unsafe path: symlink:${rel(m)}`);

      expect(() => loadStartSnapshot(rel(m), { root: REPO_ROOT })).toThrow(`unsafe path: symlink:${rel(m)}`);

      expect(sha256(fs.readFileSync(abs(k)))).toBe(copySha);
      expect(fs.readFileSync(abs(A)).equals(origBytes)).toBe(true);
      expect(fs.lstatSync(abs(m)).isSymbolicLink()).toBe(true);
    } finally {
      fs.rmSync(abs(m), { force: true });
      fs.rmSync(abs(k), { force: true });
      fs.rmSync(abs(A), { force: true });
    }
    for (const x of [m, k, A]) expect(() => fs.lstatSync(abs(x))).toThrow(/ENOENT/);
  });
});
