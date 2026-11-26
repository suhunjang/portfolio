// 합성 저장소·설계 블록·subprocess helper (설계 §11.7 테스트 격리, §12 합성 저장소 예외). 테스트 전용.
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const TESTS_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const REPO_ROOT = path.resolve(TESTS_DIR, '..');
export const DESIGN_DOC = path.join(REPO_ROOT, 'docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md');
export const SYN_BASE = path.join(REPO_ROOT, 'tests/.tmp/synthetic-repos');
const TIMEOUT = 10000;

// 부모 환경의 GIT_* 변수(GIT_DIR 등)가 합성 저장소 밖 저장소를 가리키지 않도록 제거하고,
// 전역·시스템 git 설정(서명·hook 등)의 영향을 끊는다.
export function isolatedGitEnv() {
  const env = {};
  for (const [k, v] of Object.entries(process.env)) if (!k.startsWith('GIT_')) env[k] = v;
  env.GIT_CONFIG_NOSYSTEM = '1';
  env.GIT_CONFIG_GLOBAL = '/dev/null';
  return env;
}

const COMMIT_PREFIX = ['-c', 'user.name=t', '-c', 'user.email=t@example.invalid', 'commit', '-q', '-m'];
const plainPath = (p) => typeof p === 'string' && p !== '' && !p.startsWith('-') && !p.includes(String.fromCharCode(0));

// §12가 허용하는 합성 저장소 Git 변경 명령만 통과시킨다.
function allowedGitArgs(args) {
  if (!Array.isArray(args) || !args.every((a) => typeof a === 'string')) return false;
  if (args.length === 2 && args[0] === 'init' && args[1] === '-q') return true;
  if (args.length === 2 && args[0] === 'add' && args[1] === '-A') return true;
  if (args[0] === 'add') {
    const rest = args[1] === '--' ? args.slice(2) : args.slice(1);
    return rest.length > 0 && rest.every(plainPath);
  }
  if (args.length === COMMIT_PREFIX.length + 1 && COMMIT_PREFIX.every((a, i) => args[i] === a)) {
    return typeof args[args.length - 1] === 'string' && args[args.length - 1] !== '';
  }
  return false;
}

// tests/.tmp/synthetic-repos/<pid>/ 일회용 저장소. 같은 pid의 이전 잔여물은 먼저 지운다.
export function makeSyntheticRepo() {
  const pid = String(process.pid);
  const dir = path.join(SYN_BASE, pid);
  const outside = path.join(SYN_BASE, `${pid}-outside`);
  const link = path.join(SYN_BASE, `${pid}-link`);
  const file = path.join(SYN_BASE, `${pid}-file`);
  const cleanup = () => {
    fs.rmSync(dir, { recursive: true, force: true });
    fs.rmSync(outside, { recursive: true, force: true });
    fs.rmSync(link, { force: true });
    fs.rmSync(file, { force: true });
  };
  cleanup();
  fs.mkdirSync(dir, { recursive: true });
  fs.mkdirSync(outside, { recursive: true });
  const git = (args) => {
    if (!allowedGitArgs(args)) throw new Error(`synthetic git: not allowed: ${JSON.stringify(args)}`);
    const r = spawnSync('git', ['-C', dir, ...args], { env: isolatedGitEnv(), timeout: TIMEOUT });
    if (r.error) throw r.error;
    if (r.status !== 0) throw new Error(`synthetic git ${args.join(' ')} failed: ${r.stderr}`);
    return r.stdout;
  };
  return { dir, outside, link, file, git, cleanup };
}

// 설계 블록 추출 규칙: marker로 시작하는 줄 다음 첫 fenced code block 본문 + 끝 개행 1개 (문서 읽기만)
export function designBlock(marker) {
  const lines = fs.readFileSync(DESIGN_DOC, 'utf8').split('\n');
  const i = lines.findIndex((l) => l.startsWith(marker));
  if (i < 0) throw new Error(`design marker not found: ${marker}`);
  const open = lines.findIndex((l, n) => n > i && l.startsWith('```'));
  const close = open < 0 ? -1 : lines.findIndex((l, n) => n > open && l.startsWith('```'));
  if (open < 0 || close < 0) throw new Error(`design block not found after: ${marker}`);
  return `${lines.slice(open + 1, close).join('\n')}\n`;
}

function run(cmd, args, { cwd = REPO_ROOT, input } = {}) {
  const r = spawnSync(cmd, args, { cwd, input, encoding: 'utf8', timeout: TIMEOUT });
  if (r.error) throw r.error;
  return { code: r.status, signal: r.signal, stdout: r.stdout, stderr: r.stderr };
}

export function runPython(args, opts = {}) {
  return run('python3', args, opts);
}

export function runNode(args, opts = {}) {
  return run(process.execPath, args, opts);
}

// S·C exec harness (설계 §11.7): git은 rev-parse --show-toplevel만 toplevel을 돌려주고 나머지는 기록 후 예외.
// os.lstat·os.walk·os.open·os.makedirs·builtins.open을 기록 래퍼로 감싸고 고정 본문을 그대로 exec한다.
export const EXEC_HARNESS = String.raw`
import builtins, json, os, subprocess, sys
import hashlib, re, stat
cfg = json.loads(sys.stdin.read())
calls = []
real = {'lstat': os.lstat, 'walk': os.walk, 'open': os.open, 'makedirs': os.makedirs, 'bopen': builtins.open, 'run': subprocess.run}
def rec(name, fn):
    def w(*a, **k):
        calls.append([name, [os.fsdecode(x) if isinstance(x, (str, bytes)) else repr(x) for x in a]])
        return fn(*a, **k)
    return w
def fake_run(args, *a, **k):
    args = list(args)
    if args == ['git', 'rev-parse', '--show-toplevel']:
        calls.append(['git-toplevel', args])
        return subprocess.CompletedProcess(args, 0, (cfg['top'] + '\n').encode(), b'')
    calls.append(['git-other', [str(x) for x in args]])
    raise RuntimeError('unexpected subprocess: ' + repr(args))
os.lstat = rec('os.lstat', real['lstat'])
os.walk = rec('os.walk', real['walk'])
os.open = rec('os.open', real['open'])
os.makedirs = rec('os.makedirs', real['makedirs'])
builtins.open = rec('open', real['bopen'])
subprocess.run = fake_run
sys.argv = ['-'] + cfg['argv']
result = {'exit': None, 'error': None}
try:
    exec(compile(cfg['body'], '<body>', 'exec'), {'__name__': '__main__'})
except SystemExit as e:
    result['exit'] = e.code if isinstance(e.code, (str, int)) or e.code is None else repr(e.code)
except BaseException as e:
    result['error'] = repr(e)
finally:
    os.lstat, os.walk, os.open, os.makedirs = real['lstat'], real['walk'], real['open'], real['makedirs']
    builtins.open, subprocess.run = real['bopen'], real['run']
result['calls'] = calls
sys.stdout.write(json.dumps(result))
`;

export function runHarness(body, { cwd, toplevel, argv = [] } = {}) {
  const r = runPython(['-I', '-c', EXEC_HARNESS], { cwd, input: JSON.stringify({ body, argv, top: toplevel }) });
  if (r.code !== 0) throw new Error(`exec harness failed (${r.code}): ${r.stderr}`);
  return JSON.parse(r.stdout);
}
