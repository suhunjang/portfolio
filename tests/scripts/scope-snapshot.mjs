// 범위 비교 도구 (설계 §11.7). S·C와 같은 판정·문자열·순서를 쓴다.
// step 1: 상수, 경로 유형 검사, 안전 읽기. 파일 쓰기·CLI 없음.
// step 2: 저장소 상대 경로 판정, status parser, 최상위 JSON token scanner, schemaVersion 판정 (순수).
// step 3: strict schema loader (loadStartSnapshot).
// step 4: 현재 상태 수집 (scanProject, hashPath, takeCurrent). Git 읽기만, 쓰기 없음.
// step 7: identity(computeIdentity, checkIdentity), 순수 판정(diffAgainstStart … evaluateGate). 쓰기 없음.
// step 8: after.z 안전 쓰기(writeAfterZ), runCheck 실행 순서, CLI --check.
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
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
  sourceCommit: 'e7a03919a460f975149f7c55343ca4b34d3d2352',
  manifestHash: 'b627e6a5ce4a903c24c400927ca2b49a14d0bd59632c691b2a5c2d74c6c08372',
  distributionVersion: '2.0.1',
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

// ---- step 3: strict schema loader (쓰기 없음, snapshot 파일 경로 외 접근 없음) -------------------

const UTF8_STRICT = new TextDecoder('utf-8', { fatal: true, ignoreBOM: true });
function utf8Ok(bytes) {
  try {
    UTF8_STRICT.decode(bytes);
    return true;
  } catch {
    return false;
  }
}
const isPlainObject = (v) => v !== null && typeof v === 'object' && !Array.isArray(v);
const hasOwn = (o, k) => Object.prototype.hasOwnProperty.call(o, k);

// statusZHex 디코드 bytes를 S parse_status와 같은 범주로 판정한다.
// S는 레코드를 앞에서부터 decode하므로 첫 비UTF-8 레코드 앞에서 생긴 bad path만 paths, 그 밖은 status parse.
function parseSnapshotStatus(bytes) {
  const recs = [];
  let from = 0;
  for (let i = 0; i < bytes.length; i += 1) {
    if (bytes[i] === 0) {
      recs.push(bytes.subarray(from, i));
      from = i + 1;
    }
  }
  recs.push(bytes.subarray(from));
  const badUtf8 = recs.findIndex((r) => !utf8Ok(r));
  const input = badUtf8 < 0 ? bytes : Buffer.concat(recs.slice(0, badUtf8).flatMap((r) => [r, Buffer.alloc(1)]));
  let entries;
  try {
    entries = parseStatusZ(input);
  } catch (e) {
    return { error: String(e.message).startsWith('bad path') ? 'paths' : 'status parse' };
  }
  return badUtf8 < 0 ? { entries } : { error: 'status parse' };
}

// 시작 snapshot을 strict schema(설계 §11.7 검사 순서)로 읽는다. 오류는 throw.
export function loadStartSnapshot(file, { fs = nodeFs, root = process.cwd() } = {}) {
  const item = checkPath(file, ['file'], { fs, root });
  if (item) throw new UnsafePathError(item);
  const raw = readRegular(file, { fs, root });
  const fail = (what) => new Error(`bad start snapshot: ${what}: ${file}`);

  let obj;
  let top;
  try {
    const text = UTF8_STRICT.decode(raw);
    obj = JSON.parse(text);
    top = scanJsonTopLevel(text);
  } catch {
    throw fail('invalid json');
  }
  if (!isPlainObject(obj)) throw fail('keys');
  if (Object.keys(obj).length !== SNAPSHOT_KEYS.length || !SNAPSHOT_KEYS.every((k) => hasOwn(obj, k))) {
    throw fail('keys');
  }

  const sv = top.filter((m) => m.key === 'schemaVersion');
  if (sv.length !== 1 || !isSchemaVersion1(obj.schemaVersion, sv[0].token)) throw fail('schemaVersion');

  const { stepId } = obj;
  if (typeof stepId !== 'string' || !STEP_ID_RE.test(stepId) || file !== `tests/.tmp/start-snapshot-${stepId}.json`) {
    throw fail('stepId');
  }

  const hx = obj.statusZHex;
  if (typeof hx !== 'string' || hx.length % 2 !== 0 || !/^[0-9a-f]*$/.test(hx)) throw fail('statusZHex');
  const parsed = parseSnapshotStatus(Buffer.from(hx, 'hex'));
  if (parsed.error) throw fail(parsed.error);
  const { entries } = parsed;

  const xy = statusXyMap(entries);
  const xyKeys = Object.keys(xy);
  const oxy = obj.xy;
  if (!isPlainObject(oxy) || Object.keys(oxy).length !== xyKeys.length
    || !xyKeys.every((k) => hasOwn(oxy, k) && oxy[k] === xy[k])) {
    throw fail('xy');
  }

  const { files } = obj;
  if (!isPlainObject(files)
    || !Object.values(files).every((v) => v === null || (typeof v === 'string' && HEX64_RE.test(v)))) {
    throw fail('files');
  }
  if (!Object.keys(files).every((p) => isRepoRelative(p))) throw fail('paths');
  if (xyKeys.some((p) => !SKIP_PREFIXES.some((s) => p.startsWith(s)) && !hasOwn(files, p))) {
    throw fail('files/status');
  }

  return {
    stepId,
    identity: {
      schemaVersion: obj.schemaVersion,
      projectRoot: obj.projectRoot,
      head: obj.head,
      base: obj.base,
      harness: obj.harness,
    },
    entries,
    xy: oxy,
    files,
  };
}

// ---- step 4: 현재 상태 수집 (Git 읽기만, 링크를 따라가거나 읽지 않음, 쓰기 없음) ------------------

const isSkipped = (p) => SKIP_PREFIXES.some((s) => p.startsWith(s));
const sortedUnique = (items) => [...new Set(items)].sort();

// projectRoot부터 readdirSync(withFileTypes)로 걷는다(S의 scan과 같은 판정).
// symlink 엔트리(SKIP 디렉터리 엔트리 자체 포함)는 unsafe, SKIP 디렉터리 안은 들어가지 않는다.
export function scanProject({ fs = nodeFs, root = process.cwd() } = {}) {
  checkRoot({ fs, root });
  const unsafe = [];
  const testsFiles = [];
  const walk = (rel) => {
    const abs = rel ? path.join(root, rel) : root;
    for (const ent of fs.readdirSync(abs, { withFileTypes: true })) {
      const p = rel ? `${rel}/${ent.name}` : ent.name;
      if (ent.isSymbolicLink()) {
        unsafe.push(`symlink:${p}`);
      } else if (ent.isDirectory()) {
        if (!isSkipped(`${p}/`)) walk(p);
      } else if (p.startsWith('tests/')) {
        testsFiles.push(p);
      }
    }
  };
  walk('');
  return { unsafe: sortedUnique(unsafe), testsFiles: sortedUnique(testsFiles) };
}

// regular file이면 sha256, 경로가 없으면 null, 그 밖의 유형은 UnsafePathError (leaf lstat 후 file일 때만 open)
export function hashPath(p, { fs = nodeFs, root = process.cwd() } = {}) {
  const k = pathKind(p, { fs, root });
  if (k === 'missing') return null;
  if (k !== 'file') throw new UnsafePathError(label(k, p));
  return createHash('sha256').update(readRegular(p, { fs, root })).digest('hex');
}

// 기본 Git 읽기 (status·ls-files만 호출된다)
function runGit(args, root) {
  const r = spawnSync('git', args, { cwd: root, maxBuffer: 256 * 1024 * 1024 });
  if (r.error) throw r.error;
  if (r.status !== 0) throw new Error(`git ${args.join(' ')} failed: ${String(r.stderr).trim()}`);
  return r.stdout;
}

// 현재 status + 기록 대상 hash. start가 있으면 그 files·xy key를 먼저 경로 계약으로 검사한다(fs·git 접근 전).
// unsafe가 하나라도 있으면 hash하지 않고 files는 {}.
export function takeCurrent(start, { git, fs = nodeFs, root = process.cwd() } = {}) {
  const startFiles = start ? Object.keys(start.files ?? {}) : [];
  if (start) {
    const keys = [...startFiles, ...Object.keys(start.xy ?? {})];
    if (!keys.every((p) => isRepoRelative(p))) throw new Error('bad start snapshot: paths');
  }
  const readGit = git ?? ((args) => runGit(args, root));
  checkRoot({ fs, root });

  let entries;
  try {
    entries = parseStatusZ(readGit([...STATUS_ARGS]));
  } catch (e) {
    if (/^bad (status record|path)/.test(String(e?.message))) throw new Error('bad git status');
    throw e;
  }
  const xy = statusXyMap(entries);
  const scan = scanProject({ fs, root });
  const listed = Buffer.from(readGit([...LS_FILES_ARGS])).toString('utf8')
    .split(String.fromCharCode(0)).filter((p) => p !== '');

  const targets = sortedUnique([...Object.keys(xy), ...startFiles, ...scan.testsFiles, ...listed])
    .filter((p) => !isSkipped(p));
  const unsafe = [...scan.unsafe];
  for (const p of targets) {
    const r = checkPath(p, ['missing', 'file'], { fs, root });
    if (r) unsafe.push(r);
  }
  let files = {};
  if (unsafe.length === 0) {
    for (const p of targets) {
      try {
        files[p] = hashPath(p, { fs, root });
      } catch (e) {
        if (!(e instanceof UnsafePathError)) throw e;
        unsafe.push(e.item);
      }
    }
    if (unsafe.length) files = {};
  }
  return { entries, xy, files, unsafe: sortedUnique(unsafe) };
}

// ---- step 7: identity 계산·대조, 순수 변경·정책 판정 (파일 쓰기·CLI 없음) ---------------------------

const gitText = (out) => Buffer.from(out).toString('utf8').trim();

// 현재 identity. checkRoot → toplevel realpath = root realpath → lock 경로 유형 → HEAD → BASE 확인 → lock 읽기.
export function computeIdentity({ git, fs = nodeFs, root = process.cwd() } = {}) {
  const readGit = git ?? ((args) => runGit(args, root));
  checkRoot({ fs, root });
  const top = gitText(readGit(['rev-parse', '--show-toplevel']));
  const projectRoot = fs.realpathSync(top);
  if (projectRoot !== fs.realpathSync(root)) throw new Error(`run from project root: ${top}`);
  const item = checkPath(LOCK_PATH, ['file'], { fs, root });
  if (item) throw new UnsafePathError(item);
  const head = gitText(readGit(['rev-parse', 'HEAD']));
  try {
    readGit(['rev-parse', '--verify', `${BASE}^{commit}`]);
  } catch (e) {
    throw new Error(`base commit not found: ${BASE} (${e?.message ?? e})`);
  }
  const lock = readRegular(LOCK_PATH, { fs, root });
  if (!Object.values(HARNESS_IDENTITY).every((v) => lock.includes(Buffer.from(v, 'utf8')))) {
    throw new Error(`harness identity mismatch: ${LOCK_PATH}`);
  }
  return {
    schemaVersion: 1,
    projectRoot,
    head,
    base: BASE,
    harness: { ...HARNESS_IDENTITY, lockSha256: createHash('sha256').update(lock).digest('hex') },
  };
}

const IDENTITY_FIELDS = Object.freeze(['schemaVersion', 'projectRoot', 'head', 'base']);
const HARNESS_FIELDS = Object.freeze(['sourceCommit', 'manifestHash', 'distributionVersion', 'lockSha256']);
const identityOf = (o) => (isPlainObject(o) && isPlainObject(o.identity) ? o.identity : o ?? {});

// identity 차이 → identity-mismatch:{field} (schemaVersion, projectRoot, head, base, harness.* 순서). 순수.
export function checkIdentity(start, current) {
  const a = identityOf(start);
  const b = identityOf(current);
  const out = IDENTITY_FIELDS.filter((f) => a[f] !== b[f]).map((f) => `identity-mismatch:${f}`);
  const ha = isPlainObject(a.harness) ? a.harness : {};
  const hb = isPlainObject(b.harness) ? b.harness : {};
  for (const f of HARNESS_FIELDS) {
    if (!hasOwn(ha, f) || !hasOwn(hb, f) || ha[f] !== hb[f]) out.push(`identity-mismatch:harness.${f}`);
  }
  return out;
}

const getOr = (o, k) => (o && hasOwn(o, k) ? o[k] : null);

// 시작·현재 files 합집합 경로별 변경(경로 오름차순). hash 다르면 new|deleted|content-changed, 같고 xy 다르면 status-changed.
export function diffAgainstStart(start, current) {
  const sf = start?.files ?? {};
  const cf = current?.files ?? {};
  const sx = start?.xy ?? {};
  const cx = current?.xy ?? {};
  const out = [];
  for (const p of sortedUnique([...Object.keys(sf), ...Object.keys(cf)])) {
    const before = getOr(sf, p);
    const after = getOr(cf, p);
    const xyBefore = getOr(sx, p);
    const xyAfter = getOr(cx, p);
    let kind = null;
    if (before !== after) {
      if (before === null) kind = 'new';
      else if (after === null) kind = 'deleted';
      else kind = 'content-changed';
    } else if (xyBefore !== xyAfter) {
      kind = 'status-changed';
    }
    if (kind) out.push({ path: p, kind, xyBefore, xyAfter });
  }
  return out;
}

const isExempt = (p) => EXEMPT_PREFIXES.some((s) => p.startsWith(s)) && !GUARDED_PATHS.includes(p);

// 변경 → 판정 문자열 (allow·EXEMPT 제외, GUARDED는 면제 아님). 입력 순서 유지.
export function classifyChanges(changes, { allow = [] } = {}) {
  const allowed = new Set(allow);
  const out = [];
  for (const c of changes) {
    if (allowed.has(c.path) || isExempt(c.path)) continue;
    if (c.kind === 'status-changed') out.push(`status-changed:${c.path}`);
    else out.push(`${c.path.startsWith('tests/') ? 'tests-changed:' : 'outside-tests:'}${c.path}`);
  }
  return out;
}

// 시작에 없던 RUNTIME 경로가 현재 status에 보이면 runtime-visible (정렬)
export function checkRuntimeVisible(start, current) {
  const sx = start?.xy ?? {};
  return Object.keys(current?.xy ?? {}).sort()
    .filter((p) => RUNTIME_PREFIXES.some((s) => p.startsWith(s)) && !hasOwn(sx, p))
    .map((p) => `runtime-visible:${p}`);
}

// --require-absent 경로가 시작 기록(files·xy)에 있으면 snapshot-not-first (정렬·중복 제거)
export function checkSnapshotFirst(start, paths = []) {
  const sf = start?.files ?? {};
  const sx = start?.xy ?? {};
  return sortedUnique(paths).filter((p) => hasOwn(sf, p) || hasOwn(sx, p)).map((p) => `snapshot-not-first:${p}`);
}

// 전체 판정: snapshot-not-first → (unsafe면 정렬 unsafe만, 변경 판정 생략) → 경로 오름차순 변경 → runtime-visible
export function evaluateGate(start, current, { allow = [], requireAbsent = [] } = {}) {
  const bad = checkSnapshotFirst(start, requireAbsent);
  const unsafe = current?.unsafe ?? [];
  if (unsafe.length) return [...bad, ...sortedUnique(unsafe)];
  return [
    ...bad,
    ...classifyChanges(diffAgainstStart(start, current), { allow }),
    ...checkRuntimeVisible(start, current),
  ];
}

// ---- step 8: after.z 안전 쓰기, runCheck 실행 순서, CLI --check ----------------------------------

// after.z = snapshot 이름의 .json → -after.z. 경로 유형 검사 실패면 open 없이 UnsafePathError.
export function writeAfterZ(startFile, statusBytes, { fs = nodeFs, root = process.cwd() } = {}) {
  const after = startFile.replace(/\.json$/, '-after.z');
  const item = checkPath(after, ['missing', 'file'], { fs, root });
  if (item) throw new UnsafePathError(item);
  const { O_WRONLY, O_CREAT, O_TRUNC, O_NOFOLLOW, O_NONBLOCK } = nodeFs.constants;
  const fd = fs.openSync(path.join(root, after), O_WRONLY | O_CREAT | O_TRUNC | O_NOFOLLOW | O_NONBLOCK, 0o644);
  try {
    if (!fs.fstatSync(fd).isFile()) throw new UnsafePathError(`non-regular:${after}`);
    fs.writeFileSync(fd, Buffer.from(statusBytes));
  } finally {
    fs.closeSync(fd);
  }
  return after;
}

const errText = (e) => String(e?.message ?? e);
const isStatusArgs = (args) => args.length === STATUS_ARGS.length && args.every((a, i) => a === STATUS_ARGS[i]);

// 설계 §11.7 비교 도구 step 8 순서: checkRoot → loader → identity → takeCurrent(unsafe면 즉시 실패) →
// writeAfterZ → evaluateGate. (0)~(3) 실패는 어떤 파일도 쓰지 않는다. snapshot은 만들거나 고치지 않는다.
// deps는 테스트용 단계 대체(기본은 이 모듈의 함수).
export function runCheck({ startFile, allow = [], requireAbsent = [] } = {},
  { git, fs = nodeFs, root = process.cwd(), deps = {} } = {}) {
  const d = {
    checkRoot, loadStartSnapshot, computeIdentity, checkIdentity, takeCurrent, writeAfterZ, evaluateGate, ...deps,
  };
  const fail = (lines) => ({ code: 1, stdout: '', stderr: lines.join('\n') });
  const readGit = git ?? ((args) => runGit(args, root));
  let statusRaw = null;
  const recGit = (args) => {
    const out = readGit(args);
    if (isStatusArgs(args)) statusRaw = out;
    return out;
  };

  let start;
  let current;
  try {
    d.checkRoot({ fs, root });
    start = d.loadStartSnapshot(startFile, { fs, root });
    const ident = d.computeIdentity({ git: recGit, fs, root });
    const mismatch = d.checkIdentity(start.identity, ident);
    if (mismatch.length) {
      return fail(mismatch.map((m) => `start snapshot identity mismatch: ${m.replace(/^identity-mismatch:/, '')}`));
    }
    current = d.takeCurrent(start, { git: recGit, fs, root });
  } catch (e) {
    return fail([errText(e)]);
  }
  if (current.unsafe.length) {
    return fail([...checkSnapshotFirst(start, requireAbsent), ...sortedUnique(current.unsafe)]);
  }
  try {
    d.writeAfterZ(startFile, statusRaw ?? Buffer.alloc(0), { fs, root });
  } catch (e) {
    return fail([errText(e)]);
  }
  const bad = d.evaluateGate(start, current, { allow, requireAbsent });
  if (bad.length) return fail(bad);
  return { code: 0, stdout: 'scope-snapshot: OK', stderr: '' };
}

const USAGE = 'usage: scope-snapshot.mjs --check <start.json> --allow <list> [--require-absent <list>]';
const splitList = (s) => s.split(',').filter((p) => p !== '');

// CLI 인자 → runCheck 옵션. 알 수 없는·중복·값 없는 인자, --check·--allow 누락이면 null.
function parseCliArgs(argv) {
  const known = new Set(['--check', '--allow', '--require-absent']);
  const got = {};
  for (let i = 0; i < argv.length; i += 2) {
    const k = argv[i];
    if (!known.has(k) || hasOwn(got, k) || i + 1 >= argv.length) return null;
    got[k] = argv[i + 1];
  }
  if (!hasOwn(got, '--check') || got['--check'] === '' || !hasOwn(got, '--allow')) return null;
  return {
    startFile: got['--check'],
    allow: splitList(got['--allow']),
    requireAbsent: splitList(got['--require-absent'] ?? ''),
  };
}

function isMain() {
  if (!process.argv[1]) return false;
  try {
    return nodeFs.realpathSync(process.argv[1]) === nodeFs.realpathSync(new URL(import.meta.url));
  } catch {
    return false;
  }
}

if (isMain()) {
  const parsed = parseCliArgs(process.argv.slice(2));
  if (!parsed) {
    process.stderr.write(`${USAGE}\n`);
    process.exitCode = 2;
  } else {
    const r = runCheck(parsed, { root: process.cwd() });
    if (r.stdout) process.stdout.write(`${r.stdout}\n`);
    if (r.stderr) process.stderr.write(`${r.stderr}\n`);
    process.exitCode = r.code;
  }
}
