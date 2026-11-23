// step 2 — scope-snapshot.mjs 순수 파싱 함수 (node 전용, desktop-dark에서만 실행)
import { test, expect } from '@playwright/test';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  isRepoRelative, parseStatusZ, statusXyMap, scanJsonTopLevel, isSchemaVersion1,
} from '../scripts/scope-snapshot.mjs';

const TESTS_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const REPO_ROOT = path.resolve(TESTS_DIR, '..');
const DESIGN_DOC = path.join(REPO_ROOT, 'docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md');
const NUL = String.fromCharCode(0);

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

// S 본문에서 rel_ok 함수 정의(def 줄부터 다음 최상위 줄 직전까지)를 그대로 잘라낸다.
function relOkSource() {
  const lines = designBlock('스크립트 S').split('\n');
  const start = lines.findIndex((l) => l.startsWith('def rel_ok('));
  expect(start).toBeGreaterThanOrEqual(0);
  let end = start + 1;
  while (end < lines.length && /^\s/.test(lines[end])) end += 1;
  return `${lines.slice(start, end).join('\n')}\n`;
}

const deepCopy = (v) => JSON.parse(JSON.stringify(v));

test.describe('step 2 scope-snapshot parse', () => {
  test.beforeEach(({}, testInfo) => {
    test.skip(testInfo.project.name !== 'desktop-dark', 'node 전용 검사는 desktop-dark에서만 실행');
  });

  test('isRepoRelative: 저장소 상대 경로 계약, S rel_ok와 일치', () => {
    const truthy = ['a', 'tests/specs/a.spec.js', '.harness/policy.json', 'a..b/c'];
    const falsy = ['', '/abs', '/', '../outside.txt', 'a/../b', './a', 'a/./b', '..', '.', 'a//b', 'a/',
      `a${NUL}b`, null, 1, 0, { p: 'a' }];
    for (const p of truthy) expect(isRepoRelative(p), JSON.stringify(p)).toBe(true);
    for (const p of falsy) expect(isRepoRelative(p), JSON.stringify(p)).toBe(false);

    const inputs = [...truthy, ...falsy];
    const before = deepCopy(inputs);
    const harness = [
      'import json, os, sys',
      'exec(sys.argv[1])',
      'print(json.dumps([rel_ok(p) for p in json.loads(sys.argv[2])]))',
    ].join('\n');
    const r = spawnSync('python3', ['-I', '-c', harness, relOkSource(), JSON.stringify(inputs)], {
      encoding: 'utf8', timeout: 10000,
    });
    expect(r.error).toBeUndefined();
    expect(r.status, r.stderr).toBe(0);
    const py = JSON.parse(r.stdout);
    expect(py).toEqual(inputs.map((p) => isRepoRelative(p)));
    expect(py).toEqual([...truthy.map(() => true), ...falsy.map(() => false)]);
    expect(inputs).toEqual(before);
  });

  test('parseStatusZ·statusXyMap: 정상 레코드', () => {
    expect(parseStatusZ(Buffer.from(` M CLAUDE.md${NUL}?? docs/a.md${NUL}`))).toEqual([
      { xy: ' M', path: 'CLAUDE.md', origPath: null },
      { xy: '??', path: 'docs/a.md', origPath: null },
    ]);
    // 끝 NUL 없음도 허용
    expect(parseStatusZ(Buffer.from(' M CLAUDE.md'))).toEqual([{ xy: ' M', path: 'CLAUDE.md', origPath: null }]);
    const raw = Buffer.from(`R  new.md${NUL}old.md${NUL}`);
    const rawCopy = Buffer.from(raw);
    const entries = parseStatusZ(raw);
    expect(entries).toEqual([{ xy: 'R ', path: 'new.md', origPath: 'old.md' }]);
    expect(raw.equals(rawCopy)).toBe(true);
    const entriesCopy = deepCopy(entries);
    expect(statusXyMap(entries)).toEqual({ 'new.md': 'R ', 'old.md': 'R ' });
    expect(entries).toEqual(entriesCopy);
    expect(parseStatusZ(Buffer.alloc(0))).toEqual([]);
    expect(parseStatusZ('')).toEqual([]);
    expect(statusXyMap([])).toEqual({});
  });

  test('parseStatusZ: 형식 오류와 경로 계약 위반은 throw', () => {
    // 끝 NUL은 하나만 허용 — 두 개면 빈 레코드
    expect(() => parseStatusZ(Buffer.from(` M a${NUL}${NUL}`))).toThrow(/^bad status record/);
    for (const bad of ['M a', ' Ma', ' M', `?? docs/a.md${NUL}abc`, 'XYZa']) {
      expect(() => parseStatusZ(Buffer.from(bad)), JSON.stringify(bad)).toThrow(/^bad status record/);
    }
    expect(() => parseStatusZ(Buffer.from('R  new.md'))).toThrow(/^bad status record/);
    expect(() => parseStatusZ(Buffer.from(`R  new.md${NUL}`))).toThrow(/^bad status record/);
    expect(() => parseStatusZ(Buffer.from(`R  new.md${NUL}${NUL}`))).toThrow(/^bad status record/);
    expect(() => parseStatusZ(Buffer.from(` C new.md${NUL}`))).toThrow(/^bad status record/);
    for (const bad of [' M ../outside.txt', '?? /abs/x', ' M a//b', `R  new.md${NUL}../old.md`]) {
      expect(() => parseStatusZ(Buffer.from(bad)), JSON.stringify(bad)).toThrow(/^bad path/);
    }
  });

  test('scanJsonTopLevel: 최상위 token만, 문자열·중첩 무시', () => {
    expect(scanJsonTopLevel('{"schemaVersion":1}')).toEqual([{ key: 'schemaVersion', token: '1' }]);
    expect(scanJsonTopLevel('{"a":{"schemaVersion":1},"schemaVersion":1.0}')).toEqual([
      { key: 'a', token: '{"schemaVersion":1}' },
      { key: 'schemaVersion', token: '1.0' },
    ]);
    expect(scanJsonTopLevel('{"s":"\\"schemaVersion\\": 1","schemaVersion":1e0}')).toEqual([
      { key: 's', token: '"\\"schemaVersion\\": 1"' },
      { key: 'schemaVersion', token: '1e0' },
    ]);
    expect(scanJsonTopLevel('{"a":[{"b":"},"}],"schemaVersion" : 1 }')).toEqual([
      { key: 'a', token: '[{"b":"},"}]' },
      { key: 'schemaVersion', token: '1' },
    ]);
    const text = '{\n "o" : { "x" : [1, {"y": "]"}] } ,\n "arr":[ ],\t"n":null }';
    const copy = `${text}`;
    expect(scanJsonTopLevel(text)).toEqual([
      { key: 'o', token: '{ "x" : [1, {"y": "]"}] }' },
      { key: 'arr', token: '[ ]' },
      { key: 'n', token: 'null' },
    ]);
    expect(text).toBe(copy);
    expect(scanJsonTopLevel('[1]')).toEqual([]);
    expect(scanJsonTopLevel('"x"')).toEqual([]);
    expect(scanJsonTopLevel('{}')).toEqual([]);
  });

  test('scanJsonTopLevel: 중복 key throw', () => {
    const dups = [
      '{"schemaVersion":1,"schemaVersion":1}',
      '{"schemaVersion":1,"a":2,"schemaVersion":2}',
      '{"schema\\u0056ersion":1,"schemaVersion":1}',
      '{"schemaVersion":1,"schema\\u0056ersion":1}',
      '{"a":{"b":1,"b":2},"schemaVersion":1}',
      '{"a":[{"b":1,"b":2}]}',
    ];
    for (const d of dups) {
      expect(() => JSON.parse(d)).not.toThrow();
      expect(() => scanJsonTopLevel(d), d).toThrow(/^duplicate key: /);
    }
    expect(() => scanJsonTopLevel(dups[2])).toThrow('duplicate key: schemaVersion');
    // 다른 객체의 같은 key는 중복 아님
    expect(scanJsonTopLevel('{"a":{"b":1},"c":{"b":2}}')).toEqual([
      { key: 'a', token: '{"b":1}' },
      { key: 'c', token: '{"b":2}' },
    ]);
  });

  test('isSchemaVersion1: 값과 lexical token 모두 1', () => {
    expect(isSchemaVersion1(1, '1')).toBe(true);
    expect(isSchemaVersion1(2, '2')).toBe(false);
    expect(isSchemaVersion1(true, 'true')).toBe(false);
    expect(isSchemaVersion1('1', '"1"')).toBe(false);
    expect(isSchemaVersion1(1, '1.0')).toBe(false);
    expect(isSchemaVersion1(1, '1e0')).toBe(false);
  });
});
