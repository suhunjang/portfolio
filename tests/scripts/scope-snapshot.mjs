// 범위 비교 도구 (설계 §11.7). S·C와 같은 판정·문자열·순서를 쓴다.
// step 1: 상수, 경로 유형 검사, 안전 읽기. 파일 쓰기·CLI 없음.
// step 2: 저장소 상대 경로 판정, status parser, 최상위 JSON token scanner, schemaVersion 판정 (순수).
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

// ---- step 2: 파싱 (순수 함수, 파일 시스템 접근 없음, 입력을 바꾸지 않음) ----------------------

// 저장소 상대 경로 계약 (S·C의 rel_ok와 같은 판정)
export function isRepoRelative(p) {
  return typeof p === 'string' && p !== '' && !p.includes(String.fromCharCode(0))
    && !path.isAbsolute(p) && path.parse(p).root === ''
    && p.split('/').every((c) => c !== '' && c !== '.' && c !== '..');
}

// git status --porcelain=v1 -z 원문 → { xy, path, origPath }[] (S의 parse_status와 같은 엄격 규칙)
export function parseStatusZ(raw) {
  const buf = typeof raw === 'string' ? Buffer.from(raw, 'utf8') : Buffer.from(raw);
  const recs = [];
  let from = 0;
  for (let i = 0; i < buf.length; i += 1) {
    if (buf[i] === 0) {
      recs.push(buf.subarray(from, i));
      from = i + 1;
    }
  }
  recs.push(buf.subarray(from));
  if (recs.length && recs[recs.length - 1].length === 0) recs.pop();
  const out = [];
  let i = 0;
  while (i < recs.length) {
    const rec = recs[i];
    i += 1;
    if (rec.length < 4 || rec[2] !== 0x20) {
      throw new Error(`bad status record: ${JSON.stringify(rec.toString('utf8'))}`);
    }
    const xy = rec.subarray(0, 2).toString('utf8');
    const p = rec.subarray(3).toString('utf8');
    if (!isRepoRelative(p)) throw new Error(`bad path: ${JSON.stringify(p)}`);
    let origPath = null;
    if ('RC'.includes(xy[0]) || 'RC'.includes(xy[1])) {
      if (i >= recs.length || recs[i].length === 0) {
        throw new Error(`bad status record: missing origPath for ${JSON.stringify(p)}`);
      }
      origPath = recs[i].toString('utf8');
      if (!isRepoRelative(origPath)) throw new Error(`bad path: ${JSON.stringify(origPath)}`);
      i += 1;
    }
    out.push({ xy, path: p, origPath });
  }
  return out;
}

// path·origPath 모두 → xy
export function statusXyMap(entries) {
  const xy = {};
  for (const e of entries) {
    xy[e.path] = e.xy;
    if (e.origPath !== null && e.origPath !== undefined) xy[e.origPath] = e.xy;
  }
  return xy;
}

// JSON.parse가 성공한 텍스트의 최상위 객체 멤버 { key, token }[] (원문 순서). 모든 깊이의 중복 key는 throw.
export function scanJsonTopLevel(rawText) {
  const text = String(rawText);
  const stack = [];
  const out = [];
  let topIsObject = null;
  let pendingKey = null;
  let valueStart = -1;
  const atTop = () => stack.length === 1 && stack[0].kind === 'object';
  const flush = (end) => {
    if (pendingKey !== null) out.push({ key: pendingKey, token: text.slice(valueStart, end).trim() });
    pendingKey = null;
  };
  let i = 0;
  while (i < text.length) {
    const ch = text[i];
    if (ch === ' ' || ch === '\t' || ch === '\n' || ch === '\r') {
      i += 1;
    } else if (ch === '"') {
      let j = i + 1;
      while (j < text.length && text[j] !== '"') j += text[j] === '\\' ? 2 : 1;
      const top = stack[stack.length - 1];
      if (top && top.kind === 'object' && top.expectKey) {
        const key = JSON.parse(text.slice(i, j + 1));
        if (top.keys.has(key)) throw new Error(`duplicate key: ${key}`);
        top.keys.add(key);
        top.expectKey = false;
        if (stack.length === 1) pendingKey = key;
      }
      if (topIsObject === null) topIsObject = false;
      i = j + 1;
    } else if (ch === ':') {
      if (atTop()) valueStart = i + 1;
      i += 1;
    } else if (ch === ',') {
      if (atTop()) flush(i);
      const top = stack[stack.length - 1];
      if (top && top.kind === 'object') top.expectKey = true;
      i += 1;
    } else if (ch === '{' || ch === '[') {
      if (topIsObject === null) topIsObject = ch === '{';
      stack.push({ kind: ch === '{' ? 'object' : 'array', keys: new Set(), expectKey: ch === '{' });
      i += 1;
    } else if (ch === '}' || ch === ']') {
      if (atTop()) flush(i);
      stack.pop();
      i += 1;
    } else {
      if (topIsObject === null) topIsObject = false;
      i += 1;
    }
  }
  return topIsObject ? out : [];
}

// 값이 정수 1이고 lexical token이 정확히 '1'
export function isSchemaVersion1(value, token) {
  return Number.isInteger(value) && value === 1 && token === '1';
}
