#!/usr/bin/env node
// step 24 — BASE fixture 생성 (설계 §5): git show BASE:js/data.js → vm 평가 → baseline-data.json,
// git show BASE:index.html → baseline-index.html. Git은 읽기(show)만.
import { execFileSync } from 'node:child_process';
import { writeFileSync, mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import vm from 'node:vm';
import { BASE } from './scope-snapshot.mjs';

const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const FIXTURES = path.join(REPO_ROOT, 'tests', 'fixtures');
export const BASELINE_KEYS = ['PROFILE', 'STATS', 'CAREER', 'VIS_ACCENT', 'PROJECTS', 'STRENGTHS', 'SKILLS'];

function gitShow(spec) {
  return execFileSync('git', ['-C', REPO_ROOT, 'show', spec], { maxBuffer: 64 * 1024 * 1024 });
}

export function evalDataJs(source) {
  const context = vm.createContext({ window: {} });
  vm.runInContext(source, context, { filename: 'BASE:js/data.js' });
  const data = vm.runInContext(`({ ${BASELINE_KEYS.join(', ')} })`, context);
  return JSON.parse(JSON.stringify(data));
}

function main() {
  mkdirSync(FIXTURES, { recursive: true });
  const data = evalDataJs(gitShow(`${BASE}:js/data.js`).toString('utf8'));
  writeFileSync(path.join(FIXTURES, 'baseline-data.json'), JSON.stringify(data, null, 2) + '\n');
  writeFileSync(path.join(FIXTURES, 'baseline-index.html'), gitShow(`${BASE}:index.html`));
  console.log('make-fixtures: OK');
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main();
