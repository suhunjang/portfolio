import hashlib, json, os, re, stat, subprocess, sys
RUNTIME = ('tests/node_modules/', 'tests/.npm-cache/', 'tests/.pw-browsers/', 'tests/.tmp/', 'tests/test-results/', 'tests/playwright-report/', 'tests/screenshots/')
SKIP = RUNTIME + ('.git/', '.venv/')
BASE = 'd0a8a6e462bc1366757b1401c3ba7aeb0fbf391d'
HARNESS = {'sourceCommit': 'e7a03919a460f975149f7c55343ca4b34d3d2352', 'manifestHash': 'b627e6a5ce4a903c24c400927ca2b49a14d0bd59632c691b2a5c2d74c6c08372', 'distributionVersion': '2.0.1'}
LOCK = '.harness/harness.lock.json'
KEYS = {'schemaVersion', 'stepId', 'projectRoot', 'head', 'base', 'harness', 'statusZHex', 'xy', 'files'}
HEX64 = re.compile('[0-9a-f]{64}')
STEP = sys.argv[1] if len(sys.argv) == 2 else ''
if not re.fullmatch('step[0-9]+|axe-remediation-[a-z0-9]+(-[a-z0-9]+)*|parity-[0-9]+', STEP):
    sys.exit('bad step id: ' + STEP)
OUT = 'tests/.tmp/start-snapshot-' + STEP + '.json'
def git(*args):
    return subprocess.run(['git', *args], check=True, capture_output=True).stdout
def unsafe(items):
    sys.exit('unsafe path: ' + ','.join(items))
def rel_ok(p):
    if not isinstance(p, str) or p == '' or chr(0) in p or os.path.isabs(p) or os.path.splitdrive(p)[0]:
        return False
    return all(c not in ('', '.', '..') for c in p.split('/'))
def kind(p):
    try:
        mode = os.lstat(p).st_mode
    except FileNotFoundError:
        return 'missing'
    if stat.S_ISLNK(mode):
        return 'symlink'
    if stat.S_ISDIR(mode):
        return 'dir'
    if stat.S_ISREG(mode):
        return 'file'
    return 'other'
def label(k, p):
    return {'symlink': 'symlink:', 'missing': 'missing:'}.get(k, 'non-regular:') + p
def check(p, leaf):
    parts = p.split('/')
    for i in range(1, len(parts)):
        a = '/'.join(parts[:i])
        k = kind(a)
        if k == 'missing':
            return None if 'missing' in leaf else 'missing:' + p
        if k != 'dir':
            return label(k, a)
    k = kind(p)
    return None if k in leaf else label(k, p)
def read(p):
    fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as f:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            unsafe(['non-regular:' + p])
        return f.read()
def digest(p):
    k = kind(p)
    if k == 'missing':
        return None
    if k != 'file':
        unsafe([label(k, p)])
    return hashlib.sha256(read(p)).hexdigest()
def scan():
    bad, found = [], []
    for top, dirs, names in os.walk('.'):
        rel = '' if top == '.' else top[2:] + '/'
        keep = []
        for d in dirs:
            if os.path.islink(rel + d):
                bad.append('symlink:' + rel + d)
            elif not (rel + d + '/').startswith(SKIP):
                keep.append(d)
        dirs[:] = keep
        for n in names:
            if os.path.islink(rel + n):
                bad.append('symlink:' + rel + n)
            elif (rel + n).startswith('tests/'):
                found.append(rel + n)
    return bad, found
def parse_status(raw):
    recs = raw.split(bytes(1))
    if recs and recs[-1] == b'':
        recs.pop()
    xy = {}
    i = 0
    while i < len(recs):
        rec = recs[i]
        i += 1
        if len(rec) < 4 or rec[2:3] != b' ':
            raise ValueError('bad status record')
        try:
            code = rec[:2].decode()
            p = rec[3:].decode()
        except UnicodeDecodeError:
            raise ValueError('bad status record')
        if not rel_ok(p):
            raise ValueError('bad path')
        xy[p] = code
        if code[0] in 'RC' or code[1] in 'RC':
            if i >= len(recs) or not recs[i]:
                raise ValueError('bad status record')
            try:
                o = recs[i].decode()
            except UnicodeDecodeError:
                raise ValueError('bad status record')
            if not rel_ok(o):
                raise ValueError('bad path')
            xy[o] = code
            i += 1
    return xy
def fail(what):
    sys.exit('bad start snapshot: ' + what + ': ' + OUT)
def version_ok(v):
    return type(v) is int and v == 1
def no_dup(pairs):
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError('duplicate key')
    return dict(pairs)
def no_const(name):
    raise ValueError('json constant ' + name)
top = git('rev-parse', '--show-toplevel').decode().strip()
rk = kind(top)
if rk != 'dir':
    unsafe([label(rk, top)])
root = os.path.realpath(top)
if os.path.realpath(os.getcwd()) != root:
    sys.exit('run from project root: ' + root)
bad, found = scan()
status = git('status', '--porcelain=v1', '-z', '--untracked-files=all')
try:
    xy = parse_status(status)
except ValueError:
    sys.exit('bad git status')
tracked = [p.decode() for p in git('ls-files', '-z').split(bytes(1)) if p]
targets = sorted(p for p in set(xy) | set(found) | set(tracked) if not p.startswith(SKIP))
bad += [r for r in (check(p, ('missing', 'file')) for p in targets) if r]
bad += [r for r in (check(LOCK, ('file',)), check('tests/.tmp', ('missing', 'dir')), check(OUT, ('missing', 'file'))) if r]
if bad:
    unsafe(sorted(set(bad)))
git('rev-parse', '--verify', BASE + '^{commit}')
lock = read(LOCK)
if any(v.encode() not in lock for v in HARNESS.values()):
    sys.exit('harness identity mismatch: ' + LOCK)
ident = {'schemaVersion': 1, 'stepId': STEP, 'projectRoot': root, 'head': git('rev-parse', 'HEAD').decode().strip(), 'base': BASE, 'harness': dict(HARNESS, lockSha256=hashlib.sha256(lock).hexdigest())}
if not version_ok(ident['schemaVersion']):
    fail('schemaVersion')
if kind(OUT) == 'file':
    try:
        old = json.loads(read(OUT).decode('utf-8'), object_pairs_hook=no_dup, parse_constant=no_const)
    except (OSError, ValueError):
        fail('invalid json')
    if not isinstance(old, dict) or set(old) != KEYS:
        fail('keys')
    if not version_ok(old['schemaVersion']):
        fail('schemaVersion')
    hx, oxy, ofiles = old['statusZHex'], old['xy'], old['files']
    if not isinstance(hx, str) or len(hx) % 2 or not re.fullmatch('[0-9a-f]*', hx):
        fail('statusZHex')
    try:
        parsed = parse_status(bytes.fromhex(hx))
    except ValueError as e:
        fail('paths' if str(e) == 'bad path' else 'status parse')
    if parsed != oxy:
        fail('xy')
    if not isinstance(ofiles, dict) or any(not (v is None or (isinstance(v, str) and HEX64.fullmatch(v))) for v in ofiles.values()):
        fail('files')
    if not all(rel_ok(p) for p in ofiles):
        fail('paths')
    if any(p not in ofiles for p in parsed if not p.startswith(SKIP)):
        fail('files/status')
    for k in sorted(ident):
        if old[k] != ident[k]:
            sys.exit('start snapshot identity mismatch: ' + k)
    print('start-snapshot: reused ' + OUT)
    sys.exit(0)
files = {p: digest(p) for p in targets}
os.makedirs('tests/.tmp', exist_ok=True)
fd = os.open(OUT, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
with os.fdopen(fd, 'w', encoding='utf-8') as f:
    json.dump(dict(ident, statusZHex=status.hex(), xy=xy, files=files), f, indent=1, sort_keys=True)
print('start-snapshot: created ' + OUT)
