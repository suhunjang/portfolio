// 범위 비교 도구 (설계 §11.7). S·C와 같은 판정·문자열·순서를 쓴다.
// step 1: 상수, 경로 유형 검사, 안전 읽기. 파일 쓰기·CLI 없음.
import nodeFs from 'node:fs';
import path from 'node:path';

export const RUNTIME_PREFIXES = Object.freeze([
  'tests/node_modules/', 'tests/.npm-cache/', 'tests/.pw-browsers/', 'tests/.tmp/',
  'tests/test-results/', 'tests/playwright-report/', 'tests/screenshots/',
]);
export const SKIP_PREFIXES = Object.freeze([...RUNTIME_PREFIXES, '.git/', '.venv/']);
export const EXEMPT_PREFIXES = Object.freeze(['.harness/', '.venv/', 'phases/HOO-81-portfolio-redesign/']);
export const GUARDED_PATHS = Object.freeze(['.harness/harness.lock.json', '.harness/policy.json']);
export const LOCK_PATH = '.harness/harness.lock.json';
export const SNAPSHOT_KEYS = Object.freeze([
  'schemaVersion', 'stepId', 'projectRoot', 'head', 'base', 'harness', 'statusZHex', 'xy', 'files',
]);
export const STEP_ID_RE = /^(?:step[0-9]+|axe-remediation-[a-z0-9]+(?:-[a-z0-9]+)*|parity-[0-9]+)$/;
export const HEX64_RE = /^[0-9a-f]{64}$/;
export const BASE = 'd0a8a6e462bc1366757b1401c3ba7aeb0fbf391d';
export const HARNESS_IDENTITY = Object.freeze({
  sourceCommit: 'cb179f99acbb9ad32c5dcebab01ff19df7c3f4ae',
  manifestHash: '287201c44d766b0441470953005450b40f300de2718b246eeb44fd0e3c2f900a',
  distributionVersion: '2.0.0',
});
export const STATUS_ARGS = Object.freeze(['status', '--porcelain=v1', '-z', '--untracked-files=all']);
export const LS_FILES_ARGS = Object.freeze(['ls-files', '-z']);

export class UnsafePathError extends Error {
  constructor(item) {
    super(`unsafe path: ${item}`);
    this.name = 'UnsafePathError';
    this.item = item;
  }
}

// lstat 결과 → missing | file | dir | symlink | other (링크를 따라가지 않음)
function kindAt(fs, abs) {
  let st;
  try {
    st = fs.lstatSync(abs);
  } catch (e) {
    if (e && e.code === 'ENOENT') return 'missing';
    throw e;
  }
  if (st.isSymbolicLink()) return 'symlink';
  if (st.isDirectory()) return 'dir';
  if (st.isFile()) return 'file';
  return 'other';
}

function label(kind, p) {
  if (kind === 'symlink') return `symlink:${p}`;
  if (kind === 'missing') return `missing:${p}`;
  return `non-regular:${p}`;
}

// projectRoot 자체를 lstat 1회로 검사한다. dir가 아니면 UnsafePathError.
export function checkRoot({ fs = nodeFs, root = process.cwd() } = {}) {
  const k = kindAt(fs, root);
  if (k !== 'dir') throw new UnsafePathError(label(k, root));
}

// projectRoot 기준 상대 경로 p의 유형 (lstatSync만)
export function pathKind(p, { fs = nodeFs, root = process.cwd() } = {}) {
  return kindAt(fs, path.join(root, p));
}

// S의 check와 같은 조상·leaf 규칙. 먼저 checkRoot(오류는 그대로 전파).
export function checkPath(p, leafKinds, { fs = nodeFs, root = process.cwd() } = {}) {
  checkRoot({ fs, root });
  const parts = p.split('/');
  for (let i = 1; i < parts.length; i += 1) {
    const a = parts.slice(0, i).join('/');
    const k = kindAt(fs, path.join(root, a));
    if (k === 'missing') return leafKinds.includes('missing') ? null : `missing:${p}`;
    if (k !== 'dir') return label(k, a);
  }
  const k = kindAt(fs, path.join(root, p));
  return leafKinds.includes(k) ? null : label(k, p);
}

// O_RDONLY | O_NOFOLLOW | O_NONBLOCK으로 열고, 연 fd가 regular가 아니면 읽지 않고 거부한다.
export function readRegular(p, { fs = nodeFs, root = process.cwd() } = {}) {
  const { O_RDONLY, O_NOFOLLOW, O_NONBLOCK } = nodeFs.constants;
  const fd = fs.openSync(path.join(root, p), O_RDONLY | O_NOFOLLOW | O_NONBLOCK);
  try {
    if (!fs.fstatSync(fd).isFile()) throw new UnsafePathError(`non-regular:${p}`);
    return fs.readFileSync(fd);
  } finally {
    fs.closeSync(fd);
  }
}
