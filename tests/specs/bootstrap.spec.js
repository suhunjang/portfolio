// step 0 — tests 실행 환경 bootstrap 검증 (node 전용, desktop-dark에서만 실행)
import { test, expect } from '@playwright/test';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import config from '../playwright.config.js';
import { HARNESS_IDENTITY } from '../scripts/scope-snapshot.mjs';

const TESTS_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const REPO_ROOT = path.resolve(TESTS_DIR, '..');
const DESIGN_DOC = path.join(REPO_ROOT, 'docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md');
const S_SCRIPT = 'tests/scripts/start-snapshot.py';
const TMP_DIR = path.join(REPO_ROOT, 'tests/.tmp');
const PROBE_DIR = path.join(TMP_DIR, 'snapshot-probes');
const PROBE = path.join(PROBE_DIR, '__retry_probe.txt');
const SNAPSHOT_KEYS = ['base', 'files', 'harness', 'head', 'projectRoot', 'schemaVersion', 'statusZHex', 'stepId', 'xy'];
const SKIP_PREFIXES = [
  'tests/node_modules/', 'tests/.npm-cache/', 'tests/.pw-browsers/', 'tests/.tmp/',
  'tests/test-results/', 'tests/playwright-report/', 'tests/screenshots/', '.git/', '.venv/',
];

const sha256 = (buf) => createHash('sha256').update(buf).digest('hex');
const snapshotPath = (id) => path.join(TMP_DIR, `start-snapshot-${id}.json`);

let seq = 0;
const runBase = `${Date.now()}${process.pid}`;
const created = [];
function nextParityId() {
  seq += 1;
  const id = `parity-${runBase}${String(seq).padStart(3, '0')}`;
  created.push(snapshotPath(id));
  return id;
}

function runS(id) {
  const r = spawnSync('python3', ['-I', S_SCRIPT, id], { cwd: REPO_ROOT, encoding: 'utf8', timeout: 10000 });
  if (r.error) throw r.error;
  return { status: r.status, stdout: r.stdout, stderr: r.stderr };
}

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

test.describe('step 0 bootstrap', () => {
  test.beforeEach(({}, testInfo) => {
    test.skip(testInfo.project.name !== 'desktop-dark', 'node 전용 검사는 desktop-dark에서만 실행');
  });

  test.afterAll(() => {
    for (const f of created) fs.rmSync(f, { force: true });
  });

  test('playwright config는 직렬이고 6 project를 정의한다', () => {
    expect(config.workers).toBe(1);
    expect(config.fullyParallel).toBe(false);
    const expected = [];
    const sizes = { mobile: [375, 812], tablet: [768, 1024], desktop: [1280, 800] };
    for (const [device, [width, height]] of Object.entries(sizes)) {
      for (const theme of ['dark', 'light']) expected.push({ name: `${device}-${theme}`, width, height, theme });
    }
    expect(config.projects.map((p) => p.name).sort()).toEqual(expected.map((e) => e.name).sort());
    for (const e of expected) {
      const p = config.projects.find((x) => x.name === e.name);
      expect(p.use.viewport).toEqual({ width: e.width, height: e.height });
      expect(p.use.colorScheme).toBe(e.theme);
      expect(p.metadata.theme).toBe(e.theme);
    }
  });

  test('.gitignore 7줄과 with-env.sh 래퍼', () => {
    const gi = fs.readFileSync(path.join(TESTS_DIR, '.gitignore'), 'utf8');
    expect(gi).toBe('node_modules/\n.npm-cache/\n.pw-browsers/\n.tmp/\ntest-results/\nplaywright-report/\nscreenshots/\n');
    const sh = fs.readFileSync(path.join(TESTS_DIR, 'scripts/with-env.sh'), 'utf8');
    const lines = sh.split('\n');
    expect(lines[0]).toBe('#!/bin/sh');
    expect(lines[1]).toBe('set -eu');
    expect(lines).toContain('export PLAYWRIGHT_BROWSERS_PATH="$REPO_ROOT/tests/.pw-browsers"');
  });

  test('start-snapshot.py bytes = 설계 S 블록', () => {
    const actual = fs.readFileSync(path.join(REPO_ROOT, S_SCRIPT));
    expect(actual.equals(Buffer.from(designBlock('스크립트 S'), 'utf8'))).toBe(true);
  });

  test('scope-snapshot HARNESS_IDENTITY = 설계 S HARNESS', () => {
    const m = designBlock('스크립트 S').match(/^HARNESS = (\{.*\})$/m);
    expect(m, 'S HARNESS line').not.toBeNull();
    const sHarness = JSON.parse(m[1].replace(/'/g, '"'));
    expect({ ...HARNESS_IDENTITY }).toEqual(sHarness);
  });

  test('S 최초 생성·재사용·identity/schemaVersion 거부', () => {
    const id = nextParityId();
    const file = snapshotPath(id);
    expect(fs.existsSync(file)).toBe(false);

    // 최초 생성
    const first = runS(id);
    expect(first.status, first.stderr).toBe(0);
    expect(first.stdout).toContain(`start-snapshot: created tests/.tmp/start-snapshot-${id}.json`);
    const raw = fs.readFileSync(file, 'utf8');
    const snap = JSON.parse(raw);
    expect(Object.keys(snap).sort()).toEqual(SNAPSHOT_KEYS);
    expect(snap.stepId).toBe(id);
    expect(snap.schemaVersion).toBe(1);
    expect(snap.files['tests/playwright.config.js']).toBe(sha256(fs.readFileSync(path.join(TESTS_DIR, 'playwright.config.js'))));
    for (const [p, v] of Object.entries(snap.files)) {
      expect(v === null || /^[0-9a-f]{64}$/.test(v), p).toBe(true);
      expect(SKIP_PREFIXES.some((s) => p.startsWith(s)), p).toBe(false);
      if (v === null) {
        let code = null;
        try { fs.lstatSync(path.join(REPO_ROOT, p)); } catch (e) { code = e.code; }
        expect(code, p).toBe('ENOENT');
      }
    }
    const firstHash = sha256(fs.readFileSync(file));
    const firstMtime = fs.statSync(file).mtimeMs;

    // 중간 실패 뒤 재사용: runtime probe가 생겨도 기존 baseline 재사용
    try {
      fs.mkdirSync(PROBE_DIR, { recursive: true });
      fs.writeFileSync(PROBE, 'probe\n');
      const again = runS(id);
      expect(again.status, again.stderr).toBe(0);
      expect(again.stdout).toContain(`start-snapshot: reused tests/.tmp/start-snapshot-${id}.json`);
      expect(sha256(fs.readFileSync(file))).toBe(firstHash);
      expect(fs.statSync(file).mtimeMs).toBe(firstMtime);
    } finally {
      fs.rmSync(PROBE, { force: true });
      try { fs.rmdirSync(PROBE_DIR); } catch { /* 비어 있지 않거나 없음 */ }
    }

    // identity 거부: 한 필드씩 바꾼 별도 parity 파일
    const variants = [
      ['stepId', (o) => { /* stepId는 원본(id) 그대로 두어 파일명과 다르게 */ }, 'stepId'],
      ['head', (o) => { o.head = '0'.repeat(40); }, 'head'],
      ['base', (o) => { o.base = 'f'.repeat(40); }, 'base'],
      ['projectRoot', (o) => { o.projectRoot = '/tmp/other'; }, 'projectRoot'],
      ['harness.manifestHash', (o) => { o.harness.manifestHash = '0'.repeat(64); }, 'harness'],
      ['harness.lockSha256', (o) => { o.harness.lockSha256 = '0'.repeat(64); }, 'harness'],
    ];
    for (const [name, mutate, field] of variants) {
      const vid = nextParityId();
      const vfile = snapshotPath(vid);
      const obj = JSON.parse(raw);
      if (name !== 'stepId') obj.stepId = vid;
      mutate(obj);
      fs.writeFileSync(vfile, JSON.stringify(obj, null, 1));
      const before = sha256(fs.readFileSync(vfile));
      const r = runS(vid);
      expect(r.status, name).not.toBe(0);
      expect(r.stderr, name).toMatch(new RegExp(`identity mismatch: ${field}|bad start snapshot`));
      expect(sha256(fs.readFileSync(vfile)), name).toBe(before);
    }

    // schemaVersion 거부: 원문 텍스트 변형
    const replaceOnce = (text, from, to) => {
      expect(text.split(from).length - 1, `token ${from}`).toBe(1);
      return text.replace(from, to);
    };
    const SV = '\n "schemaVersion": 1,';
    const textVariants = [
      ['2', (t) => replaceOnce(t, SV, '\n "schemaVersion": 2,'), 'schemaVersion'],
      ['true', (t) => replaceOnce(t, SV, '\n "schemaVersion": true,'), 'schemaVersion'],
      ['1.0', (t) => replaceOnce(t, SV, '\n "schemaVersion": 1.0,'), 'schemaVersion'],
      ['1e0', (t) => replaceOnce(t, SV, '\n "schemaVersion": 1e0,'), 'schemaVersion'],
      ['dup-end-1.0', (t) => `${t.slice(0, t.lastIndexOf('}'))}, "schemaVersion": 1.0}${t.slice(t.lastIndexOf('}') + 1)}`, 'invalid json'],
      ['dup-end-1e0', (t) => `${t.slice(0, t.lastIndexOf('}'))}, "schemaVersion": 1e0}${t.slice(t.lastIndexOf('}') + 1)}`, 'invalid json'],
      ['dup-start-1.0', (t) => t.replace('{', '{"schemaVersion": 1.0, '), 'invalid json'],
      ['nested-harness', (t) => replaceOnce(replaceOnce(t, SV, '\n "schemaVersion": 1.0,'), '"harness": {', '"harness": {"schemaVersion": 1, '), 'schemaVersion'],
      ['files-NaN', (t) => t.replace(/("tests\/playwright\.config\.js": )"[0-9a-f]{64}"/, (_, k) => `${k}NaN`), 'invalid json'],
    ];
    for (const [name, mutate, category] of textVariants) {
      const vid = nextParityId();
      const vfile = snapshotPath(vid);
      const base = replaceOnce(raw, `"stepId": "${id}"`, `"stepId": "${vid}"`);
      const text = mutate(base);
      expect(text, name).not.toBe(base);
      fs.writeFileSync(vfile, text);
      const before = sha256(fs.readFileSync(vfile));
      const r = runS(vid);
      expect(r.status, name).not.toBe(0);
      expect(r.stderr, name).toContain(`bad start snapshot: ${category}: tests/.tmp/start-snapshot-${vid}.json`);
      expect(sha256(fs.readFileSync(vfile)), name).toBe(before);
    }

    // 최초 snapshot은 끝까지 불변
    expect(sha256(fs.readFileSync(file))).toBe(firstHash);
  });

  test('잘못된 step id는 파일을 만들지 않고 거부한다', () => {
    const listing = () => JSON.stringify([
      fs.readdirSync(TESTS_DIR).sort(),
      fs.readdirSync(TMP_DIR).filter((n) => n.startsWith('start-snapshot')).sort(),
    ]);
    for (const bad of ['step', '../x', 'Step1']) {
      const before = listing();
      const r = runS(bad);
      expect(r.status, bad).not.toBe(0);
      expect(r.stderr, bad).toContain('bad step id');
      expect(listing(), bad).toBe(before);
    }
  });
});
