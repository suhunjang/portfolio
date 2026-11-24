// step 9 — 합성 저장소에서 inline C와 runCheck의 정상·변경 parity (i)~(v), runtime 비노출 검사
// (node 전용, desktop-dark에서만 실행. 코드 추가 없음, 테스트만)
import { test, expect } from '@playwright/test';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import {
  BASE, HARNESS_IDENTITY, STATUS_ARGS, parseStatusZ, computeIdentity, takeCurrent, runCheck,
} from '../scripts/scope-snapshot.mjs';
import { makeSyntheticRepo, designBlock, isolatedGitEnv } from '../helpers/synthetic-repo.js';

const TIMEOUT = 10000;
const STEP = 'parity-1';
const SNAP_REL = 'tests/.tmp/start-snapshot-parity-1.json';
const AFTER_REL = 'tests/.tmp/start-snapshot-parity-1-after.z';
const GITIGNORE = 'tests/.tmp/\n';
const COMMIT = ['-c', 'user.name=t', '-c', 'user.email=t@example.invalid', 'commit', '-q', '-m', 'init'];
const BASE_VERIFY = JSON.stringify(['rev-parse', '--verify', `${BASE}^{commit}`]);

const sha256 = (buf) => createHash('sha256').update(buf).digest('hex');

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

// rev-parse --verify BASE^{commit}만 성공으로 대체, 나머지는 실제 git
function gitWrapper(dir) {
  return (args) => {
    if (JSON.stringify([...args]) === BASE_VERIFY) return Buffer.from(`${BASE}\n`);
    return realGit(dir, [...args]);
  };
}

// 대상 디렉터리 inventory: 상대 경로 → 유형·sha256·mtime (링크를 따라가지 않음, skip 디렉터리 제외)
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
        out[r] = { type: st.isSymbolicLink() ? 'symlink' : 'other', mtime: st.mtimeMs };
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
  write(repo.outside, 'keep.txt', `outside-${process.pid}\n`);
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

const lines = (s) => s.split('\n').filter((l) => l !== '');

// 같은 합성 상태에서 C와 runCheck를 각각 실행해 code·위반 줄·after.z 비교
function runBoth(repo, { allow = '', absent = '' } = {}) {
  const { dir } = repo;
  const afterAbs = path.join(dir, AFTER_REL);
  const snapBytes = fs.readFileSync(path.join(dir, SNAP_REL));

  fs.rmSync(afterAbs, { force: true });
  const c = spawnSync('python3', ['-I', '-', STEP, allow, absent], {
    cwd: dir, input: designBlock('inline 범위 검사 C'), env: isolatedGitEnv(), encoding: 'utf8', timeout: TIMEOUT,
  });
  expect(c.error, 'C subprocess error/timeout').toBeUndefined();
  expect(fs.lstatSync(afterAbs).isFile()).toBe(true);
  expectRuntimeHidden(dir);
  const cAfter = fs.readFileSync(afterAbs);

  fs.rmSync(afterAbs, { force: true });
  const split = (s) => s.split(',').filter((p) => p !== '');
  const js = runCheck({ startFile: SNAP_REL, allow: split(allow), requireAbsent: split(absent) },
    { git: gitWrapper(dir), root: dir });
  expect(fs.lstatSync(afterAbs).isFile()).toBe(true);
  expectRuntimeHidden(dir);
  const jsAfter = fs.readFileSync(afterAbs);

  expect(fs.readFileSync(path.join(dir, SNAP_REL)).equals(snapBytes)).toBe(true);
  const cRes = { code: c.status, out: lines(c.stdout), bad: lines(c.stderr) };
  const jsRes = { code: js.code, out: lines(js.stdout), bad: lines(js.stderr) };
  expect(jsRes.code).toBe(cRes.code);
  expect(jsRes.bad).toEqual(cRes.bad);
  expect(jsRes.out).toEqual(cRes.out);
  expect(jsAfter.equals(cAfter)).toBe(true);
  expect(cAfter.equals(realGit(dir, [...STATUS_ARGS]))).toBe(true);
  return cRes;
}

// 사례 공통: 새 합성 저장소, 실행 전후 대상(저장소 비runtime·외부) inventory 불변, finally cleanup
function withCase(setup, check) {
  const repo = makeSyntheticRepo();
  try {
    prepareRepo(repo);
    setup(repo);
    const skip = ['.git', 'tests/.tmp'];
    const before = { repo: inventory(repo.dir, skip), outside: inventory(repo.outside) };
    check(repo);
    expect(inventory(repo.dir, skip)).toEqual(before.repo);
    expect(inventory(repo.outside)).toEqual(before.outside);
  } finally {
    repo.cleanup();
  }
  expect(fs.existsSync(repo.dir)).toBe(false);
  expect(fs.existsSync(repo.outside)).toBe(false);
}

test.describe('step 9 scope-snapshot parity core', () => {
  test.beforeEach(({}, testInfo) => {
    test.skip(testInfo.project.name !== 'desktop-dark', 'node 전용 검사는 desktop-dark에서만 실행');
  });

  test('(i) 변경 없음 → 둘 다 code 0·scope-snapshot: OK', () => {
    withCase((repo) => makeStartSnapshot(repo), (repo) => {
      const r = runBoth(repo);
      expect(r.code).toBe(0);
      expect(r.out).toEqual(['scope-snapshot: OK']);
      expect(r.bad).toEqual([]);
    });
  });

  test('(ii) tracked.txt 수정(allow 밖) → outside-tests:tracked.txt', () => {
    withCase((repo) => {
      makeStartSnapshot(repo);
      write(repo.dir, 'tracked.txt', 'changed\n');
    }, (repo) => {
      const r = runBoth(repo, { allow: 'tests/specs/a.spec.js' });
      expect(r.code).toBe(1);
      expect(r.bad).toEqual(['outside-tests:tracked.txt']);
    });
  });

  test('(iii) 새 tests/specs/x.spec.js(allow 밖) → tests-changed:tests/specs/x.spec.js', () => {
    withCase((repo) => {
      makeStartSnapshot(repo);
      write(repo.dir, 'tests/specs/x.spec.js', 'x\n');
    }, (repo) => {
      const r = runBoth(repo);
      expect(r.code).toBe(1);
      expect(r.bad).toEqual(['tests-changed:tests/specs/x.spec.js']);
    });
  });

  test('(iv) --require-absent tracked.txt → snapshot-not-first:tracked.txt', () => {
    withCase((repo) => makeStartSnapshot(repo), (repo) => {
      const r = runBoth(repo, { absent: 'tracked.txt' });
      expect(r.code).toBe(1);
      expect(r.bad).toEqual(['snapshot-not-first:tracked.txt']);
    });
  });

  test('(v) stage만 바뀜 → status-changed:tracked.txt', () => {
    let start;
    withCase((repo) => {
      write(repo.dir, 'tracked.txt', 'modified\n');
      start = makeStartSnapshot(repo);
      repo.git(['add', 'tracked.txt']);
    }, (repo) => {
      const cur = takeCurrent(null, { git: gitWrapper(repo.dir), root: repo.dir });
      expect(start.xy['tracked.txt']).toBe(' M');
      expect(cur.xy['tracked.txt']).toBe('M ');
      expect(cur.files['tracked.txt']).toBe(start.files['tracked.txt']);
      expect(cur.files['tracked.txt']).toBe(sha256('modified\n'));
      const r = runBoth(repo);
      expect(r.code).toBe(1);
      expect(r.bad).toEqual(['status-changed:tracked.txt']);
    });
  });
});
