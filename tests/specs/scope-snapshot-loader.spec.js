// step 3 — loadStartSnapshot strict schema loader와 S 재사용 분기 parity (node 전용, desktop-dark에서만 실행)
import { test, expect } from '@playwright/test';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadStartSnapshot, UnsafePathError, SKIP_PREFIXES } from '../scripts/scope-snapshot.mjs';

const TESTS_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const REPO_ROOT = path.resolve(TESTS_DIR, '..');
const S_SCRIPT = 'tests/scripts/start-snapshot.py';
const NUL = String.fromCharCode(0);

const sha256 = (buf) => createHash('sha256').update(buf).digest('hex');
const snapRel = (id) => `tests/.tmp/start-snapshot-${id}.json`;
const absOf = (rel) => path.join(REPO_ROOT, rel);

// 실제 저장소에 만드는 parity 파일은 모두 runtime 경로(tests/.tmp)이고, 테스트가 끝나면 지운다.
let counter = 0;
const created = new Set();
function nextId() {
  counter += 1;
  return `parity-${process.pid * 1000 + counter}`;
}
function cleanup() {
  for (const p of created) fs.rmSync(p, { force: true });
  created.clear();
}

function runS(id) {
  const r = spawnSync('python3', ['-I', S_SCRIPT, id], { cwd: REPO_ROOT, encoding: 'utf8', timeout: 10000 });
  expect(r.error, 'S subprocess error/timeout').toBeUndefined();
  return { code: r.status, stdout: r.stdout, stderr: r.stderr.trim() };
}

// S 생성 분기로 정상 parity-<A>를 만들고 원문 텍스트를 돌려준다
function makeOriginal() {
  const id = nextId();
  const rel = snapRel(id);
  expect(fs.existsSync(absOf(rel))).toBe(false);
  created.add(absOf(rel));
  const r = runS(id);
  expect(r.code, r.stderr).toBe(0);
  expect(r.stdout.trim()).toBe(`start-snapshot: created ${rel}`);
  return { id, text: fs.readFileSync(absOf(rel), 'utf8') };
}

// 원문 텍스트의 stepId만 새 이름으로 바꾸고 mutate(text)를 적용한 parity-<n> 파일을 쓴다
function writeVariant(orig, mutate = (t) => t) {
  const id = nextId();
  const rel = snapRel(id);
  const renamed = orig.text.replace(`"stepId": "${orig.id}"`, `"stepId": "${id}"`);
  expect(renamed).not.toBe(orig.text);
  const bytes = Buffer.from(mutate(renamed), 'utf8');
  expect(fs.existsSync(absOf(rel))).toBe(false);
  created.add(absOf(rel));
  fs.writeFileSync(absOf(rel), bytes, { flag: 'wx' });
  return { id, rel, sha: sha256(bytes) };
}

// 객체 단위 변형 (JSON 재직렬화). placeholder 문자열을 원문 token으로 치환할 수 있다.
const viaObject = (fn, replace = []) => (t) => {
  const o = JSON.parse(t);
  fn(o);
  let out = JSON.stringify(o, null, 1);
  for (const [from, to] of replace) out = out.replace(from, to);
  return out;
};
const svLine = '"schemaVersion": 1,';
const swapSv = (to) => (t) => {
  expect(t).toContain(svLine);
  return t.replace(svLine, to);
};

function loaderError(rel, opts = {}) {
  try {
    loadStartSnapshot(rel, { root: REPO_ROOT, ...opts });
  } catch (e) {
    return e;
  }
  return null;
}

// 같은 파일에 S 재사용 분기와 loader를 실행해 둘 다 같은 메시지로 거부하고 파일이 바뀌지 않는지 본다
function expectParityReject(v, category) {
  const s = runS(v.id);
  expect(s.code, `S ${category}`).not.toBe(0);
  expect(s.stdout).not.toContain('reused');
  expect(s.stderr).toBe(`bad start snapshot: ${category}: ${v.rel}`);
  const e = loaderError(v.rel);
  expect(e, `loader ${category}`).not.toBeNull();
  expect(e.message).toBe(s.stderr);
  expect(sha256(fs.readFileSync(absOf(v.rel)))).toBe(v.sha);
}

function fakeStats(kind) {
  return {
    isFile: () => kind === 'file',
    isDirectory: () => kind === 'dir',
    isSymbolicLink: () => kind === 'symlink',
    isFIFO: () => false,
    isSocket: () => false,
    isBlockDevice: () => false,
    isCharacterDevice: () => false,
  };
}
// 가짜 fs: lstatSync만 응답하고 그 밖의 호출은 기록 후 throw
function makeFakeFs(entries) {
  const calls = [];
  const deny = (name) => (...args) => {
    calls.push([name, ...args.map(String)]);
    throw new Error(`${name} not allowed`);
  };
  const fake = {
    constants: fs.constants,
    lstatSync(p) {
      calls.push(['lstatSync', p]);
      if (!(p in entries)) throw Object.assign(new Error(`ENOENT: ${p}`), { code: 'ENOENT' });
      return fakeStats(entries[p]);
    },
    statSync: deny('statSync'),
    openSync: deny('openSync'),
    readFileSync: deny('readFileSync'),
    readlinkSync: deny('readlinkSync'),
    realpathSync: deny('realpathSync'),
    readdirSync: deny('readdirSync'),
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

test.describe('step 3 loadStartSnapshot', () => {
  test.beforeEach(({}, testInfo) => {
    test.skip(testInfo.project.name !== 'desktop-dark', 'node 전용 검사는 desktop-dark에서만 실행');
  });
  test.afterEach(() => cleanup());

  test('projectRoot 유형: symlink·regular file root는 root lstat 1회로 거부', () => {
    const root = '/fake/project';
    for (const [kind, msg] of [['symlink', `unsafe path: symlink:${root}`], ['file', `unsafe path: non-regular:${root}`]]) {
      const { fake, calls } = makeFakeFs({ [root]: kind });
      const e = loaderError(snapRel('step3'), { fs: fake, root });
      expect(e).toBeInstanceOf(UnsafePathError);
      expect(e.message).toBe(msg);
      expect(calls).toEqual([['lstatSync', root]]);
    }
  });

  test('loader: 파일 없음·조상 문제는 open 없이 unsafe path', () => {
    const root = '/fake/project';
    const rel = snapRel('parity-1');
    let { fake, calls } = makeFakeFs({ [root]: 'dir', [`${root}/tests`]: 'dir', [`${root}/tests/.tmp`]: 'dir' });
    let e = loaderError(rel, { fs: fake, root });
    expect(e.message).toBe(`unsafe path: missing:${rel}`);
    expect(calls.every((c) => c[0] === 'lstatSync')).toBe(true);

    ({ fake, calls } = makeFakeFs({ [root]: 'dir', [`${root}/tests`]: 'dir', [`${root}/tests/.tmp`]: 'symlink' }));
    e = loaderError(rel, { fs: fake, root });
    expect(e.message).toBe('unsafe path: symlink:tests/.tmp');
    expect(calls.map((c) => c[1])).toEqual([root, `${root}/tests`, `${root}/tests/.tmp`]);

    ({ fake, calls } = makeFakeFs({ [root]: 'dir', [`${root}/tests`]: 'dir', [`${root}/tests/.tmp`]: 'dir', [`${root}/${rel}`]: 'dir' }));
    e = loaderError(rel, { fs: fake, root });
    expect(e.message).toBe(`unsafe path: non-regular:${rel}`);
    expect(calls.every((c) => c[0] === 'lstatSync')).toBe(true);

    // 실제 저장소: 없는 parity 파일
    const id = nextId();
    expect(loaderError(snapRel(id)).message).toBe(`unsafe path: missing:${snapRel(id)}`);
  });

  test('loader: stepId 형식 오류·파일명 불일치는 throw', () => {
    const orig = makeOriginal();
    const mismatch = writeVariant(orig, viaObject((o) => { o.stepId = 'step3'; }));
    expect(loaderError(mismatch.rel).message).toBe(`bad start snapshot: stepId: ${mismatch.rel}`);
    for (const bad of ['bogus', 'parity-x', 7, null]) {
      const v = writeVariant(orig, viaObject((o) => { o.stepId = bad; }));
      expect(loaderError(v.rel).message, JSON.stringify(bad)).toBe(`bad start snapshot: stepId: ${v.rel}`);
      expect(sha256(fs.readFileSync(absOf(v.rel)))).toBe(v.sha);
    }
  });

  test('S 재사용 분기와 loader가 모든 schema 범주에서 같은 판정', () => {
    const orig = makeOriginal();
    const o0 = JSON.parse(orig.text);
    const fileKeys = Object.keys(o0.files);
    const xyKeys = Object.keys(o0.xy);
    expect(fileKeys.length).toBeGreaterThan(0);
    expect(xyKeys.length).toBeGreaterThan(0);
    const statusPath = xyKeys.find((p) => !SKIP_PREFIXES.some((s) => p.startsWith(s)) && p in o0.files);
    expect(statusPath).toBeTruthy();
    const upper = o0.statusZHex.toUpperCase();
    expect(upper).not.toBe(o0.statusZHex);

    const cases = [
      ['invalid json', (t) => t.slice(0, -5)],
      ['invalid json', viaObject((o) => { o.files[fileKeys[0]] = '__NAN__'; }, [['"__NAN__"', 'NaN']])],
      ['invalid json', swapSv(`${svLine}\n "schemaVersion": 1.0,`)],
      ['invalid json', swapSv(`${svLine}\n "schemaVersion": 1e0,`)],
      ['invalid json', swapSv(`"schemaVersion": 1.0,\n ${svLine}`)],
      ['invalid json', (t) => t.replace('"harness": {', '"harness": {\n  "distributionVersion": "2.0.0",')],
      ['invalid json', (t) => t.replace('"harness": {', '"harness": {\n  "lockSha256": "x",')],
      ['keys', viaObject((o) => { delete o.head; })],
      ['keys', viaObject((o) => { o.extra = 1; })],
      ['schemaVersion', swapSv('"schemaVersion": 2,')],
      ['schemaVersion', swapSv('"schemaVersion": true,')],
      ['schemaVersion', swapSv('"schemaVersion": 1.0,')],
      ['schemaVersion', swapSv('"schemaVersion": 1e0,')],
      ['schemaVersion', swapSv('"schemaVersion": "1",')],
      ['schemaVersion', (t) => swapSv('"schemaVersion": 1.0,')(viaObject((o) => { o.harness.schemaVersion = 1; })(t))],
      ['schemaVersion', (t) => swapSv('"schemaVersion": 1.0,')(viaObject((o) => { o.files.schemaVersion = 1; })(t))],
      ['statusZHex', viaObject((o) => { o.statusZHex = 'zz'; })],
      ['statusZHex', viaObject((o) => { o.statusZHex = '0'; })],
      ['statusZHex', viaObject((o) => { o.statusZHex = upper; })],
      ['status parse', viaObject((o) => { o.statusZHex = '3f3f'; })],
      ['status parse', viaObject((o) => { o.statusZHex = Buffer.from(` M \xff${NUL}`, 'latin1').toString('hex'); })],
      ['xy', viaObject((o) => { o.xy['zz-extra-path.txt'] = ' M'; })],
      ['xy', viaObject((o) => { o.xy[xyKeys[0]] = o.xy[xyKeys[0]] === ' M' ? 'MM' : ' M'; })],
      ['files', viaObject((o) => { o.files[fileKeys[0]] = 'abc'; })],
      ['files', viaObject((o) => { o.files[fileKeys[0]] = 'A'.repeat(64); })],
      ['files', viaObject((o) => { o.files[fileKeys[0]] = 1; })],
      ['files/status', viaObject((o) => { delete o.files[statusPath]; })],
    ];
    for (const [category, mutate] of cases) {
      const v = writeVariant(orig, mutate);
      expectParityReject(v, category);
    }
  });

  test('저장소 상대 경로 계약: S·loader 모두 paths, 대상 경로 접근 0', () => {
    const orig = makeOriginal();
    const sentinelRel = `tests/.tmp/abs-sentinel-${process.pid}.txt`;
    const sentinelAbs = path.resolve(REPO_ROOT, sentinelRel);
    created.add(sentinelAbs);
    fs.writeFileSync(sentinelAbs, `abs-sentinel-${process.pid}\n`, { flag: 'wx' });
    const sentinelSha = sha256(fs.readFileSync(sentinelAbs));
    const sentinelMtime = fs.statSync(sentinelAbs).mtimeMs;
    const o0 = JSON.parse(orig.text);
    expect(o0.statusZHex === '' || o0.statusZHex.endsWith('00')).toBe(true);
    const outsideHex = Buffer.from(` M ../outside.txt${NUL}`).toString('hex');

    const cases = [
      viaObject((o) => { o.files['../outside.txt'] = null; }),
      viaObject((o) => { o.files[sentinelAbs] = null; }),
      viaObject((o) => { o.files['a//b'] = null; }),
      viaObject((o) => { o.files['./x'] = null; }),
      viaObject((o) => { o.files['x/..'] = null; }),
      viaObject((o) => {
        o.statusZHex += outsideHex;
        o.xy['../outside.txt'] = ' M';
        o.files['../outside.txt'] = null;
      }),
    ];
    for (const mutate of cases) {
      const v = writeVariant(orig, mutate);
      const parsed = JSON.parse(fs.readFileSync(absOf(v.rel), 'utf8'));
      // 정상 identity 유지: stepId 외 identity 필드는 S가 만든 원본과 같다
      for (const k of ['schemaVersion', 'projectRoot', 'head', 'base', 'harness']) expect(parsed[k]).toEqual(o0[k]);
      expectParityReject(v, 'paths');

      const calls = [];
      const e = loaderError(v.rel, { fs: recordingFs(calls) });
      expect(e.message).toBe(`bad start snapshot: paths: ${v.rel}`);
      const allowed = new Set([REPO_ROOT, absOf('tests'), absOf('tests/.tmp'), absOf(v.rel)]);
      for (const c of calls) {
        for (const a of c.slice(1)) {
          if (/^[0-9]+$/.test(a)) continue; // fd·flags·mode
          expect(allowed.has(a), `${c[0]} ${a}`).toBe(true);
        }
        expect(['lstatSync', 'openSync', 'fstatSync', 'readFileSync', 'closeSync']).toContain(c[0]);
      }
      const touched = calls.flat().join('\n');
      expect(touched).not.toContain('outside.txt');
      expect(touched).not.toContain('abs-sentinel');
    }
    expect(sha256(fs.readFileSync(sentinelAbs))).toBe(sentinelSha);
    expect(fs.statSync(sentinelAbs).mtimeMs).toBe(sentinelMtime);
  });

  test('정상 사본: loader 반환 구조와 S reused', () => {
    const orig = makeOriginal();
    const o0 = JSON.parse(orig.text);
    const v = writeVariant(orig);
    const s = runS(v.id);
    expect(s.code, s.stderr).toBe(0);
    expect(s.stdout.trim()).toBe(`start-snapshot: reused ${v.rel}`);
    const got = loadStartSnapshot(v.rel, { root: REPO_ROOT });
    expect(Object.keys(got).sort()).toEqual(['entries', 'files', 'identity', 'stepId', 'xy']);
    expect(got.stepId).toBe(v.id);
    expect(got.identity).toEqual({
      schemaVersion: 1, projectRoot: o0.projectRoot, head: o0.head, base: o0.base, harness: o0.harness,
    });
    expect(got.xy).toEqual(o0.xy);
    expect(got.files).toEqual(o0.files);
    expect(Array.isArray(got.entries)).toBe(true);
    expect(Object.fromEntries(got.entries.flatMap((x) => [[x.path, x.xy], ...(x.origPath ? [[x.origPath, x.xy]] : [])])))
      .toEqual(o0.xy);
    expect(sha256(fs.readFileSync(absOf(v.rel)))).toBe(v.sha);
  });
});
